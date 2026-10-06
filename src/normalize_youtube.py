import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "raw"
    / "youtube_videos_setembro_outubro.json"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "youtube_posts.csv"
)


def main():

    print("Lendo arquivo bruto...")

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)


    videos = data["videos"]

    print(
        f"Vídeos encontrados: {len(videos)}"
    )


    df = pd.DataFrame(videos)


    # --------------------------------------------------------
    # PADRONIZAÇÃO
    # --------------------------------------------------------

    columns = [
        "platform",
        "video_id",
        "query",
        "title",
        "description",
        "channel_id",
        "channel_title",
        "published_at",
        "url",
        "collected_at",
        "views",
        "likes",
        "comments",
    ]

    df = df[
        [
            column
            for column in columns
            if column in df.columns
        ]
    ]


    # --------------------------------------------------------
    # TIPOS
    # --------------------------------------------------------

    df["published_at"] = pd.to_datetime(
        df["published_at"],
        errors="coerce",
        utc=True
    )

    df["collected_at"] = pd.to_datetime(
        df["collected_at"],
        errors="coerce",
        utc=True
    )


    for column in [
        "views",
        "likes",
        "comments",
    ]:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0).astype("int64")


    # --------------------------------------------------------
    # ENGAJAMENTO
    # --------------------------------------------------------

    df["engagement"] = (
        df["likes"]
        + df["comments"]
    )


    # --------------------------------------------------------
    # LIMPEZA DE TEXTO
    # --------------------------------------------------------

    df["title"] = (
        df["title"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["description"] = (
        df["description"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["channel_title"] = (
        df["channel_title"]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # DEDUPLICAÇÃO
    # --------------------------------------------------------

    antes = len(df)

    df = df.drop_duplicates(
        subset=["video_id"]
    )

    depois = len(df)

    print(
        f"Duplicatas removidas: "
        f"{antes - depois}"
    )


    # --------------------------------------------------------
    # ORDENAÇÃO
    # --------------------------------------------------------

    df = df.sort_values(
        "published_at",
        ascending=False
    )


    # --------------------------------------------------------
    # EXPORTAÇÃO
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    print()
    print("=" * 60)
    print("NORMALIZAÇÃO FINALIZADA")
    print("=" * 60)

    print(
        f"Registros: {len(df)}"
    )

    print(
        f"Colunas: {len(df.columns)}"
    )

    print(
        f"Arquivo: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()