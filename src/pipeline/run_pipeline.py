import subprocess
import os

# 🔥 force venv python path
PYTHON = os.path.join("venv", "Scripts", "python.exe")

def run():
    print("\n🚀 STEP 1: Scraping...")
    subprocess.run([PYTHON, "src/scraping/scrape_events.py"])

    print("\n🧹 STEP 2: Preprocessing...")
    subprocess.run([PYTHON, "src/preprocessing/preprocess_events.py"])

    print("\n🤖 STEP 3: Classification...")
    subprocess.run([PYTHON, "src/classification/bart_classifier.py"])

    print("\n🧠 STEP 4: Recommendation...")
    subprocess.run([PYTHON, "src/recommendation/semantic_recommender.py"])

    print("\n📧 STEP 5: Email...")
    subprocess.run([PYTHON, "src/notification/send_personalized.py"])

    print("\n✅ PIPELINE COMPLETED")

if __name__ == "__main__":
    run()