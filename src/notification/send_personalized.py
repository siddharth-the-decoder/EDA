# -*- coding: utf-8 -*-
"""
Send Personalized Emails
------------------------
✔ Reads recommendations
✔ Uses HTML template
✔ Sends emails via SMTP
✔ Supports --dry mode (safe testing)
"""

import os
import smtplib
import argparse
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from jinja2 import Template

# ===== PATHS =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
RECS_PATH = os.path.join(BASE_DIR, "data", "processed", "contextual_recommendations.csv")
TPL_PATH = os.path.join(BASE_DIR, "emails", "template.html")

# ===== LOAD DATA =====
def load_recommendations():
    if not os.path.exists(RECS_PATH):
        raise FileNotFoundError("❌ Missing recommendations file")

    df = pd.read_csv(RECS_PATH)

    if "email" not in df.columns:
        raise ValueError("CSV missing email column")

    print(f"✅ Loaded {len(df)} recommendations")
    return df

# ===== LOAD TEMPLATE =====
def load_template():
    if not os.path.exists(TPL_PATH):
        raise FileNotFoundError("❌ Missing email template")

    with open(TPL_PATH, "r", encoding="utf-8") as f:
        return Template(f.read())

# ===== SEND EMAIL =====
def send_email(host, port, user, password, sender, receiver, html, subject, dry):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    msg.attach(MIMEText(html, "html"))

    if dry:
        print(f"[DRY] Email to {receiver}")
        return

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(sender, [receiver], msg.as_string())

    print(f"✅ Sent email to {receiver}")

# ===== MAIN =====
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true")
    args = parser.parse_args()

    load_dotenv()

    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USERNAME")
    SMTP_PASS = os.getenv("SMTP_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM", "EventHub <noreply@example.com>")

    if not SMTP_HOST and not args.dry:
        print("❌ Missing SMTP credentials")
        return

    recs = load_recommendations()
    template = load_template()

    grouped = recs.groupby("email")

    print("📧 Sending emails...")

    for email, user_recs in grouped:
        name = user_recs["full_name"].iloc[0]

        events = []
        for _, row in user_recs.head(3).iterrows():
            events.append({
                "title": row.get("matched_event"),
                "date": row.get("date"),
                "venue": row.get("venue"),
                "source_url": row.get("source_url"),
            })

        html = template.render(full_name=name, events=events)

        send_email(
            SMTP_HOST,
            SMTP_PORT,
            SMTP_USER,
            SMTP_PASS,
            MAIL_FROM,
            email,
            html,
            "🎉 Your Event Recommendations",
            args.dry
        )

    print("✅ All emails processed")

# ===== ENTRY =====
if __name__ == "__main__":
    main()