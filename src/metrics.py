def share_of_voice(df):
    counts = df.groupby("candidate_id").size().rename("mentions")
    out = counts.reset_index()
    out["share_of_voice_pct"] = out["mentions"] / out["mentions"].sum() * 100
    return out.sort_values("mentions", ascending=False)

def daily_volume(df):
    x = df.copy()
    x["day"] = __import__("pandas").to_datetime(x["published_at"]).dt.date
    return x.groupby(["day","candidate_id"]).size().reset_index(name="mentions")
