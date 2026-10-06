from pathlib import Path
import pandas as pd


# ============================================================
# CAMINHOS
# ============================================================

BASE = Path(__file__).resolve().parent.parent

INPUT = BASE / "data/processed/youtube_final_clean.csv"

OUTPUT_POSTS = (
    BASE / "data/processed/powerbi_youtube_posts.csv"
)

OUTPUT_SUMMARY = (
    BASE / "data/processed/powerbi_candidate_summary.csv"
)

OUTPUT_DAILY = (
    BASE / "data/processed/powerbi_daily.csv"
)


# ============================================================
# EXECUÇÃO
# ============================================================

def main():

    print("=" * 60)
    print("GERANDO DATASETS PARA POWER BI")
    print("=" * 60)

    df = pd.read_csv(
        INPUT,
        dtype={"video_id": str}
    )

    print(f"\nRegistros recebidos: {len(df)}")


    # ========================================================
    # DATAS
    # ========================================================

    df["published_at"] = pd.to_datetime(
        df["published_at"],
        errors="coerce",
        utc=True
    )

    df["date"] = (
        df["published_at"]
        .dt.tz_convert("America/Sao_Paulo")
        .dt.date
    )

    df["hour"] = (
        df["published_at"]
        .dt.tz_convert("America/Sao_Paulo")
        .dt.hour
    )


    # ========================================================
    # MÉTRICAS NUMÉRICAS
    # ========================================================

    numeric_columns = [
        "views",
        "likes",
        "comments",
        "engagement"
    ]

    for col in numeric_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)


    # ========================================================
    # GARANTIR ENGAGEMENT
    # ========================================================

    df["engagement"] = (
        df["likes"] +
        df["comments"]
    )


    # ========================================================
    # TAXAS
    # ========================================================

    df["engagement_rate"] = 0.0

    mask = df["views"] > 0

    df.loc[
        mask,
        "engagement_rate"
    ] = (

        df.loc[
            mask,
            "engagement"
        ]

        /

        df.loc[
            mask,
            "views"
        ]

    )


    # ========================================================
    # FLAGS
    # ========================================================

    df["is_identified"] = (
        df["candidate"]
        != "indeterminado"
    )

    df["is_ai_resolved"] = (
        df["candidate_resolution"]
        == "ai"
    )


    # ========================================================
    # SHARE OF OBSERVED VIDEOS
    # ========================================================

    identified_count = (
        df["is_identified"].sum()
    )

    candidate_counts = (
        df[
            df["is_identified"]
        ]
        ["candidate"]
        .value_counts()
    )

    share_map = (
        candidate_counts
        / identified_count
    )

    df["candidate_video_share"] = (
        df["candidate"]
        .map(share_map)
    )


    # ========================================================
    # TABELA 1 — POSTS
    # ========================================================

    posts_columns = [

        "video_id",
        "platform",

        "published_at",
        "date",
        "hour",

        "candidate",
        "candidate_original",
        "candidate_resolution",
        "candidate_normalization",

        "is_identified",
        "is_ai_resolved",

        "title",
        "description",

        "channel_id",
        "channel_title",

        "url",
        "query",

        "views",
        "likes",
        "comments",
        "engagement",

        "engagement_rate",

        "candidate_video_share",

        "sentiment",
        "stance",

        "ai_model"
    ]


    posts = df[
        [
            col
            for col in posts_columns
            if col in df.columns
        ]
    ].copy()


    posts.to_csv(
        OUTPUT_POSTS,
        index=False,
        encoding="utf-8-sig"
    )


    # ========================================================
    # BASE IDENTIFICADA
    # ========================================================

    identified = df[
        df["is_identified"]
    ].copy()


    # ========================================================
    # TABELA 2 — RESUMO POR CANDIDATO
    # ========================================================

    summary = (

        identified

        .groupby(
            "candidate",
            as_index=False
        )

        .agg(

            videos=(
                "video_id",
                "nunique"
            ),

            channels=(
                "channel_id",
                "nunique"
            ),

            views=(
                "views",
                "sum"
            ),

            likes=(
                "likes",
                "sum"
            ),

            comments=(
                "comments",
                "sum"
            ),

            engagement=(
                "engagement",
                "sum"
            ),

            median_views=(
                "views",
                "median"
            ),

            median_engagement=(
                "engagement",
                "median"
            )
        )
    )


    # ========================================================
    # PARTICIPAÇÃO NO CONJUNTO OBSERVADO
    # ========================================================

    total_videos = summary["videos"].sum()

    total_views = summary["views"].sum()

    total_engagement = (
        summary["engagement"].sum()
    )


    summary["video_share"] = (
        summary["videos"]
        / total_videos
        if total_videos > 0
        else 0
    )


    summary["view_share"] = (
        summary["views"]
        / total_views
        if total_views > 0
        else 0
    )


    summary["engagement_share"] = (
        summary["engagement"]
        / total_engagement
        if total_engagement > 0
        else 0
    )


    # ========================================================
    # TAXA AGREGADA
    # ========================================================

    summary["engagement_rate"] = 0.0

    mask = summary["views"] > 0

    summary.loc[
        mask,
        "engagement_rate"
    ] = (

        summary.loc[
            mask,
            "engagement"
        ]

        /

        summary.loc[
            mask,
            "views"
        ]

    )


    summary.to_csv(
        OUTPUT_SUMMARY,
        index=False,
        encoding="utf-8-sig"
    )


    # ========================================================
    # TABELA 3 — CANDIDATO POR DIA
    # ========================================================

    daily = (

        identified

        .groupby(
            [
                "date",
                "candidate"
            ],
            as_index=False
        )

        .agg(

            videos=(
                "video_id",
                "nunique"
            ),

            channels=(
                "channel_id",
                "nunique"
            ),

            views=(
                "views",
                "sum"
            ),

            likes=(
                "likes",
                "sum"
            ),

            comments=(
                "comments",
                "sum"
            ),

            engagement=(
                "engagement",
                "sum"
            )
        )
    )


    daily.to_csv(
        OUTPUT_DAILY,
        index=False,
        encoding="utf-8-sig"
    )


    # ========================================================
    # VALIDAÇÕES
    # ========================================================

    print("\n" + "=" * 60)
    print("VALIDAÇÃO")
    print("=" * 60)


    print(
        f"\nPosts: {len(posts)}"
    )

    print(
        f"IDs únicos: "
        f"{posts['video_id'].nunique()}"
    )

    print(
        f"Identificados: "
        f"{identified_count}"
    )

    print(
        f"Indeterminados: "
        f"{(~df['is_identified']).sum()}"
    )


    print(
        "\nPeríodo:"
    )

    print(
        df["date"].min(),
        "até",
        df["date"].max()
    )


    print(
        "\nTotais observados:"
    )

    print(
        f"Views: "
        f"{int(df['views'].sum()):,}"
    )

    print(
        f"Likes: "
        f"{int(df['likes'].sum()):,}"
    )

    print(
        f"Comentários: "
        f"{int(df['comments'].sum()):,}"
    )

    print(
        f"Engajamento: "
        f"{int(df['engagement'].sum()):,}"
    )


    print(
        "\nResumo por candidato:"
    )

    print(
        summary[
            [
                "candidate",
                "videos",
                "views",
                "engagement",
                "video_share"
            ]
        ].to_string(
            index=False
        )
    )


    # ========================================================
    # CHECAGEM
    # ========================================================

    if (
        len(posts) == 1399
        and posts["video_id"].nunique() == 1399
    ):

        print(
            "\nOK: datasets gerados com integridade."
        )

    else:

        print(
            "\nATENÇÃO: verificar quantidade de registros."
        )


    print("\nArquivos criados:")

    print(OUTPUT_POSTS)
    print(OUTPUT_SUMMARY)
    print(OUTPUT_DAILY)


if __name__ == "__main__":
    main()