from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed" /
    "youtube_posts_candidates.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed" /
    "validation_sample.csv"
)

SAMPLE_SIZE = 30
RANDOM_STATE = 42


def main():

    print("=" * 60)
    print("CRIANDO AMOSTRA DE VALIDAÇÃO")
    print("=" * 60)

    df = pd.read_csv(INPUT_FILE)

    ambiguous = df[
        df["detection_type"].isin(["none", "multiple"])
    ].copy()

    print(f"\nCasos ambíguos disponíveis: {len(ambiguous)}")

    # Divide a amostra entre os dois tipos
    none_df = ambiguous[
        ambiguous["detection_type"] == "none"
    ]

    multiple_df = ambiguous[
        ambiguous["detection_type"] == "multiple"
    ]

    # 15 de cada grupo
    sample_none = none_df.sample(
        n=min(15, len(none_df)),
        random_state=RANDOM_STATE
    )

    sample_multiple = multiple_df.sample(
        n=min(15, len(multiple_df)),
        random_state=RANDOM_STATE
    )

    sample = pd.concat(
        [sample_none, sample_multiple],
        ignore_index=True
    )

    # Embaralha a ordem final
    sample = sample.sample(
        frac=1,
        random_state=RANDOM_STATE
    ).reset_index(drop=True)

    # ID simples para nossa auditoria
    sample.insert(
        0,
        "validation_id",
        range(1, len(sample) + 1)
    )

    # Campos que preencheremos manualmente
    sample["human_main_candidate"] = ""
    sample["human_candidates"] = ""
    sample["human_sentiment"] = ""
    sample["human_stance"] = ""
    sample["human_topic"] = ""
    sample["human_notes"] = ""

    sample.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nDistribuição:")
    print(sample["detection_type"].value_counts())

    print(f"\nRegistros selecionados: {len(sample)}")
    print(f"Arquivo: {OUTPUT_FILE}")

    print("\nAmostra criada com sucesso.")


if __name__ == "__main__":
    main()