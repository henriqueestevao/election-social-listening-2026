import json
import os
import time
from pathlib import Path

import pandas as pd
from ollama import Client


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE = Path(__file__).resolve().parent.parent

INPUT = (
    BASE
    / "data"
    / "processed"
    / "youtube_final_clean.csv"
)

OUTPUT = (
    BASE
    / "data"
    / "processed"
    / "youtube_sentiment_all.csv"
)

MODEL = "qwen3:4b-instruct"

client = Client(
    host="http://localhost:11434"
)


# ============================================================
# SCHEMA
# ============================================================

SCHEMA = {
    "type": "object",

    "properties": {

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
        "sentiment",
        "stance"
    ]
}


# ============================================================
# PROMPT
# ============================================================

SYSTEM_PROMPT = """
Você classifica o tom de conteúdos políticos.

O candidato-alvo já foi identificado anteriormente.

Analise SOMENTE o título e a descrição fornecidos.

Não identifique outro candidato.
Não estime intenção de voto.
Não estime resultado eleitoral.
Não infira identidade política do autor.
Não use conhecimento externo.

SENTIMENT representa o tom do conteúdo em relação
ao candidato-alvo.

Valores possíveis:

positivo
negativo
neutro
misto
indeterminado

STANCE representa o posicionamento explicitamente
expresso em relação ao candidato-alvo.

Valores possíveis:

favoravel
contrario
neutro
misto
indeterminado

Uma notícia sobre pesquisa eleitoral não é
automaticamente positiva ou negativa.

Uma notícia relatando críticas não significa
automaticamente que o autor do vídeo concorda
com a crítica.

Quando não houver evidência suficiente,
use indeterminado.
"""


# ============================================================
# CLASSIFICADOR
# ============================================================

def classify(row):

    candidate = str(
        row.get("candidate", "")
    )

    title = str(
        row.get("title", "") or ""
    )

    description = str(
        row.get("description", "") or ""
    )

    prompt = f"""
CANDIDATO-ALVO:
{candidate}

TÍTULO:
{title}

DESCRIÇÃO:
{description}

Classifique sentiment e stance em relação
ao candidato-alvo.
"""

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
            "num_predict": 100,
            "num_ctx": 1536
        }
    )

    return json.loads(
        response["message"]["content"]
    )


# ============================================================
# SALVAMENTO SEGURO
# ============================================================

def save(df):

    temp = OUTPUT.with_suffix(".tmp")

    df.to_csv(
        temp,
        index=False,
        encoding="utf-8-sig"
    )

    os.replace(
        temp,
        OUTPUT
    )


# ============================================================
# EXECUÇÃO
# ============================================================

def main():

    print("=" * 60)
    print("SENTIMENTO + STANCE — TODOS OS VÍDEOS")
    print("=" * 60)

    df = pd.read_csv(
        INPUT,
        dtype={"video_id": str}
    )

    print(
        f"\nBase: {len(df)} vídeos"
    )


    # ========================================================
    # CARREGAR RESULTADOS EXISTENTES
    # ========================================================

    if OUTPUT.exists():

        existing = pd.read_csv(
            OUTPUT,
            dtype={"video_id": str}
        )

        # Mantemos somente classificações válidas.
        valid = existing[
            existing["sentiment_all"]
            .notna()
            &
            existing["sentiment_all"]
            .ne("ERRO")
        ].copy()

        valid = valid.drop_duplicates(
            subset=["video_id"],
            keep="last"
        )

        processed = set(
            valid["video_id"]
            .astype(str)
        )

        results = valid.to_dict(
            orient="records"
        )

    else:

        processed = set()
        results = []


    total = len(df)

    print(
        f"Já processados: {len(processed)}"
    )

    print(
        f"Restantes: {total - len(processed)}"
    )

    print(
        f"Modelo: {MODEL}"
    )


    # ========================================================
    # PROCESSAMENTO
    # ========================================================

    durations = []

    errors = 0


    for index, row in df.iterrows():

        video_id = str(
            row["video_id"]
        )


        if video_id in processed:
            continue


        print("\n" + "-" * 60)

        print(
            f"Processando {len(processed) + 1}/{total}"
        )

        print(
            "Candidato:",
            row.get("candidate")
        )

        print(
            "Título:",
            str(
                row.get("title", "")
            )[:100]
        )


        start = time.perf_counter()


        try:

            result = classify(row)

            output = row.to_dict()

            output.update({

                "sentiment_all":
                    result["sentiment"],

                "stance_all":
                    result["stance"],

                "sentiment_model":
                    MODEL,

                "sentiment_error":
                    ""
            })


            results.append(
                output
            )

            processed.add(
                video_id
            )


            # --------------------------------------------
            # SALVAR APÓS CADA REGISTRO
            # --------------------------------------------

            result_df = pd.DataFrame(
                results
            )

            save(
                result_df
            )


            elapsed = (
                time.perf_counter()
                - start
            )

            durations.append(
                elapsed
            )


            average = (
                sum(durations)
                / len(durations)
            )

            remaining = (
                total
                - len(processed)
            )

            eta_minutes = (
                remaining
                * average
                / 60
            )


            print(
                "Sentimento:",
                result["sentiment"]
            )

            print(
                "Stance:",
                result["stance"]
            )

            print(
                f"Tempo: {elapsed:.1f}s"
            )

            print(
                f"Média da sessão: "
                f"{average:.1f}s/post"
            )

            print(
                f"Restantes: {remaining}"
            )

            print(
                f"ETA aproximado: "
                f"{eta_minutes:.0f} min"
            )


        except KeyboardInterrupt:

            print(
                "\nInterrompido pelo usuário."
            )

            print(
                "Resultados já processados "
                "foram preservados."
            )

            break


        except Exception as error:

            errors += 1

            print(
                "ERRO:",
                error
            )

            # Não marca como processado.
            # Na próxima execução será tentado novamente.

            if errors >= 5:

                print(
                    "\n5 erros nesta execução."
                )

                print(
                    "Interrompendo para diagnóstico."
                )

                break


    # ========================================================
    # RESUMO
    # ========================================================

    print("\n" + "=" * 60)
    print("RESUMO")
    print("=" * 60)

    print(
        f"Processados: {len(processed)}/{total}"
    )

    print(
        f"Restantes: {total - len(processed)}"
    )

    print(
        f"Erros nesta execução: {errors}"
    )

    print(
        f"\nArquivo:\n{OUTPUT}"
    )


if __name__ == "__main__":
    main()