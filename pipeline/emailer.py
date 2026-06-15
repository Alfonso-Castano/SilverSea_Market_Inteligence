# pipeline/emailer.py — Sends the weekly digest via Gmail SMTP
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime


def send_digest(report_text: str, report_html: str, country_name: str) -> None:
    """Send the weekly report as a multipart email (plain text + HTML)."""
    gmail_user = os.environ["GMAIL_USER"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]
    recipients = [r.strip() for r in os.environ["RECIPIENT_EMAILS"].split(",")]

    date_str = datetime.date.today().strftime("%d %B %Y")
    subject = f"Silversea Market Intelligence — {country_name} — {date_str}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = ", ".join(recipients)

    msg.attach(MIMEText(report_text, "plain"))
    msg.attach(MIMEText(report_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipients, msg.as_string())

    print(f"  Email sent to: {', '.join(recipients)}")
