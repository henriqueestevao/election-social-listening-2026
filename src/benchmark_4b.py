import json
import time
from pathlib import Path

import pandas as pd
from ollama import Client


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed" /
    "youtube_ai_ambiguous.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed" /
    "benchmark_qwen4b.csv"
)

MODEL = "qwen3:4b-instruct"
TEST_LIMIT = 10

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

Não infira intenção de voto, resultado eleitoral,
identidade política ou informações ausentes.

Para cada candidato realmente mencionado, classifique:

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

Sentimento é o tom do conteúdo em relação ao candidato.
Stance é o posicionamento explicitamente expresso.

Uma notícia negativa não implica automaticamente
stance contrário.

main_candidate é o foco principal.
Se não houver foco claro, use "indeterminado".
"""


SCHEMA = {
    "type": "object",
    "properties": {

        "main_candidate": {"type": "string"},

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
        }
    },

    "required": [
        "main_candidate",
        "candidates"
    ]
}


def classify(row):

    prompt = f"""
TÍTULO:
{row.get("title", "")}

DESCRIÇÃO:
{row.get("description", "")}

Classifique.
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
            "temperature": 0
        }
    )

    elapsed = time.perf_counter() - start

    result = json.loads(
        response["message"]["content"]
    )

    return result, elapsed


def main():

    print("=" * 60)
    print("BENCHMARK QWEN3 4B")
    print("=" * 60)

    df = pd.read_csv(INPUT_FILE)

    # Só resultados válidos do 8B
    df = df[
        df["ai_main_candidate"] != "ERRO"
    ].head(TEST_LIMIT).copy()

    results = []

    total_start = time.perf_counter()

    for i, row in df.iterrows():

        number = len(results) + 1

        print("\n" + "-" * 60)
        print(f"Teste {number}/{len(df)}")
        print("Título:", str(row["title"])[:100])

        try:

            result, elapsed = classify(row)

            print(
                f"Tempo: {elapsed:.1f} segundos"
            )

            print(
                "8B principal:",
                row["ai_main_candidate"]
            )

            print(
                "4B principal:",
                result["main_candidate"]
            )

            results.append({

                "video_id":
                    row["video_id"],

                "title":
                    row["title"],

                "8b_main_candidate":
                    row["ai_main_candidate"],

                "8b_candidates_json":
                    row["ai_candidates_json"],

                "4b_main_candidate":
                    result["main_candidate"],

                "4b_candidates_json":
                    json.dumps(
                        result["candidates"],
                        ensure_ascii=False
                    ),

                "seconds":
                    round(elapsed, 2),

                "main_agreement":
                    str(row["ai_main_candidate"]).strip()
                    == str(result["main_candidate"]).strip()
            })

        except Exception as error:

            print("ERRO:", error)


    total = time.perf_counter() - total_start

    result_df = pd.DataFrame(results)

    result_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("BENCHMARK FINALIZADO")
    print("=" * 60)

    print(
        f"Tempo total: {total / 60:.1f} minutos"
    )

    if len(result_df):

        print(
            f"Tempo médio: "
            f"{result_df['seconds'].mean():.1f} segundos/post"
        )

        agreement = (
            result_df["main_agreement"].mean() * 100
        )

        print(
            f"Concordância candidato principal: "
            f"{agreement:.1f}%"
        )

    print("\nArquivo:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()