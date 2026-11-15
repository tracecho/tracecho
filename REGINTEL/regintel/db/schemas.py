from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Auth / User schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


# ---------------------------------------------------------------------------
# QueryHistory schemas
# ---------------------------------------------------------------------------

class QueryHistoryCreate(BaseModel):
    query: str
    response_summary: Optional[str] = None
    regulator: Optional[str] = None
    evidence_insufficient: bool = False


class QueryHistoryOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    query: str
    response_summary: Optional[str]
    regulator: Optional[str]
    evidence_insufficient: bool
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Feedback schemas
# ---------------------------------------------------------------------------

class FeedbackCreate(BaseModel):
    query_history_id: Optional[uuid.UUID] = None
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class FeedbackOut(BaseModel):
    id: uuid.UUID
    query_history_id: Optional[uuid.UUID]
    user_id: uuid.UUID
    rating: int
    comment: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Contact schemas
# ---------------------------------------------------------------------------

class ContactSubmissionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=255)
    organization: str = Field(..., min_length=2, max_length=150)
    enquiry_type: str = Field(..., min_length=2, max_length=100)
    message: str = Field(..., min_length=20, max_length=4000)
    honeypot: Optional[str] = Field(None, max_length=100)


class ContactSubmissionOut(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    organization: str
    enquiry_type: str
    message: str
    status: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ContactResponse(BaseModel):
    success: bool
    message: str
    submission_id: Optional[str] = None
    email_delivered: bool = False

