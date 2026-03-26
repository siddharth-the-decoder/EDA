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
def send_email(to_email, subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["From"] = MAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.connect(SMTP_HOST, SMTP_PORT)   # 🔥 FIX
        server.ehlo()
        server.starttls()
        server.ehlo()

        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

        server.quit()

    except Exception as e:
        raise e

# ===== MAIN =====
def main():
    df = pd.read_csv(RECS)
    sent = load_log()

    already = set(sent["email"].tolist())
    new = []

    print("📧 Sending emails...\n")

    for email in df["email"].unique():

        if email in already:
            print(f"⏩ Skipping already sent: {email}")
            continue

        print(f"📧 Sending to {email}")

        user_events = df[df["email"] == email].head(3)

        # ===== BUILD HTML EVENTS =====
        events_html = ""

        for _, row in user_events.iterrows():
            date = row['date'] if pd.notna(row['date']) else "TBD"
            venue = row['venue'] if pd.notna(row['venue']) else "TBA"

            events_html += f"""
            <div style="padding:12px; border:1px solid #ddd; border-radius:10px; margin-bottom:12px; background:#fafafa;">
                <h3 style="margin:0; color:#222;">{row['matched_event']}</h3>
                <p style="margin:6px 0;">📅 <b>Date:</b> {date}</p>
                <p style="margin:6px 0;">📍 <b>Venue:</b> {venue}</p>
                <a href="{row['source_url']}" 
                   style="display:inline-block; margin-top:5px; color:white; background:#007bff; padding:6px 10px; border-radius:5px; text-decoration:none;">
                   View Event
                </a>
            </div>
            """

        # ===== FULL HTML TEMPLATE =====
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background:#f4f6f8; padding:20px;">
            <div style="max-width:600px; margin:auto; background:white; padding:20px; border-radius:12px; box-shadow:0 2px 10px rgba(0,0,0,0.1);">
                
                <h2 style="color:#007bff;">🎉 Your Event Recommendations</h2>
                
                <p>Hi 👋,</p>
                <p>We found some exciting events tailored just for you:</p>

                {events_html}

                <hr>
                <p style="font-size:12px; color:gray;">
                    🚀 Powered by your AI Event Recommender
                </p>

            </div>
        </body>
        </html>
        """

        try:
            send_email(email, "🎉 Your Event Recommendations", html_body)
            new.append(email)
            print(f"✅ Sent successfully to {email}\n")
        except Exception as e:
            print(f"❌ Failed for {email}: {e}\n")

    # ===== UPDATE LOG =====
    if new:
        pd.DataFrame({"email": new}).to_csv(LOG, index=False)

    print("✅ All emails processed")

# ===== ENTRY =====
if __name__ == "__main__":
    main()