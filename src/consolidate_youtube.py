import json
from pathlib import Path

import pandas as pd


# ============================================================
# CAMINHOS
# ============================================================

BASE = Path(__file__).resolve().parent.parent

POSTS_FILE = (
    BASE / "data/processed/youtube_posts_candidates.csv"
)

AI_FILE = (
    BASE / "data/processed/youtube_ai_ambiguous.csv"
)

OUTPUT_FILE = (
    BASE / "data/processed/youtube_final.csv"
)


# ============================================================
# FUNÇÕES
# ============================================================

def parse_ai_candidates(value):
    """
    Converte ai_candidates_json para lista Python.
    """

    if pd.isna(value):
        return []

    try:
        result = json.loads(value)

        if isinstance(result, list):
            return result

        return []

    except Exception:
        return []


def main():

    print("=" * 60)
    print("CONSOLIDAÇÃO YOUTUBE")
    print("=" * 60)

    # ========================================================
    # CARREGAR DADOS
    # ========================================================

    posts = pd.read_csv(
        POSTS_FILE,
        dtype={"video_id": str}
    )

    ai = pd.read_csv(
        AI_FILE,
        dtype={"video_id": str}
    )

    print(f"\nPosts originais: {len(posts)}")
    print(f"Casos classificados por IA: {len(ai)}")


    # ========================================================
    # GARANTIR UNICIDADE
    # ========================================================

    posts = posts.drop_duplicates(
        subset=["video_id"],
        keep="last"
    )

    ai = ai.drop_duplicates(
        subset=["video_id"],
        keep="last"
    )


    # ========================================================
    # CRIAR MAPA DA IA
    # ========================================================

    ai_map = ai.set_index("video_id").to_dict(
        orient="index"
    )


    # ========================================================
    # CONSOLIDAR
    # ========================================================

    results = []

    for _, row in posts.iterrows():

        video_id = str(row["video_id"])

        detection_type = str(
            row.get("detection_type", "")
        )

        final_candidate = None
        resolution = None
        ai_model = None

        sentiment = None
        stance = None

        candidates_json = None


        # ====================================================
        # CASO 1 — DETERMINÍSTICO
        # ====================================================

        if detection_type == "single":

            final_candidate = row.get(
                "detected_candidate"
            )

            resolution = "deterministic"


        # ====================================================
        # CASO 2 — IA
        # ====================================================

        elif detection_type in ["none", "multiple"]:

            ai_row = ai_map.get(video_id)

            if ai_row is not None:

                final_candidate = ai_row.get(
                    "ai_main_candidate"
                )

                ai_model = ai_row.get(
                    "ai_model"
                )

                resolution = "ai"

                candidates = parse_ai_candidates(
                    ai_row.get(
                        "ai_candidates_json"
                    )
                )

                candidates_json = json.dumps(
                    candidates,
                    ensure_ascii=False
                )


                # ============================================
                # SENTIMENTO / STANCE DO CANDIDATO PRINCIPAL
                # ============================================

                for candidate_data in candidates:

                    candidate_name = candidate_data.get(
                        "candidate"
                    )

                    if (
                        candidate_name
                        == final_candidate
                    ):

                        sentiment = (
                            candidate_data.get(
                                "sentiment"
                            )
                        )

                        stance = (
                            candidate_data.get(
                                "stance"
                            )
                        )

                        break

            else:

                resolution = "unresolved"


        # ====================================================
        # CRIAR LINHA FINAL
        # ====================================================

        output = {

            "platform":
                row.get("platform"),

            "video_id":
                video_id,

            "published_at":
                row.get("published_at"),

            "title":
                row.get("title"),

            "description":
                row.get("description"),

            "channel_id":
                row.get("channel_id"),

            "channel_title":
                row.get("channel_title"),

            "url":
                row.get("url"),

            "query":
                row.get("query"),

            "views":
                row.get("views"),

            "likes":
                row.get("likes"),

            "comments":
                row.get("comments"),

            "engagement":
                row.get("engagement"),

            # --------------------------------------------
            # DETECÇÃO ORIGINAL
            # --------------------------------------------

            "detection_type":
                detection_type,

            "detected_candidates":
                row.get(
                    "detected_candidates"
                ),

            # --------------------------------------------
            # RESULTADO CONSOLIDADO
            # --------------------------------------------

            "candidate":
                final_candidate,

            "candidate_resolution":
                resolution,

            # --------------------------------------------
            # IA
            # --------------------------------------------

            "ai_model":
                ai_model,

            "sentiment":
                sentiment,

            "stance":
                stance,

            "ai_candidates_json":
                candidates_json
        }

        results.append(output)


    # ========================================================
    # DATAFRAME FINAL
    # ========================================================

    final = pd.DataFrame(results)


    # ========================================================
    # LIMPEZA
    # ========================================================

    final["candidate"] = (
        final["candidate"]
        .replace(
            {
                "": pd.NA,
                "nan": pd.NA,
                "None": pd.NA
            }
        )
    )


    # ========================================================
    # SALVAR
    # ========================================================

    final.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    # ========================================================
    # VALIDAÇÕES
    # ========================================================

    print("\n" + "=" * 60)
    print("CONSOLIDAÇÃO FINALIZADA")
    print("=" * 60)

    print(
        f"\nRegistros finais: {len(final)}"
    )

    print(
        f"Video IDs únicos: "
        f"{final['video_id'].nunique()}"
    )


    print("\nResolução:")

    print(
        final[
            "candidate_resolution"
        ].value_counts(
            dropna=False
        )
    )


    print("\nCandidato principal:")

    print(
        final[
            "candidate"
        ].value_counts(
            dropna=False
        )
    )


    print("\nModelos IA:")

    print(
        final[
            "ai_model"
        ].value_counts(
            dropna=False
        )
    )


    # ========================================================
    # CHECAGENS
    # ========================================================

    duplicates = final[
        "video_id"
    ].duplicated().sum()

    unresolved = (
        final[
            "candidate_resolution"
        ]
        .eq("unresolved")
        .sum()
    )

    errors = (
        final["candidate"]
        .astype(str)
        .eq("ERRO")
        .sum()
    )


    print("\n" + "-" * 60)

    print(
        f"Duplicados: {duplicates}"
    )

    print(
        f"Não resolvidos: {unresolved}"
    )

    print(
        f"ERRO como candidato: {errors}"
    )

    print("-" * 60)


    # ========================================================
    # TESTE DE INTEGRIDADE
    # ========================================================

    if len(final) != len(posts):

        print(
            "\nATENÇÃO: quantidade final diferente "
            "da quantidade original!"
        )

    elif duplicates > 0:

        print(
            "\nATENÇÃO: existem video_ids duplicados!"
        )

    else:

        print(
            "\nOK: integridade básica da base confirmada."
        )


    print(
        f"\nArquivo criado:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()