import os
import pandas as pd

INPUT = "data/raw/eventhub_events_latest.csv"
OUTPUT = "data/processed/events_preprocessed.csv"

def main():
    if not os.path.exists(INPUT):
        print("❌ Missing raw file")
        return

    df = pd.read_csv(INPUT)

    df["title"] = df["title"].astype(str).str.strip()
    df["raw_text"] = df["raw_text"].astype(str)

    df = df.drop_duplicates(subset=["title"])

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUTPUT, index=False)

    print(f"✅ Preprocessed {len(df)} events")

if __name__ == "__main__":
    main()