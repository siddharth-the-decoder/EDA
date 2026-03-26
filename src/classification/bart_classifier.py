import pandas as pd
from transformers import pipeline

INPUT = "data/processed/events_preprocessed.csv"
OUTPUT = "data/processed/classified_events_with_departments.csv"

def classify_events():
    df = pd.read_csv(INPUT)

    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    categories = ["CSE","ECE","Engineering","Management","Sports","Academic","Cultural"]

    df["predicted_department"] = df["title"].apply(
        lambda x: classifier(x, categories)["labels"][0]
    )

    df.to_csv(OUTPUT, index=False)
    print("✅ Classification done")

if __name__ == "__main__":
    classify_events()