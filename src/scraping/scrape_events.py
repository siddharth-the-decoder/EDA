# -*- coding: utf-8 -*-

import os, re, csv, tempfile, time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://eventhubcc.vit.ac.in/EventHub/"
HEADLESS = True

DATE_RE = re.compile(r"\d{1,2}[-/ ]\d{1,2}[-/ ]\d{2,4}")
VENUE_RE = re.compile(r"(?:venue|location)\s*[:\-]\s*([^\n|•]+)", re.IGNORECASE)
TYPE_RE = re.compile(r"(workshop|seminar|conference|sports|cultural)", re.IGNORECASE)

def make_driver():
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    return webdriver.Chrome(options=options)

def extract_fields(text):
    date = DATE_RE.search(text)
    venue = VENUE_RE.search(text)
    etype = TYPE_RE.search(text)

    return {
        "date": date.group(0) if date else "",
        "venue": venue.group(1) if venue else "",
        "type": etype.group(1).title() if etype else "",
    }

def main():
    driver = make_driver()
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(URL)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        elements = driver.find_elements(By.XPATH, "//div[contains(@class,'card')]")

        rows = []
        seen = set()

        for el in elements:
            raw = el.text.strip()
            if not raw:
                continue

            title = raw.split("\n")[0]
            if title.lower() in seen:
                continue
            seen.add(title.lower())

            fields = extract_fields(raw)

            rows.append({
                "title": title,
                "date": fields["date"],
                "venue": fields["venue"],
                "type": fields["type"],
                "raw_text": raw,
                "source_url": URL,
            })

        df = pd.DataFrame(rows)
        df = df.drop_duplicates(subset=["title"])

        os.makedirs("data/raw", exist_ok=True)

        df.to_csv("data/raw/eventhub_events_latest.csv", index=False)
        df.to_excel("data/raw/eventhub_events_latest.xlsx", index=False)

        print(f"✅ Saved {len(df)} events")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()