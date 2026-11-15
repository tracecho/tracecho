from __future__ import annotations

from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from db.crud import (
    JWT_EXPIRE_DAYS,
    authenticate_user,
    create_access_token,
    create_user,
    get_current_user,
    get_user_by_email,
    require_admin,
)
from db.database import get_db
from db.models import User
from db.schemas import Token, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: DBSession = Depends(get_db)):
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user = create_user(db, user_in)
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(days=JWT_EXPIRE_DAYS),
    )
    return Token(access_token=token)


@router.post("/signin", response_model=Token)
def signin(credentials: UserLogin, db: DBSession = Depends(get_db)):
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
        )
    token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=timedelta(days=JWT_EXPIRE_DAYS),
    )
    return Token(access_token=token)


@router.post("/signout")
def signout(_: User = Depends(get_current_user)):
    # Stateless JWT — client discards the token
    return {"detail": "Successfully signed out"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/users", response_model=List[UserOut])
def list_users(
    db: DBSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return db.query(User).all()
