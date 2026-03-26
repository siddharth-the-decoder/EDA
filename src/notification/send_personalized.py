# -*- coding: utf-8 -*-

import os
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

RECS = "data/processed/contextual_recommendations.csv"
LOG = "data/processed/sent_log.csv"

# ===== LOAD ENV =====
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USERNAME")
SMTP_PASS = os.getenv("SMTP_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")

# ===== LOAD LOG =====
def load_log():
    if os.path.exists(LOG):
        return pd.read_csv(LOG)
    return pd.DataFrame(columns=["email"])

# ===== SEND EMAIL =====
def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

# ===== MAIN =====
def main():
    df = pd.read_csv(RECS)
    sent = load_log()

    already = set(sent["email"].tolist())
    new = []

    for email in df["email"].unique():
        if email in already:
            print(f"⏩ Skipping {email}")
            continue

        print(f"📧 Sending to {email}")

        user_events = df[df["email"] == email].head(3)

        body = "Your Event Recommendations:\n\n"

        for _, row in user_events.iterrows():
            body += f"- {row['matched_event']} ({row['date']}, {row['venue']})\n"

        try:
            send_email(email, "🎉 Your Event Recommendations", body)
            new.append(email)
            print(f"✅ Sent to {email}")
        except Exception as e:
            print(f"❌ Failed for {email}: {e}")

    if new:
        pd.DataFrame({"email": new}).to_csv(LOG, index=False)

    print("✅ Emails processed")

if __name__ == "__main__":
    main()