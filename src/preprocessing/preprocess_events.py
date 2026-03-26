# -*- coding: utf-8 -*-
"""
Preprocess scraped events
-------------------------
✔ Picks latest CSV from data/raw/
✔ Cleans text
✔ Normalizes date
✔ Infers missing event type
✔ Saves to data/processed/events_preprocessed.csv
"""

import os
import glob
import pandas as pd
from datetime import datetime

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
OUTPUT_PATH = os.path.join(PROCESSED_DIR, "events_preprocessed.csv")

# ===== GET LATEST FILE =====
def get_latest_file():
    files = glob.glob(os.path.join(RAW_DIR, "*.csv"))
    if not files:
        raise FileNotFoundError("❌ No CSV files found in data/raw/")
    latest = max(files, key=os.path.getmtime)
    print(f"📂 Using latest file: {os.path.basename(latest)}")
    return latest

# ===== CLEAN TEXT =====
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).replace("\n", " ").replace("\r", " ").strip()
    return " ".join(text.split())

# ===== NORMALIZE DATE =====
def normalize_date(d):
    if pd.isna(d) or str(d).strip() == "":
        return ""
    d = str(d).strip()

    try:
        if "-" in d:
            parts = d.split("-")
            if len(parts[0]) == 2:
                return datetime.strptime(d, "%y-%m-%d").strftime("%Y-%m-%d")
            elif len(parts[0]) == 4:
                return datetime.strptime(d, "%Y-%m-%d").strftime("%Y-%m-%d")
    except:
        return d

    return d

# ===== INFER TYPE =====
def infer_type(row):
    if row.get("type") and str(row["type"]).strip():
        return row["type"]

    text = (row.get("title", "") + " " + row.get("raw_text", "")).lower()

    if "conference" in text:
        return "Conference"
    if "workshop" in text:
        return "Workshop"
    if "seminar" in text:
        return "Seminar"
    if "training" in text or "session" in text:
        return "Training"
    if "sports" in text or "match" in text:
        return "Sports"
    if "festival" in text or "cultural" in text:
        return "Cultural"

    return "General"

# ===== MAIN =====
def main():
    try:
        file = get_latest_file()
    except Exception as e:
        print(e)
        return

    df = pd.read_csv(file)

    print("🧹 Cleaning data...")

    df["title"] = df["title"].apply(clean_text)
    df["venue"] = df["venue"].apply(clean_text)
    df["type"] = df["type"].apply(clean_text)
    df["raw_text"] = df["raw_text"].apply(clean_text)
    df["date"] = df["date"].apply(normalize_date)

    df["type"] = df.apply(infer_type, axis=1)

    # remove empty titles + duplicates
    df = df[df["title"].str.len() > 0]
    df = df.drop_duplicates(subset=["title"])

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"✅ Preprocessed {len(df)} events saved to {OUTPUT_PATH}")

# ===== ENTRY =====
if __name__ == "__main__":
    main()