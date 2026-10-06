import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed" /
    "validation_qwen.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed" /
    "validation_review.csv"
)


def main():

    print("=" * 60)
    print("PREPARANDO REVISÃO HUMANA")
    print("=" * 60)

    df = pd.read_csv(INPUT_FILE)

    rows = []

    for _, row in df.iterrows():

        try:
            candidates = json.loads(
                row["qwen_candidates_json"]
            )
        except Exception:
            candidates = []

        # Caso o Qwen não tenha encontrado candidato
        if not candidates:

            rows.append({
                "validation_id": row["validation_id"],
                "title": row["title"],
                "description": row["description"],

                "qwen_main_candidate":
                    row["qwen_main_candidate"],

                "candidate": "nenhum",

                "qwen_sentiment":
                    "indeterminado",

                "qwen_stance":
                    "indeterminado",

                "qwen_topic":
                    row["qwen_topic"],

                "qwen_confidence":
                    row["qwen_confidence"],

                "human_candidate_correct": "",
                "human_sentiment": "",
                "human_stance": "",
                "human_main_correct": "",
                "human_notes": ""
            })

            continue

        # Uma linha para cada candidato
        for candidate in candidates:

            rows.append({
                "validation_id":
                    row["validation_id"],

                "title":
                    row["title"],

                "description":
                    row["description"],

                "qwen_main_candidate":
                    row["qwen_main_candidate"],

                "candidate":
                    candidate.get("candidate", ""),

                "qwen_sentiment":
                    candidate.get("sentiment", ""),

                "qwen_stance":
                    candidate.get("stance", ""),

                "qwen_topic":
                    row["qwen_topic"],

                "qwen_confidence":
                    row["qwen_confidence"],

                # CAMPOS PARA VOCÊ PREENCHER
                "human_candidate_correct": "",
                "human_sentiment": "",
                "human_stance": "",
                "human_main_correct": "",
                "human_notes": ""
            })

    review = pd.DataFrame(rows)

    review.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print()
    print("Posts originais:", len(df))
    print("Linhas para revisão:", len(review))

    print()
    print("Arquivo:")
    print(OUTPUT_FILE)

    print()
    print("Arquivo de revisão criado com sucesso.")


if __name__ == "__main__":
    main()