import json

def build_prompt(text, candidates, system_prompt):
    candidate_text = "\n".join(
        f'{c["id"]}: {", ".join(c["aliases"])}' for c in candidates
    )
    return f"{system_prompt}\n\nCANDIDATOS:\n{candidate_text}\n\nTEXTO:\n{text}"

def validate(result):
    required = [
        "candidate_ids","topic","sentiment","stance","narrative",
        "is_sarcasm","is_news_report","is_campaign_content","confidence"
    ]
    missing = [k for k in required if k not in result]
    if missing:
        raise ValueError(f"Campos ausentes: {missing}")
    return result
