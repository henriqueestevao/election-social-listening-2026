import json
from pathlib import Path

import pandas as pd
from ollama import Client


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed" /
    "validation_sample.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed" /
    "validation_qwen.csv"
)

MODEL = "qwen3:8b"

client = Client(host="http://localhost:11434")


SYSTEM_PROMPT = """
Você é um classificador de conteúdo político brasileiro.

Analise SOMENTE o título e a descrição fornecidos.

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

REGRAS:

- Não infira intenção de voto além do que estiver explicitamente escrito.
- Não estime resultado eleitoral.
- Não infira identidade política do autor.
- Não use conhecimento externo.
- Liste somente candidatos realmente mencionados no conteúdo.

Para cada candidato mencionado classifique:

sentiment:
positivo
negativo
neutro
misto
indeterminado

stance:
favoravel
contrario
neutro
misto
indeterminado

Sentimento é o tom em relação ao candidato.
Stance é o posicionamento explicitamente expresso.

Uma notícia negativa não significa automaticamente
stance contrário.

main_candidate deve ser o foco principal do conteúdo.
Se não houver um foco claro, use "indeterminado".

confidence indica apenas a segurança da classificação textual.
"""


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
                    "candidate": {"type": "string"},
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
        "topic": {"type": "string"},
        "narrative": {"type": "string"},
        "is_sarcasm": {"type": "boolean"},
        "is_news_report": {"type": "boolean"},
        "is_campaign_content": {"type": "boolean"},
        "confidence": {"type": "number"}
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


def classify(row):

    prompt = f"""
TÍTULO:
{row.get("title", "")}

DESCRIÇÃO:
{row.get("description", "")}

Classifique o conteúdo.
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
            "temperature": 0
        }
    )

    return json.loads(
        response["message"]["content"]
    )


def main():

    print("=" * 60)
    print("VALIDAÇÃO — QWEN3")
    print("=" * 60)

    df = pd.read_csv(INPUT_FILE)

    results = []

    for i, row in df.iterrows():

        print(
            f"\nClassificando {i + 1}/{len(df)} "
            f"| ID {row['validation_id']}"
        )

        print(
            "Título:",
            str(row["title"])[:120]
        )

        try:

            result = classify(row)

            print(
                "Principal:",
                result["main_candidate"]
            )

            for candidate in result["candidates"]:

                print(
                    "  -",
                    candidate["candidate"],
                    "|",
                    candidate["sentiment"],
                    "|",
                    candidate["stance"]
                )

            results.append({
                "qwen_main_candidate":
                    result["main_candidate"],

                "qwen_candidates_json":
                    json.dumps(
                        result["candidates"],
                        ensure_ascii=False
                    ),

                "qwen_topic":
                    result["topic"],

                "qwen_narrative":
                    result["narrative"],

                "qwen_sarcasm":
                    result["is_sarcasm"],

                "qwen_news_report":
                    result["is_news_report"],

                "qwen_campaign_content":
                    result["is_campaign_content"],

                "qwen_confidence":
                    result["confidence"],

                "qwen_error": ""
            })

        except Exception as error:

            print("ERRO:", error)

            results.append({
                "qwen_main_candidate": "ERRO",
                "qwen_candidates_json": "[]",
                "qwen_topic": "",
                "qwen_narrative": "",
                "qwen_sarcasm": False,
                "qwen_news_report": False,
                "qwen_campaign_content": False,
                "qwen_confidence": 0,
                "qwen_error": str(error)
            })


    result_df = pd.DataFrame(results)

    final = pd.concat(
        [
            df.reset_index(drop=True),
            result_df
        ],
        axis=1
    )

    final.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    errors = (
        final["qwen_main_candidate"]
        .eq("ERRO")
        .sum()
    )

    print("\n" + "=" * 60)
    print("VALIDAÇÃO FINALIZADA")
    print("=" * 60)

    print("Registros:", len(final))
    print("Erros:", errors)
    print("Arquivo:", OUTPUT_FILE)


if __name__ == "__main__":
    main()