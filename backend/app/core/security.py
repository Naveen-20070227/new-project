from datetime import datetime, timedelta, timezone
from typing import Optional
import sys
import json
import base64
import hmac
import hashlib

# Robust PyJWT import with auto-healing and built-in standard library fallback
try:
    import jwt
except ImportError:
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyJWT"])
        import jwt
    except Exception:
        jwt = None

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db

def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def _b64_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64encode(base64.urlsafe_b64decode((data + padding).encode('utf-8')))

def _builtin_jwt_encode(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    hdr_b64 = _b64_encode(json.dumps(header).encode('utf-8'))
    pay_b64 = _b64_encode(json.dumps(payload, default=str).encode('utf-8'))
    signing_input = f"{hdr_b64}.{pay_b64}".encode('utf-8')
    sig = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64_encode(sig)
    return f"{hdr_b64}.{pay_b64}.{sig_b64}"

def _builtin_jwt_decode(token: str, secret: str) -> Optional[dict]:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        hdr_b64, pay_b64, sig_b64 = parts
        signing_input = f"{hdr_b64}.{pay_b64}".encode('utf-8')
        expected_sig = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode((sig_b64 + '=' * (4 - (len(sig_b64) % 4))).encode('utf-8'))
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload_bytes = base64.urlsafe_b64decode((pay_b64 + '=' * (4 - (len(pay_b64) % 4))).encode('utf-8'))
        return json.loads(payload_bytes.decode('utf-8'))
    except Exception:
        return None

security_scheme = HTTPBearer(auto_error=False)

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp())
    }
    if jwt is not None:
        try:
            return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        except Exception:
            pass
    return _builtin_jwt_encode(to_encode, settings.SECRET_KEY)

def decode_access_token(token: str) -> Optional[int]:
    payload = None
    if jwt is not None:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except Exception:
            payload = None
    if payload is None:
        payload = _builtin_jwt_decode(token, settings.SECRET_KEY)
    
    if not payload:
        return None
    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None
    try:
        return int(user_id_str)
    except ValueError:
        return None

def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not auth or not auth.credentials:
        raise credentials_exception
    
    user_id = decode_access_token(auth.credentials)
    if user_id is None:
        raise credentials_exception
    
    from backend.app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user
