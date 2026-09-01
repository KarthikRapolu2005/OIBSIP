"""
skills/email_skill.py -- Sends email via smtplib, ONLY when explicitly
invoked by the user through a command. Credentials come exclusively
from environment variables (SMTP_EMAIL / SMTP_PASSWORD).

SAFETY:
- Nova NEVER sends email automatically or in the background.
- If credentials are not configured, the assistant runs in a SAFE
  SIMULATED MODE: it composes and prints/speaks the email content but
  does not attempt a network connection. This makes the project fully
  demonstrable without real credentials.
- For Gmail, use an "App Password" with a dedicated TEST account, never
  a personal account's main password.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import SMTP_HOST, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, email_configured


def send_email(to_address: str, subject: str, body: str) -> str:
    to_address = (to_address or "").strip()
    subject = (subject or "(no subject)").strip()
    body = (body or "").strip()

    if not to_address:
        return "I need a recipient email address before I can send anything."

    if not email_configured():
        # SAFE SIMULATED MODE -- no network call is made.
        return (
            "[SIMULATED MODE — no SMTP credentials configured]\n"
            f"  To:      {to_address}\n"
            f"  Subject: {subject}\n"
            f"  Body:    {body}\n"
            "No real email was sent. To enable real sending, set SMTP_EMAIL and "
            "SMTP_PASSWORD in your .env file using a TEST email account."
        )

    message = MIMEMultipart()
    message["From"] = SMTP_EMAIL
    message["To"] = to_address
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls(context=context)
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, to_address, message.as_string())
        return f"Email sent successfully to {to_address}."
    except smtplib.SMTPAuthenticationError:
        return (
            "Email authentication failed. Please verify SMTP_EMAIL and SMTP_PASSWORD "
            "(use an app password for Gmail) in your .env file."
        )
    except smtplib.SMTPException as exc:
        return f"Failed to send email due to an SMTP error: {exc}"
    except Exception as exc:
        return f"An unexpected error occurred while sending email: {exc}"
