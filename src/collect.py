from datetime import datetime
from pathlib import Path
import json


# Diretório principal do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Pasta onde vamos guardar os dados brutos
RAW_DIR = BASE_DIR / "data" / "raw"

# Cria a pasta caso ela ainda não exista
RAW_DIR.mkdir(parents=True, exist_ok=True)


def save_raw(data, filename):
    """Salva dados brutos em JSON."""

    path = RAW_DIR / filename

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print(f"Arquivo salvo em: {path}")


if __name__ == "__main__":

    test_data = {
        "project": "Election Social Listening 2026",
        "collected_at": datetime.now().isoformat(),
        "status": "collector_ready"
    }

    save_raw(test_data, "test.json")