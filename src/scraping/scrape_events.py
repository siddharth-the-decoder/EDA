# -*- coding: utf-8 -*-
"""
EventHub Scraper
----------------
✔ Launches Chrome (headless)
✔ Scrolls to load all events
✔ Extracts title, date, venue, type
✔ Saves into data/raw/
"""

import os, re, csv, tempfile, time
from datetime import datetime
from typing import List, Dict
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# ===== CONFIG =====
URL = "https://eventhubcc.vit.ac.in/EventHub/"
HEADLESS = True
MAX_SCROLLS = 10

# ===== REGEX =====
DATE_RE = re.compile(
    r"\d{1,2}[-/ ](?:\d{1,2}|[A-Za-z]{3,9})[-/ ]\d{2,4}",
    re.IGNORECASE,
)
VENUE_RE = re.compile(r"(?:venue|location)\s*[:\-]\s*([^\n|•]+)", re.IGNORECASE)
TYPE_RE = re.compile(
    r"(workshop|seminar|talk|webinar|hackathon|conference|sports?|cultural|concert|meetup)",
    re.IGNORECASE,
)

# ===== DRIVER =====
def make_driver():
    temp_dir = tempfile.mkdtemp(prefix="eh_")
    options = webdriver.ChromeOptions()

    if HEADLESS:
        options.add_argument("--headless=new")

    options.add_argument(f"--user-data-dir={temp_dir}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,900")

    return webdriver.Chrome(options=options)

# ===== SCROLL =====
def auto_scroll(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    driver.execute_script("window.scrollTo(0, 0)")

# ===== EXTRACT =====
def extract_fields(text):
    date = DATE_RE.search(text)
    venue = VENUE_RE.search(text)
    etype = TYPE_RE.search(text)

    return {
        "date": date.group(0) if date else "",
        "venue": venue.group(1) if venue else "",
        "type": etype.group(1).title() if etype else "",
    }

# ===== MAIN =====
def main():
    driver = make_driver()
    wait = WebDriverWait(driver, 20)
    rows: List[Dict] = []

    try:
        print("🚀 Opening EventHub...")
        driver.get(URL)

        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        print("⏬ Scrolling...")
        auto_scroll(driver)

        elements = driver.find_elements(By.XPATH, "//div[contains(@class,'card')]")

        print(f"🔍 Found {len(elements)} elements")

        seen = set()

        for el in elements:
            raw = el.text.strip()
            if not raw:
                continue

            title = raw.split("\n")[0]

            key = title.lower().strip()
            if key in seen:
                continue
            seen.add(key)

            fields = extract_fields(raw)

            rows.append({
                "title": title,
                "date": fields["date"],
                "venue": fields["venue"],
                "type": fields["type"],
                "raw_text": raw,
                "source_url": URL,
            })

        print(f"✅ Extracted {len(rows)} unique events")

        # ===== SAVE =====
        os.makedirs("data/raw", exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        csv_path = f"data/raw/eventhub_events_{ts}.csv"
        xlsx_path = f"data/raw/eventhub_events_{ts}.xlsx"

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["title", "date", "venue", "type", "raw_text", "source_url"]
            )
            writer.writeheader()
            writer.writerows(rows)

        pd.DataFrame(rows).to_excel(xlsx_path, index=False)

        print("💾 Saved:", csv_path)
        print("💾 Saved:", xlsx_path)

    finally:
        driver.quit()

# ===== ENTRY =====
if __name__ == "__main__":
    main()