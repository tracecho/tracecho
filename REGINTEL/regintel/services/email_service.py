from __future__ import annotations

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional

logger = logging.getLogger("regintel.email")
if not logger.handlers:
    import sys
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def is_smtp_configured() -> bool:
    """Check if SMTP is enabled and has minimal credentials configured."""
    enabled = os.environ.get("SMTP_ENABLED", "false").strip().lower() in ("true", "1", "yes")
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    return enabled and bool(user) and bool(password)


def send_contact_emails(
    name: str,
    email: str,
    organization: str,
    enquiry_type: str,
    message: str,
    submission_id: str,
) -> Dict[str, Any]:
    """
    Sends admin notification and user acknowledgement emails via SMTP.
    Returns status dictionary indicating delivery outcome.
    Never raises uncaught exceptions that could disrupt API response.
    """
    result: Dict[str, Any] = {
        "admin_sent": False,
        "user_sent": False,
        "skipped": False,
        "error": None,
    }

    if not is_smtp_configured():
        logger.info(
            "SMTP is disabled or unconfigured (SMTP_ENABLED=%s, SMTP_USER set=%s). Skipping email delivery.",
            os.environ.get("SMTP_ENABLED", "false"),
            bool(os.environ.get("SMTP_USER", "").strip()),
        )
        result["skipped"] = True
        return result

    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com").strip()
    try:
        smtp_port = int(os.environ.get("SMTP_PORT", "587").strip())
    except ValueError:
        smtp_port = 587

    smtp_user = os.environ.get("SMTP_USER", "").strip()
    smtp_password = os.environ.get("SMTP_PASSWORD", "").strip()
    use_tls = os.environ.get("SMTP_USE_TLS", "true").strip().lower() in ("true", "1", "yes")

    from_email = (
        os.environ.get("SMTP_FROM_EMAIL", "").strip()
        or smtp_user
        or "no-reply@tracecho.com"
    )
    from_name = os.environ.get("SMTP_FROM_NAME", "TRACECHO Regulatory Intelligence").strip()
    from_header = f'"{from_name}" <{from_email}>'

    admin_recipient = (
        os.environ.get("ADMIN_EMAIL", "").strip()
        or os.environ.get("CONTACT_ADMIN_EMAIL", "").strip()
        or smtp_user
    )

    try:
        # Connect to SMTP server
        with smtplib.SMTP(smtp_host, smtp_port, timeout=12) as server:
            if use_tls:
                server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)

            # 1. Admin Notification Email
            if admin_recipient:
                admin_msg = MIMEMultipart("alternative")
                admin_msg["Subject"] = f"[TRACECHO Enquiry] {enquiry_type} - {organization} ({name})"
                admin_msg["From"] = from_header
                admin_msg["To"] = admin_recipient
                admin_msg["Reply-To"] = email

                admin_text = f"""New TRACECHO Platform Enquiry Received

Reference ID: {submission_id}
Enquiry Type: {enquiry_type}
Name: {name}
Email: {email}
Organization: {organization}

Message Content:
----------------------------------------
{message}
----------------------------------------

This enquiry has been saved to the TRACECHO contact_submissions database.
"""
                admin_html = f"""<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #202C2A; line-height: 1.5; padding: 20px; background-color: #F5F7F7;">
  <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border: 1px solid #E2E9E6; border-radius: 8px; padding: 24px;">
    <div style="border-bottom: 2px solid #167568; padding-bottom: 12px; margin-bottom: 20px;">
      <h2 style="margin: 0; color: #167568; font-size: 20px;">TRACECHO &bull; New Enquiry</h2>
      <p style="margin: 4px 0 0 0; color: #66736F; font-size: 13px;">Reference ID: {submission_id}</p>
    </div>
    <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 20px;">
      <tr><td style="padding: 6px 0; color: #66736F; width: 130px;"><strong>Enquiry Type:</strong></td><td style="padding: 6px 0; color: #202C2A;">{enquiry_type}</td></tr>
      <tr><td style="padding: 6px 0; color: #66736F;"><strong>Name:</strong></td><td style="padding: 6px 0; color: #202C2A;">{name}</td></tr>
      <tr><td style="padding: 6px 0; color: #66736F;"><strong>Email:</strong></td><td style="padding: 6px 0; color: #202C2A;"><a href="mailto:{email}" style="color: #167568;">{email}</a></td></tr>
      <tr><td style="padding: 6px 0; color: #66736F;"><strong>Organization:</strong></td><td style="padding: 6px 0; color: #202C2A;">{organization}</td></tr>
    </table>
    <div style="background-color: #F5F7F7; border: 1px solid #E2E9E6; border-radius: 6px; padding: 16px; margin-bottom: 20px;">
      <strong style="display: block; font-size: 12px; text-transform: uppercase; color: #66736F; margin-bottom: 8px;">Message:</strong>
      <p style="margin: 0; font-size: 14px; white-space: pre-wrap; color: #202C2A;">{message}</p>
    </div>
    <p style="margin: 0; font-size: 12px; color: #66736F; text-align: center;">Stored in TRACECHO PostgreSQL contact_submissions table.</p>
  </div>
</body>
</html>"""
                admin_msg.attach(MIMEText(admin_text, "plain", "utf-8"))
                admin_msg.attach(MIMEText(admin_html, "html", "utf-8"))
                server.send_message(admin_msg)
                result["admin_sent"] = True
                logger.info("Admin notification email sent successfully to %s", admin_recipient)

            # 2. User Acknowledgement Email
            user_msg = MIMEMultipart("alternative")
            user_msg["Subject"] = f"Thank you for contacting TRACECHO [Ref: {submission_id[:8]}]"
            user_msg["From"] = from_header
            user_msg["To"] = email

            user_text = f"""Dear {name},

Thank you for contacting TRACECHO regarding "{enquiry_type}".

We have received your enquiry and our compliance research team will review your requirements and respond promptly.

Summary of your submission:
- Organization: {organization}
- Enquiry Type: {enquiry_type}
- Reference: {submission_id}

Message:
{message}

Sincerely,
The TRACECHO Team
AI-Powered Regulatory Intelligence
https://tracecho.com
"""
            user_html = f"""<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #202C2A; line-height: 1.5; padding: 20px; background-color: #F5F7F7;">
  <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border: 1px solid #E2E9E6; border-radius: 8px; padding: 24px;">
    <div style="border-bottom: 2px solid #167568; padding-bottom: 12px; margin-bottom: 20px;">
      <h2 style="margin: 0; color: #167568; font-size: 20px;">TRACECHO</h2>
      <p style="margin: 4px 0 0 0; color: #66736F; font-size: 13px;">AI-Powered Regulatory Intelligence &bull; Confirmation</p>
    </div>
    <p style="font-size: 14px; margin-bottom: 16px;">Dear {name},</p>
    <p style="font-size: 14px; margin-bottom: 16px; color: #66736F;">
      Thank you for reaching out to TRACECHO regarding <strong>{enquiry_type}</strong>. We have received your message and our team will review your enquiry promptly.
    </p>
    <div style="background-color: #F5F7F7; border: 1px solid #E2E9E6; border-radius: 6px; padding: 16px; margin-bottom: 20px; font-size: 13px;">
      <div style="margin-bottom: 6px;"><strong>Reference ID:</strong> {submission_id}</div>
      <div style="margin-bottom: 6px;"><strong>Organization:</strong> {organization}</div>
      <div style="margin-bottom: 6px;"><strong>Enquiry Type:</strong> {enquiry_type}</div>
      <div style="margin-top: 10px; padding-top: 10px; border-top: 1px dashed #E2E9E6; color: #66736F;">
        <strong>Your Message:</strong><br />
        <span style="color: #202C2A;">{message}</span>
      </div>
    </div>
    <p style="font-size: 14px; margin-bottom: 8px;">Warm regards,</p>
    <p style="font-size: 14px; margin: 0; font-weight: 600; color: #167568;">The TRACECHO Team</p>
    <p style="font-size: 12px; margin: 4px 0 0 0; color: #66736F;">Grounded Regulatory Intelligence for RBI &amp; SEBI</p>
  </div>
</body>
</html>"""
            user_msg.attach(MIMEText(user_text, "plain", "utf-8"))
            user_msg.attach(MIMEText(user_html, "html", "utf-8"))
            server.send_message(user_msg)
            result["user_sent"] = True
            logger.info("Acknowledgement email sent successfully to user %s", email)

    except Exception as exc:
        logger.error("Failed to deliver contact emails via SMTP: %s", exc)
        result["error"] = str(exc)

    return result

