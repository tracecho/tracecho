from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session as DBSession

from db.database import get_db
from db.models import EvaluationRun, QueryHistory, User, UserFeedback, ContactSubmission
from db.schemas import FeedbackCreate, QueryHistoryCreate, TokenData, UserCreate

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "INSECURE_DEFAULT_CHANGE_ME")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = int(os.environ.get("JWT_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def _hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------

def create_user(db: DBSession, user: UserCreate) -> User:
    db_user = User(
        email=user.email,
        hashed_password=_hash_password(user.password),
        full_name=user.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: DBSession, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: DBSession, user_id) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: DBSession, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not _verify_password(password, user.hashed_password):
        return False
    return user


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(days=JWT_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        if user_id is None:
            return None
        return TokenData(user_id=user_id, email=email, role=role)
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: DBSession = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token)
    if token_data is None:
        raise credentials_exc
    user = get_user_by_id(db, token_data.user_id)
    if user is None or not user.is_active:
        raise credentials_exc
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


# ---------------------------------------------------------------------------
# Query history / feedback CRUD
# ---------------------------------------------------------------------------

def create_query_history(
    db: DBSession,
    user_id,
    query: str,
    response_summary: Optional[str] = None,
    regulator: Optional[str] = None,
    evidence_insufficient: bool = False,
) -> QueryHistory:
    entry = QueryHistory(
        user_id=user_id,
        query=query,
        response_summary=response_summary,
        regulator=regulator,
        evidence_insufficient=evidence_insufficient,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def create_feedback(
    db: DBSession,
    user_id,
    feedback: FeedbackCreate,
) -> UserFeedback:
    entry = UserFeedback(
        user_id=user_id,
        query_history_id=feedback.query_history_id,
        rating=feedback.rating,
        comment=feedback.comment,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def create_contact_submission(
    db: DBSession,
    name: str,
    email: str,
    organization: str,
    enquiry_type: str,
    message: str,
    status: str = "pending",
) -> ContactSubmission:
    entry = ContactSubmission(
        name=name.strip(),
        email=email.strip().lower(),
        organization=organization.strip(),
        enquiry_type=enquiry_type.strip(),
        message=message.strip(),
        status=status,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

