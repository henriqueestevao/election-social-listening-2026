import json
import time
from pathlib import Path

import pandas as pd
from ollama import Client


BASE = Path(__file__).resolve().parent.parent

FILE = BASE / "data/processed/youtube_ai_ambiguous.csv"

MODEL = "qwen3:4b-instruct"

client = Client(host="http://localhost:11434")


CANDIDATES = [
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
    "Augusto Cury"
]


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

                    "candidate": {
                        "type": "string",
                        "enum": CANDIDATES
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
        }
    },

    "required": [
        "main_candidate",
        "candidates"
    ]
}


SYSTEM_PROMPT = """
Classifique o conteúdo político fornecido.

Use SOMENTE o título e a descrição.

Não use conhecimento externo.
Não estime resultados eleitorais.
Não infira intenção de voto.
Não infira identidade política do autor.

Identifique somente candidatos explicitamente mencionados.

main_candidate:
candidato que é o foco principal.

Se não houver foco principal claro:
"indeterminado"

Para cada candidato:

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

Retorne somente a estrutura solicitada.
"""


def classify(row):

    title = str(row.get("title", "") or "")
    description = str(row.get("description", "") or "")

    response = client.chat(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content":
                    f"TÍTULO:\n{title}\n\n"
                    f"DESCRIÇÃO:\n{description}"
            }
        ],

        format=SCHEMA,

        options={
            "temperature": 0,

            # Mais espaço para terminar o JSON
            "num_predict": 800,

            "num_ctx": 2048
        }
    )

    return json.loads(
        response["message"]["content"]
    )


def main():

    df = pd.read_csv(
        FILE,
        dtype={"video_id": str}
    )

    error_mask = (
        df["ai_main_candidate"]
        .astype(str)
        .eq("ERRO")
    )

    error_indexes = df.index[error_mask].tolist()

    print("=" * 55)
    print("REPROCESSAMENTO DOS ERROS")
    print("=" * 55)

    print(
        f"Erros encontrados: {len(error_indexes)}"
    )

    fixed = 0
    failed = 0


    for number, idx in enumerate(
        error_indexes,
        start=1
    ):

        row = df.loc[idx]

        print("\n" + "-" * 55)

        print(
            f"Reprocessando {number}/{len(error_indexes)}"
        )

        print(
            "Título:",
            str(row["title"])[:120]
        )

        start = time.perf_counter()


        try:

            result = classify(row)

            df.at[
                idx,
                "ai_main_candidate"
            ] = result["main_candidate"]


            df.at[
                idx,
                "ai_candidates_json"
            ] = json.dumps(
                result["candidates"],
                ensure_ascii=False
            )


            # Marca explicitamente que esse registro
            # foi recuperado pelo 4B
            df.at[
                idx,
                "ai_model"
            ] = MODEL


            df.at[
                idx,
                "ai_error"
            ] = ""


            elapsed = (
                time.perf_counter() - start
            )


            fixed += 1


            print(
                "Principal:",
                result["main_candidate"]
            )

            print(
                f"Tempo: {elapsed:.1f}s"
            )

            print("OK")


            # Salva após cada correção
            df.to_csv(
                FILE,
                index=False,
                encoding="utf-8-sig"
            )


        except Exception as error:

            failed += 1

            df.at[
                idx,
                "ai_error"
            ] = str(error)


            print(
                "FALHOU:",
                error
            )


    # ========================================================
    # RESULTADO
    # ========================================================

    remaining = (
        df["ai_main_candidate"]
        .astype(str)
        .eq("ERRO")
        .sum()
    )


    df.to_csv(
        FILE,
        index=False,
        encoding="utf-8-sig"
    )


    print("\n" + "=" * 55)

    print(
        "REPROCESSAMENTO FINALIZADO"
    )

    print("=" * 55)

    print(
        f"Corrigidos: {fixed}"
    )

    print(
        f"Falharam novamente: {failed}"
    )

    print(
        f"Erros restantes: {remaining}"
    )


if __name__ == "__main__":
    main()