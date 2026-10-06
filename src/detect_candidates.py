import json
import re
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "youtube_posts.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "youtube_posts_candidates.csv"
)


# ============================================================
# CANDIDATOS E ALIASES
# ============================================================

CANDIDATES = {
    "Lula": [
        "Lula",
        "Luiz Inácio Lula da Silva",
        "Luiz Inacio Lula da Silva",
    ],

    "Flávio Bolsonaro": [
        "Flávio Bolsonaro",
        "Flavio Bolsonaro",
        "flaviobolsonaro",
    ],

    "Ronaldo Caiado": [
        "Ronaldo Caiado",
        "Caiado",
    ],

    "Romeu Zema": [
        "Romeu Zema",
        "Zema",
    ],

    "Rui Costa Pimenta": [
        "Rui Costa Pimenta",
        "Rui Pimenta",
    ],

    "Samara Martins": [
        "Samara Martins",
    ],

    "Hertz Dias": [
        "Hertz Dias",
    ],

    "Edmilson Costa": [
        "Edmilson Costa",
    ],

    "Renan Santos": [
        "Renan Santos",
        "renansantos",
    ],

    "Wilson Grassi": [
        "Wilson Grassi",
        "wilsongrassi",
    ],

    "Clariana Barão": [
        "Clariana Barão",
        "Clariana Barao",
    ],

    "Augusto Cury": [
        "Augusto Cury",
        "Cury",
    ],
}


# ============================================================
# FUNÇÕES
# ============================================================

def normalize_text(text):
    if pd.isna(text):
        return ""

    return str(text).lower().strip()


def detect_candidates(text):
    """
    Procura candidatos mencionados no texto.

    Retorna uma lista com os candidatos encontrados.
    """

    text = normalize_text(text)

    detected = []

    for candidate, aliases in CANDIDATES.items():

        for alias in aliases:

            alias_normalized = normalize_text(alias)

            # Busca por palavra/frase inteira
            pattern = r"(?<!\w)" + re.escape(alias_normalized) + r"(?!\w)"

            if re.search(pattern, text):

                detected.append(candidate)

                break

    return detected


# ============================================================
# PROCESSAMENTO
# ============================================================

def main():

    print("=" * 60)
    print("DETECÇÃO INICIAL DE CANDIDATOS")
    print("=" * 60)

    print("\nLendo arquivo:")

    print(INPUT_FILE)

    df = pd.read_csv(
        INPUT_FILE
    )

    print(
        f"\nRegistros carregados: {len(df)}"
    )


    # --------------------------------------------------------
    # COMBINA TÍTULO + DESCRIÇÃO
    # --------------------------------------------------------

    df["text_for_detection"] = (
        df["title"].fillna("")
        + " "
        + df["description"].fillna("")
    )


    # --------------------------------------------------------
    # DETECTA CANDIDATOS
    # --------------------------------------------------------

    df["detected_candidates"] = (
        df["text_for_detection"]
        .apply(detect_candidates)
    )


    # --------------------------------------------------------
    # QUANTIDADE DE CANDIDATOS DETECTADOS
    # --------------------------------------------------------

    df["candidate_count"] = (
        df["detected_candidates"]
        .apply(len)
    )


    # --------------------------------------------------------
    # CANDIDATO ÚNICO
    # --------------------------------------------------------

    df["detected_candidate"] = (
        df["detected_candidates"]
        .apply(
            lambda x:
                x[0] if len(x) == 1 else ""
        )
    )


    # --------------------------------------------------------
    # CLASSIFICAÇÃO DA DETECÇÃO
    # --------------------------------------------------------

    def detection_type(candidates):

        if len(candidates) == 0:
            return "none"

        if len(candidates) == 1:
            return "single"

        return "multiple"


    df["detection_type"] = (
        df["detected_candidates"]
        .apply(detection_type)
    )


    # --------------------------------------------------------
    # REMOVE COLUNA AUXILIAR
    # --------------------------------------------------------

    df = df.drop(
        columns=["text_for_detection"]
    )


    # --------------------------------------------------------
    # EXPORTAÇÃO
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    # --------------------------------------------------------
    # RESUMO
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("DETECÇÃO FINALIZADA")
    print("=" * 60)

    print(
        f"\nTotal de vídeos: {len(df)}"
    )

    print(
        "\nNenhum candidato detectado:",
        (df["detection_type"] == "none").sum()
    )

    print(
        "Um candidato detectado:",
        (df["detection_type"] == "single").sum()
    )

    print(
        "Múltiplos candidatos detectados:",
        (df["detection_type"] == "multiple").sum()
    )


    # --------------------------------------------------------
    # CONTAGEM POR CANDIDATO
    # --------------------------------------------------------

    print("\nCANDIDATOS DETECTADOS:")

    counts = {}

    for candidates in df["detected_candidates"]:

        for candidate in candidates:

            counts[candidate] = (
                counts.get(candidate, 0) + 1
            )


    for candidate, count in sorted(
        counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        print(
            f"{candidate}: {count}"
        )


    print("\nArquivo gerado:")

    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()