import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 Stunden

# Argon2 ist der aktuelle Sicherheitsstandard (Password Hashing Competition)
password_hash = PasswordHash.recommended()

# Timing-Angriff-Schutz: Bei unbekanntem Benutzer trotzdem Hash-Vergleich ausführen
DUMMY_HASH = password_hash.hash("dummypassword")

# FastAPI weiß: Token kommt via "Authorization: Bearer ..." Header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(plain_password: str) -> str:
    """Erzeugt einen Argon2-Hash inkl. automatisch eingebettetem Salt."""
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vergleicht ein Klartext-Passwort mit einem gespeicherten Hash."""
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(username: str) -> str:
    """Erzeugt einen signierten JWT mit Ablaufzeit."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> str:
    """
    Dependency: Validiert den Bearer-Token und gibt den Benutzernamen zurück.
    Wirft HTTP 401, wenn der Token ungültig oder abgelaufen ist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ungültige Anmeldedaten",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username or not isinstance(username, str):
            raise credentials_exception
        return username
    except InvalidTokenError:
        raise credentials_exception
    except Exception:
        raise credentials_exception
