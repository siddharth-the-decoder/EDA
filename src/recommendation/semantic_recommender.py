# -*- coding: utf-8 -*-
"""
Semantic Recommender
--------------------
✔ Matches events with user preferences
✔ Uses Sentence Transformers
✔ Generates contextual recommendations
✔ Saves to data/processed/contextual_recommendations.csv
"""

import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# ===== PATHS =====
EVENTS_PATH = "data/processed/classified_events_with_departments.csv"
USERS_PATH = "data/users/users.csv"
OUTPUT_PATH = "data/processed/contextual_recommendations.csv"

# ===== LOAD MODEL =====
print("🤖 Loading embedding model...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ===== SIMILARITY =====
def get_similarity(text1, text2):
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    return util.cos_sim(emb1, emb2).item()

# ===== MAIN =====
def generate_recommendations(top_k=5):
    if not os.path.exists(EVENTS_PATH):
        print("❌ Missing classified events file")
        return

    if not os.path.exists(USERS_PATH):
        print("❌ Missing users file")
        return

    events = pd.read_csv(EVENTS_PATH)
    users = pd.read_csv(USERS_PATH)

    if events.empty:
        print("⚠️ No events available")
        return

    results = []

    print("🧠 Generating recommendations...")

    for _, user in users.iterrows():
        email = user["email"]
        name = user.get("full_name", "Student")

        # combine preferences
        broad = str(user.get("broad_prefs", ""))
        specific = str(user.get("specific_prefs", ""))

        pref_text = (broad + " ") * 1 + (specific + " ") * 2

        scored_events = []

        for _, event in events.iterrows():
            event_text = " ".join([
                str(event.get("title", "")),
                str(event.get("predicted_department", "")),
                str(event.get("type", "")),
                str(event.get("raw_text", "")),
            ])

            score = get_similarity(pref_text, event_text)

            scored_events.append((score, event))

        # sort by similarity
        scored_events.sort(key=lambda x: x[0], reverse=True)

        # pick top_k
        for score, event in scored_events[:top_k]:
            results.append({
                "email": email,
                "full_name": name,
                "matched_event": event.get("title", ""),
                "predicted_department": event.get("predicted_department", ""),
                "date": event.get("date", ""),
                "venue": event.get("venue", ""),
                "type": event.get("type", ""),
                "source_url": event.get("source_url", ""),
                "similarity_score": round(score, 3)
            })

    df = pd.DataFrame(results)

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Recommendations saved to {OUTPUT_PATH}")

# ===== ENTRY =====
if __name__ == "__main__":
    generate_recommendations(top_k=5)