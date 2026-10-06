import os
import json
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError(
        "YOUTUBE_API_KEY não encontrada no arquivo .env"
    )


SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


# Janela da coleta
# Datas em horário de Brasília (UTC-3)
START_DATE = "2026-09-01T03:00:00Z"
END_DATE = "2026-10-02T03:00:00Z"


# Candidatos / termos principais
CANDIDATES = [
    "Lula",
    "Flávio Bolsonaro",
    "Ronaldo Caiado",
    "Romeu Zema",
    "Rui Costa Pimenta",
    "Samara Martins",
    "Hertz Dias",
    "Edmilson Costa",
    "Renan Santos",
    "Wilson Grassi",
    "Clariana Barão",
    "Augusto Cury",
]


# ============================================================
# BUSCA DE VÍDEOS
# ============================================================

def search_videos(query, page_token=None):

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 50,
        "regionCode": "BR",
        "relevanceLanguage": "pt",
        "order": "date",
        "publishedAfter": START_DATE,
        "publishedBefore": END_DATE,
        "key": API_KEY,
    }

    if page_token:
        params["pageToken"] = page_token

    response = requests.get(
        SEARCH_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# ESTATÍSTICAS DOS VÍDEOS
# ============================================================

def get_video_statistics(video_ids):

    statistics = {}

    # Máximo de 50 IDs por requisição
    for i in range(0, len(video_ids), 50):

        batch = video_ids[i:i + 50]

        params = {
            "part": "statistics",
            "id": ",".join(batch),
            "key": API_KEY,
        }

        response = requests.get(
            VIDEOS_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        for item in data.get("items", []):

            statistics[item["id"]] = item.get(
                "statistics",
                {}
            )

        processed = min(
            i + 50,
            len(video_ids)
        )

        print(
            f"Estatísticas: "
            f"{processed}/{len(video_ids)} vídeos processados"
        )

    return statistics


# ============================================================
# TRANSFORMAÇÃO
# ============================================================

def transform_results(query, search_data):

    videos = []

    for item in search_data.get("items", []):

        video_id = item["id"].get("videoId")

        if not video_id:
            continue

        snippet = item.get("snippet", {})

        videos.append({

            "platform": "youtube",

            "video_id": video_id,

            "query": query,

            "title": snippet.get("title"),

            "description": snippet.get("description"),

            "channel_id": snippet.get("channelId"),

            "channel_title": snippet.get("channelTitle"),

            "published_at": snippet.get("publishedAt"),

            "url":
                f"https://www.youtube.com/watch?v={video_id}",

            "collected_at":
                datetime.now().isoformat(),

        })

    return videos


# ============================================================
# COLETA
# ============================================================

def collect():

    all_videos = []

    print("=" * 60)
    print("INICIANDO COLETA DO YOUTUBE")
    print("=" * 60)

    print(
        f"Período: {START_DATE} → {END_DATE}"
    )

    print()

    for candidate in CANDIDATES:

        print(
            f"\nBuscando: {candidate}"
        )

        page_token = None

        page_number = 1

        # Até 3 páginas por candidato
        # 50 vídeos por página
        while page_number <= 3:

            search_data = search_videos(
                candidate,
                page_token
            )

            videos = transform_results(
                candidate,
                search_data
            )

            all_videos.extend(videos)

            print(
                f"  Página {page_number}: "
                f"{len(videos)} vídeos"
            )

            page_token = search_data.get(
                "nextPageToken"
            )

            if not page_token:
                break

            page_number += 1


    # ========================================================
    # DEDUPLICAÇÃO
    # ========================================================

    unique_videos = {}

    for video in all_videos:

        unique_videos[
            video["video_id"]
        ] = video

    videos = list(
        unique_videos.values()
    )


    print()
    print(
        f"Vídeos únicos encontrados: "
        f"{len(videos)}"
    )


    # ========================================================
    # ESTATÍSTICAS
    # ========================================================

    video_ids = [
        video["video_id"]
        for video in videos
    ]

    statistics = get_video_statistics(
        video_ids
    )


    for video in videos:

        stats = statistics.get(
            video["video_id"],
            {}
        )

        video["views"] = int(
            stats.get(
                "viewCount",
                0
            )
        )

        video["likes"] = int(
            stats.get(
                "likeCount",
                0
            )
        )

        video["comments"] = int(
            stats.get(
                "commentCount",
                0
            )
        )


    # ========================================================
    # SALVAR
    # ========================================================

    output = {

        "source": "youtube",

        "collected_at":
            datetime.now().isoformat(),

        "period": {

            "start": START_DATE,

            "end": END_DATE

        },

        "candidate_queries":
            CANDIDATES,

        "total_videos":
            len(videos),

        "videos":
            videos

    }


    output_file = (
        RAW_DIR /
        "youtube_videos_setembro_outubro.json"
    )


    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2
        )


    print()
    print("=" * 60)
    print("COLETA FINALIZADA")
    print("=" * 60)

    print(
        f"Vídeos coletados: {len(videos)}"
    )

    print(
        f"Arquivo: {output_file}"
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    collect()