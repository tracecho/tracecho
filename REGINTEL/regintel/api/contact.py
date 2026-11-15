from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from typing import Dict, Deque

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as DBSession

from db.crud import create_contact_submission
from db.database import get_db
from db.schemas import ContactResponse, ContactSubmissionCreate
from services.email_service import send_contact_emails

logger = logging.getLogger("regintel.contact")

router = APIRouter(prefix="/api/contact", tags=["contact"])

# ---------------------------------------------------------------------------
# Rate limiting & Anti-Spam (5 requests per 10 minutes per client IP)
# ---------------------------------------------------------------------------
_RATE_LIMIT_WINDOW_SECONDS = 600
_MAX_REQUESTS_PER_WINDOW = 5
_ip_request_timestamps: Dict[str, Deque[float]] = defaultdict(deque)

ALLOWED_ENQUIRY_TYPES = {
    "General Enquiry",
    "Platform Access",
    "Enterprise Solutions",
    "Technical Question",
    "Partnership",
}


def _check_rate_limit(client_ip: str) -> None:
    now = time.time()
    dq = _ip_request_timestamps[client_ip]
    # Prune expired timestamps
    while dq and (now - dq[0]) > _RATE_LIMIT_WINDOW_SECONDS:
        dq.popleft()

    if len(dq) >= _MAX_REQUESTS_PER_WINDOW:
        logger.warning("Rate limit exceeded for IP %s (%d requests in window)", client_ip, len(dq))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many contact submissions from your address. Please wait a few minutes before trying again.",
        )
    dq.append(now)


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def submit_contact_form(
    payload: ContactSubmissionCreate,
    request: Request,
    db: DBSession = Depends(get_db),
):
    # Determine client IP for spam protection
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    elif request.client and request.client.host:
        client_ip = request.client.host
    else:
        client_ip = "127.0.0.1"

    # Anti-bot honeypot check: bots fill hidden fields
    if payload.honeypot and payload.honeypot.strip():
        logger.info("Spam honeypot triggered by IP %s (honeypot value: %s)", client_ip, payload.honeypot)
        # Return synthetic success to confuse bot without persisting or sending email
        return ContactResponse(
            success=True,
            message="Your enquiry has been received.",
            submission_id="bot-filtered",
            email_delivered=False,
        )

    # Validate rate limit
    _check_rate_limit(client_ip)

    # Validate enquiry type
    enquiry_clean = payload.enquiry_type.strip()
    if enquiry_clean not in ALLOWED_ENQUIRY_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid enquiry type. Must be one of: {', '.join(sorted(ALLOWED_ENQUIRY_TYPES))}",
        )

    # Normalize inputs
    name_clean = payload.name.strip()
    email_clean = str(payload.email).strip().lower()
    org_clean = payload.organization.strip()
    msg_clean = payload.message.strip()

    if len(msg_clean) < 20:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Message must be at least 20 characters in length.",
        )

    # 1. Persist to PostgreSQL database
    try:
        submission = create_contact_submission(
            db=db,
            name=name_clean,
            email=email_clean,
            organization=org_clean,
            enquiry_type=enquiry_clean,
            message=msg_clean,
            status="received",
        )
        submission_id_str = str(submission.id)
        logger.info("Saved contact submission %s from %s (%s)", submission_id_str, email_clean, org_clean)
    except Exception as exc:
        logger.error("Failed to save contact submission to database: %s", exc)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving your enquiry. Please try again later.",
        ) from exc

    # 2. Attempt SMTP notification and acknowledgement delivery
    email_result = send_contact_emails(
        name=name_clean,
        email=email_clean,
        organization=org_clean,
        enquiry_type=enquiry_clean,
        message=msg_clean,
        submission_id=submission_id_str,
    )

    # Update submission status if needed based on email outcome
    email_delivered = bool(email_result.get("user_sent") or email_result.get("admin_sent"))
    if email_delivered:
        submission.status = "acknowledged"
    elif email_result.get("error"):
        submission.status = "saved_email_failed"
    else:
        submission.status = "received"
    try:
        db.commit()
    except Exception:
        db.rollback()

    if email_delivered:
        user_message = "Your enquiry has been received successfully and an acknowledgement email has been sent."
    else:
        user_message = "Your enquiry has been received and saved. Our team will review it and get back to you shortly."

    return ContactResponse(
        success=True,
        message=user_message,
        submission_id=submission_id_str,
        email_delivered=email_delivered,
    )

