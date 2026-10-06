import json
import time
from pathlib import Path

import pandas as pd
from ollama import Client


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed" /
    "youtube_posts_candidates.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed" /
    "youtube_ai_ambiguous.csv"
)

MODEL = "qwen3:4b-instruct"

client = Client(host="http://localhost:11434")


# ============================================================
# PROMPT CURTO
# ============================================================

SYSTEM_PROMPT = """
Classifique somente o texto fornecido.

Candidatos válidos:
Lula
Flávio Bolsonaro
Ronaldo Caiado
Rui Costa Pimenta
Samara Martins
Romeu Zema
Hertz Dias
Edmilson Costa
Renan Santos
Wilson Grassi
Clariana Barão
Augusto Cury

Liste somente candidatos realmente mencionados.

Para cada candidato:

sentiment:
positivo, negativo, neutro, misto ou indeterminado

stance:
favoravel, contrario, neutro, misto ou indeterminado

Sentiment = tom do conteúdo sobre o candidato.
Stance = posicionamento explicitamente expresso.

Não infira intenção de voto, identidade política
ou resultado eleitoral.

main_candidate = foco principal do texto.
Se não houver foco claro, use "indeterminado".
"""


# ============================================================
# JSON MÍNIMO
# ============================================================

SCHEMA = {
    "type": "object",
    "properties": {

        "main_candidate": {
            "type": "string"
        },

        "candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {

                    "candidate": {
                        "type": "string"
                    },

                    "sentiment": {
                        "type": "string",
                        "enum": [
                            "positivo",
                            "negativo",
                            "neutro",
                            "misto",
                            "indeterminado"
                        ]
                    },

                    "stance": {
                        "type": "string",
                        "enum": [
                            "favoravel",
                            "contrario",
                            "neutro",
                            "misto",
                            "indeterminado"
                        ]
                    }
                },

                "required": [
                    "candidate",
                    "sentiment",
                    "stance"
                ]
            }
        }
    },

    "required": [
        "main_candidate",
        "candidates"
    ]
}


# ============================================================
# CLASSIFICAR
# ============================================================

def classify(row):

    # Limitamos descrição para evitar mandar textos enormes.
    title = str(row.get("title", "") or "")
    description = str(row.get("description", "") or "")

    description = description[:1200]

    prompt = f"""
TÍTULO:
{title}

DESCRIÇÃO:
{description}
"""

    start = time.perf_counter()

    response = client.chat(
        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        format=SCHEMA,

        options={
            "temperature": 0,
            "num_predict": 180
        }
    )

    elapsed = time.perf_counter() - start

    result = json.loads(
        response["message"]["content"]
    )

    return result, elapsed


# ============================================================
# EXECUÇÃO
# ============================================================

def main():

    print("=" * 60)
    print("CLASSIFICADOR RÁPIDO — QWEN3 4B")
    print("=" * 60)

    df = pd.read_csv(INPUT_FILE)

    ambiguous = df[
        df["detection_type"].isin(
            ["none", "multiple"]
        )
    ].copy()

    ambiguous = ambiguous.reset_index(drop=True)

    total = len(ambiguous)

    print(f"\nCasos ambíguos: {total}")


    # ========================================================
    # RECUPERAR CHECKPOINT
    # ========================================================

    if OUTPUT_FILE.exists():

        existing = pd.read_csv(OUTPUT_FILE)

        if "ai_model" not in existing.columns:
            existing["ai_model"] = "qwen3:8b"

        existing["ai_model"] = (
            existing["ai_model"]
            .fillna("qwen3:8b")
        )

        processed_ids = set(
            existing["video_id"]
            .astype(str)
        )

        results = existing.to_dict(
            orient="records"
        )

    else:

        processed_ids = set()
        results = []


    already_done = len(processed_ids)

    print(f"Já processados: {already_done}")
    print(f"Restantes: {total - already_done}")
    print(f"Modelo: {MODEL}")


    # ========================================================
    # TEMPOS DA SESSÃO ATUAL
    # ========================================================

    session_times = []


    # ========================================================
    # PROCESSAR
    # ========================================================

    for index, row in ambiguous.iterrows():

        video_id = str(row["video_id"])

        if video_id in processed_ids:
            continue


        completed_before = len(processed_ids)

        print("\n" + "-" * 60)

        print(
            f"Processando "
            f"{completed_before + 1}/{total}"
        )

        print(
            "Título:",
            str(row["title"])[:100]
        )


        try:

            result, elapsed = classify(row)

            session_times.append(elapsed)

            output_row = row.to_dict()

            output_row.update({

                "ai_main_candidate":
                    result["main_candidate"],

                "ai_candidates_json":
                    json.dumps(
                        result["candidates"],
                        ensure_ascii=False
                    ),

                # Campos antigos permanecem
                # vazios nos novos registros.
                "ai_topic":
                    "",

                "ai_narrative":
                    "",

                "ai_sarcasm":
                    False,

                "ai_news_report":
                    False,

                "ai_campaign_content":
                    False,

                # Não estamos mais pedindo ao
                # modelo uma confiança subjetiva.
                "ai_confidence":
                    None,

                "ai_model":
                    MODEL,

                "ai_error":
                    ""
            })


            print(
                "Principal:",
                result["main_candidate"]
            )

            print(
                f"Tempo: {elapsed:.1f}s"
            )


        except Exception as error:

            print("ERRO:", error)

            output_row = row.to_dict()

            output_row.update({

                "ai_main_candidate":
                    "ERRO",

                "ai_candidates_json":
                    "[]",

                "ai_topic":
                    "",

                "ai_narrative":
                    "",

                "ai_sarcasm":
                    False,

                "ai_news_report":
                    False,

                "ai_campaign_content":
                    False,

                "ai_confidence":
                    None,

                "ai_model":
                    MODEL,

                "ai_error":
                    str(error)
            })


        # ====================================================
        # CHECKPOINT
        # ====================================================

        results.append(output_row)

        pd.DataFrame(results).to_csv(
            OUTPUT_FILE,
            index=False,
            encoding="utf-8-sig"
        )

        processed_ids.add(video_id)


        # ====================================================
        # ETA
        # ====================================================

        if session_times:

            avg = sum(session_times) / len(session_times)

            remaining = (
                total - len(processed_ids)
            )

            eta_seconds = avg * remaining
            eta_minutes = eta_seconds / 60

            print(
                f"Média da sessão: {avg:.1f}s/post"
            )

            print(
                f"Restantes: {remaining}"
            )

            if eta_minutes < 60:

                print(
                    f"ETA aproximado: "
                    f"{eta_minutes:.0f} min"
                )

            else:

                print(
                    f"ETA aproximado: "
                    f"{eta_minutes / 60:.1f} h"
                )


    # ========================================================
    # FINAL
    # ========================================================

    final = pd.read_csv(OUTPUT_FILE)

    errors = (
        final["ai_main_candidate"]
        .eq("ERRO")
        .sum()
    )

    print("\n" + "=" * 60)
    print("CLASSIFICAÇÃO FINALIZADA")
    print("=" * 60)

    print("Processados:", len(final))
    print("Erros:", errors)

    print("\nModelos utilizados:")

    print(
        final["ai_model"]
        .value_counts(dropna=False)
    )

    print("\nArquivo:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()