from pathlib import Path
import pandas as pd


# ============================================================
# CAMINHOS
# ============================================================

BASE = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE / "data/processed/youtube_final.csv"
)

OUTPUT_FILE = (
    BASE / "data/processed/youtube_final_clean.csv"
)


# ============================================================
# CANDIDATOS OFICIAIS DO PROJETO
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
# VARIAÇÕES INEQUÍVOCAS
# ============================================================

ALIASES = {

    # Lula
    "Luiz Inácio Lula da Silva": "Lula",
    "Luiz Inacio Lula da Silva": "Lula",

    # Flávio Bolsonaro
    "Flavio Bolsonaro": "Flávio Bolsonaro",

    # Ronaldo Caiado
    "Caiado": "Ronaldo Caiado",

    # Romeu Zema
    "Zema": "Romeu Zema",

    # Rui Costa Pimenta
    "Rui Costa Piment": "Rui Costa Pimenta",
    "Rui Costa": "Rui Costa Pimenta",

    # Edmilson Costa
    "Edmilson da Costa": "Edmilson Costa",
}


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalize_candidate(value):

    if pd.isna(value):
        return "indeterminado", "missing"

    original = str(value).strip()

    # Já é candidato válido
    if original in VALID_CANDIDATES:
        return original, "valid"

    # Modelo declarou indeterminado
    if original.lower() == "indeterminado":
        return "indeterminado", "indeterminate"

    # Alias conhecido
    if original in ALIASES:
        return ALIASES[original], "alias"

    # Qualquer outro nome fica fora do escopo
    return "indeterminado", "out_of_scope"


# ============================================================
# EXECUÇÃO
# ============================================================

def main():

    print("=" * 60)
    print("NORMALIZAÇÃO DOS CANDIDATOS")
    print("=" * 60)

    df = pd.read_csv(
        INPUT_FILE,
        dtype={"video_id": str}
    )

    print(f"\nRegistros recebidos: {len(df)}")


    # --------------------------------------------------------
    # PRESERVAR VALOR ORIGINAL
    # --------------------------------------------------------

    df["candidate_original"] = df["candidate"]


    # --------------------------------------------------------
    # NORMALIZAR
    # --------------------------------------------------------

    normalized = df["candidate"].apply(
        normalize_candidate
    )

    df["candidate"] = normalized.apply(
        lambda x: x[0]
    )

    df["candidate_normalization"] = normalized.apply(
        lambda x: x[1]
    )


    # --------------------------------------------------------
    # FLAG PARA DASHBOARD
    # --------------------------------------------------------

    df["candidate_identified"] = (
        df["candidate"] != "indeterminado"
    )


    # ========================================================
    # VALIDAÇÃO
    # ========================================================

    allowed = set(
        VALID_CANDIDATES + ["indeterminado"]
    )

    invalid = df[
        ~df["candidate"].isin(allowed)
    ]


    # ========================================================
    # SALVAR
    # ========================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    # ========================================================
    # RELATÓRIO
    # ========================================================

    print("\nTipos de normalização:")

    print(
        df["candidate_normalization"]
        .value_counts(dropna=False)
    )


    print("\nCandidato FINAL:")

    print(
        df["candidate"]
        .value_counts(dropna=False)
    )


    print("\nAliases corrigidos:")

    aliases = df[
        df["candidate_normalization"] == "alias"
    ][
        [
            "candidate_original",
            "candidate"
        ]
    ]

    if len(aliases) > 0:

        print(
            aliases
            .value_counts()
            .to_string()
        )

    else:
        print("Nenhum.")


    print("\nFora do escopo:")

    outside = df[
        df["candidate_normalization"]
        == "out_of_scope"
    ][
        [
            "candidate_original",
            "title"
        ]
    ]

    if len(outside) > 0:

        print(
            outside.to_string(
                index=False
            )
        )

    else:
        print("Nenhum.")


    # ========================================================
    # CHECAGENS FINAIS
    # ========================================================

    print("\n" + "-" * 60)

    print(
        f"Registros: {len(df)}"
    )

    print(
        f"Video IDs únicos: "
        f"{df['video_id'].nunique()}"
    )

    print(
        f"Candidatos inválidos restantes: "
        f"{len(invalid)}"
    )

    print(
        f"Indeterminados: "
        f"{(df['candidate'] == 'indeterminado').sum()}"
    )

    print("-" * 60)


    if (
        len(df) == 1399
        and df["video_id"].nunique() == 1399
        and len(invalid) == 0
    ):

        print(
            "\nOK: base normalizada com integridade."
        )

    else:

        print(
            "\nATENÇÃO: revisar validações acima."
        )


    print(
        f"\nArquivo criado:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()