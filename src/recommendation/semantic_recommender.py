import pandas as pd
from sentence_transformers import SentenceTransformer, util
from datetime import datetime

EVENTS = "data/processed/classified_events_with_departments.csv"
USERS = "data/users/users.csv"
OUTPUT = "data/processed/contextual_recommendations.csv"

print("🤖 Loading model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ===== SIMILARITY =====
def similarity(a, b):
    return util.cos_sim(
        model.encode(a, convert_to_tensor=True),
        model.encode(b, convert_to_tensor=True)
    ).item()

# ===== DATE SCORE =====
def recency_score(date_str):
    if not date_str or pd.isna(date_str):
        return 0.2

    try:
        event_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
        days_diff = (event_date - datetime.now()).days

        if days_diff < 0:
            return 0  # past event
        elif days_diff <= 3:
            return 1
        elif days_diff <= 10:
            return 0.7
        else:
            return 0.4
    except:
        return 0.2

# ===== MAIN =====
def main():
    events = pd.read_csv(EVENTS)
    users = pd.read_csv(USERS)

    results = []

    print("🧠 Generating smart recommendations...")

    for _, user in users.iterrows():
        email = user["email"]
        name = user["full_name"]

        broad = str(user.get("broad_prefs", "")).lower()
        specific = str(user.get("specific_prefs", "")).lower()

        pref_text = (broad + " ") * 1 + (specific + " ") * 2

        scored = []

        for _, e in events.iterrows():
            title = str(e.get("title", ""))
            dept = str(e.get("predicted_department", "")).lower()
            etype = str(e.get("type", "")).lower()
            raw = str(e.get("raw_text", ""))

            if not title:
                continue

            event_text = f"{title} {dept} {etype} {raw}"

            # ===== SCORES =====
            sem_score = similarity(pref_text, event_text)

            dept_score = 1 if broad in dept else 0

            type_score = 1 if specific in etype else 0

            rec_score = recency_score(e.get("date", ""))

            final_score = (
                0.6 * sem_score +
                0.2 * dept_score +
                0.1 * type_score +
                0.1 * rec_score
            )

            scored.append((final_score, e))

        # sort by score
        scored.sort(key=lambda x: x[0], reverse=True)

        # top 5
        for score, e in scored[:5]:
            results.append({
                "email": email,
                "full_name": name,
                "matched_event": e.get("title", ""),
                "predicted_department": e.get("predicted_department", ""),
                "type": e.get("type", ""),
                "date": e.get("date", ""),
                "venue": e.get("venue", ""),
                "source_url": e.get("source_url", ""),
                "final_score": round(score, 3)
            })

    df = pd.DataFrame(results)
    df.to_csv(OUTPUT, index=False)

    print(f"✅ Smart recommendations saved → {OUTPUT}")

if __name__ == "__main__":
    main()