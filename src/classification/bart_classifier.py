# -*- coding: utf-8 -*-
"""
BART Zero-Shot Classification
-----------------------------
✔ Reads preprocessed events
✔ Classifies department/category
✔ Saves to processed file
"""

import os
import pandas as pd
from transformers import pipeline

INPUT_PATH = "data/processed/events_preprocessed.csv"
OUTPUT_PATH = "data/processed/classified_events_with_departments.csv"

def classify_events():
    print("🔍 Loading preprocessed events...")

    if not os.path.exists(INPUT_PATH):
        print("❌ Missing preprocessed file")
        return

    df = pd.read_csv(INPUT_PATH)

    if df.empty:
        print("⚠️ No events found")
        return

    print("🤖 Loading BART model...")
    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli"
    )

    categories = [
        "CSE",
        "ECE",
        "Engineering",
        "Management",
        "Sports",
        "Academic",
        "Cultural"
    ]

    predictions = []

    print("⚡ Classifying events...")

    for _, row in df.iterrows():
        text = f"{row['title']} {row.get('raw_text', '')}"

        try:
            result = classifier(text, candidate_labels=categories)
            predictions.append(result["labels"][0])
        except Exception as e:
            print("⚠️ Error:", e)
            predictions.append("General")

    df["predicted_department"] = predictions

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Classified {len(df)} events saved to {OUTPUT_PATH}")

# ===== ENTRY =====
if __name__ == "__main__":
    classify_events()