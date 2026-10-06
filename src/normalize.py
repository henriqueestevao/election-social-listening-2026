import re, unicodedata, hashlib

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = re.sub(r"https?://\S+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def stable_hash(text: str) -> str:
    return hashlib.sha256(normalize_text(text).lower().encode()).hexdigest()

def engagement(row):
    return sum(int(row.get(k, 0) or 0) for k in
               ("likes", "comments", "shares", "views"))
