import json
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
    "youtube_ai_test_v2.csv"
)

MODEL = "qwen3:8b"
TEST_LIMIT = 10

client = Client(host="http://localhost:11434")


# ============================================================
# CANDIDATOS VÁLIDOS
# ============================================================

VALID_CANDIDATES = [
    "Lula",
    "Flávio Bolsonaro",
    "Ronaldo Caiado",
    "Rui Costa Pimenta",
    "Samara Martins",
    "Romeu Zema",
    "Hertz Dias",
    "Edmilson Costa",
    "Renan Santos",
    "Wilson Grassi",
    "Clariana Barão",
    "Augusto Cury",
]


# ============================================================
# PROMPT
# ============================================================

SYSTEM_PROMPT = """
Você é um classificador de conteúdo político brasileiro.

Sua tarefa é descrever SOMENTE o conteúdo fornecido.

NÃO:
- infira intenção de voto;
- infira preferência eleitoral além do que está explicitamente escrito;
- estime resultado eleitoral;
- infira identidade política do autor;
- use conhecimento externo para preencher lacunas.

CANDIDATOS VÁLIDOS:

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

REGRAS:

1. Liste somente candidatos realmente mencionados no título
   ou descrição.

2. Para CADA candidato mencionado, classifique separadamente:

sentiment:
- positivo
- negativo
- neutro
- misto
- indeterminado

stance:
- favoravel
- contrario
- neutro
- misto
- indeterminado

3. SENTIMENT significa o tom do texto em relação ao candidato.

4. STANCE significa uma posição explicitamente expressa em
relação ao candidato.

5. Sentimento negativo não significa automaticamente stance
contrário.

6. Uma notícia relatando críticas contra um candidato não
significa automaticamente que o veículo seja contrário a ele.

7. Se o texto disser explicitamente que alguém declara voto
em um candidato, isso pode indicar stance favorável NO
CONTEÚDO, mas não faça inferências além dessa declaração.

8. main_candidate é o candidato que ocupa o foco principal
do conteúdo.

Se dois ou mais candidatos tiverem importância semelhante,
use "indeterminado".

9. confidence representa apenas a segurança da classificação
textual. Não representa precisão estatística.

10. Não confunda a consulta utilizada na coleta com evidência
de que aquele candidato aparece no conteúdo.
"""


# ============================================================
# SCHEMA JSON
# ============================================================

RESPONSE_SCHEMA = {
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
        },

        "topic": {
            "type": "string"
        },

        "narrative": {
            "type": "string"
        },

        "is_sarcasm": {
            "type": "boolean"
        },

        "is_news_report": {
            "type": "boolean"
        },

        "is_campaign_content": {
            "type": "boolean"
        },

        "confidence": {
            "type": "number"
        }
    },

    "required": [
        "main_candidate",
        "candidates",
        "topic",
        "narrative",
        "is_sarcasm",
        "is_news_report",
        "is_campaign_content",
        "confidence"
    ]
}


# ============================================================
# CLASSIFICADOR
# ============================================================

def classify_post(row):

    title = str(row.get("title", "") or "")
    description = str(row.get("description", "") or "")
    detected = str(
        row.get("detected_candidates", "") or ""
    )

    prompt = f"""
Detector determinístico encontrou:
{detected}

TÍTULO:
{title}

DESCRIÇÃO:
{description}

Faça a classificação do conteúdo.
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

        format=RESPONSE_SCHEMA,

        options={
            "temperature": 0
        }
    )

    return json.loads(
        response["message"]["content"]
    )


# ============================================================
# EXECUÇÃO
# ============================================================

def main():

    print("=" * 60)
    print("CLASSIFICADOR V2 — ANÁLISE POR CANDIDATO")
    print("=" * 60)

    df = pd.read_csv(INPUT_FILE)

    ambiguous = df[
        df["detection_type"].isin(
            ["none", "multiple"]
        )
    ].copy()

    print(
        f"\nCasos ambíguos disponíveis: {len(ambiguous)}"
    )

    test_df = (
        ambiguous
        .head(TEST_LIMIT)
        .copy()
        .reset_index(drop=True)
    )

    results = []

    for number, (_, row) in enumerate(
        test_df.iterrows(),
        start=1
    ):

        print("\n" + "-" * 60)
        print(f"Classificando {number}/{len(test_df)}")
        print("Título:", str(row["title"])[:150])

        try:

            result = classify_post(row)

            # Proteção contra nomes inventados pelo modelo
            result["candidates"] = [
                c for c in result["candidates"]
                if c.get("candidate") in VALID_CANDIDATES
            ]

            results.append(result)

            print(
                "Principal:",
                result["main_candidate"]
            )

            print("Candidatos:")

            for candidate in result["candidates"]:

                print(
                    "  -",
                    candidate["candidate"],
                    "| sentimento:",
                    candidate["sentiment"],
                    "| stance:",
                    candidate["stance"]
                )

            print(
                "Tema:",
                result["topic"]
            )

            print(
                "Confiança:",
                result["confidence"]
            )

        except Exception as error:

            print("ERRO:", error)

            results.append({
                "main_candidate": "ERRO",
                "candidates": [],
                "topic": "",
                "narrative": "",
                "is_sarcasm": False,
                "is_news_report": False,
                "is_campaign_content": False,
                "confidence": 0,
                "classification_error": str(error)
            })


    # ========================================================
    # TRANSFORMAR RESULTADOS PARA CSV
    # ========================================================

    flattened_results = []

    for result in results:

        flattened_results.append({

            "ai_main_candidate":
                result.get("main_candidate"),

            "ai_candidates_json":
                json.dumps(
                    result.get("candidates", []),
                    ensure_ascii=False
                ),

            "ai_topic":
                result.get("topic"),

            "ai_narrative":
                result.get("narrative"),

            "ai_sarcasm":
                result.get("is_sarcasm"),

            "ai_news_report":
                result.get("is_news_report"),

            "ai_campaign_content":
                result.get("is_campaign_content"),

            "ai_confidence":
                result.get("confidence"),

            "ai_error":
                result.get(
                    "classification_error", ""
                )
        })


    result_df = pd.DataFrame(flattened_results)

    final_df = pd.concat(
        [
            test_df.reset_index(drop=True),
            result_df
        ],
        axis=1
    )

    final_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    # ========================================================
    # RESUMO
    # ========================================================

    errors = (
        final_df["ai_main_candidate"]
        .eq("ERRO")
        .sum()
    )

    print("\n" + "=" * 60)
    print("TESTE V2 FINALIZADO")
    print("=" * 60)

    print(
        "Classificações válidas:",
        len(final_df) - errors
    )

    print("Erros:", errors)

    print(
        "Arquivo:",
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()