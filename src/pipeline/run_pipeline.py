import subprocess

def run():
    print("\n🚀 STEP 1: Scraping events...")
    subprocess.run(["python", "src/scraping/scrape_events.py"])

    print("\n🧹 STEP 2: Preprocessing...")
    subprocess.run(["python", "src/preprocessing/preprocess_events.py"])

    print("\n🤖 STEP 3: Classification (BART)...")
    subprocess.run(["python", "src/classification/bart_classifier.py"])

    print("\n🧠 STEP 4: Recommendation...")
    subprocess.run(["python", "src/recommendation/semantic_recommender.py"])

    print("\n📧 STEP 5: Sending Emails (DRY MODE)...")
    subprocess.run(["python", "src/notification/send_personalized.py", "--dry"])

    print("\n✅ FULL PIPELINE COMPLETED!")

if __name__ == "__main__":
    run()