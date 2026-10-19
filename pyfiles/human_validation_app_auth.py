"""
Authentication and access-control module.
Implements PBKDF2-HMAC-SHA256 password hashing, signed HTTP-only session tokens,
and strict role-based access authorization for Annotator A, Annotator B, and Admin.
"""

import os
import hashlib
import secrets
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status, Depends
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from .config import (
    SECRET_KEY,
    ADMIN_SECRET,
    ANNOTATOR_A_KEY,
    ANNOTATOR_B_KEY
)

serializer = URLSafeTimedSerializer(SECRET_KEY, salt="hinglisheval-session-v1")
SESSION_COOKIE_NAME = "hinglisheval_session"
SESSION_MAX_AGE_SECONDS = 30 * 24 * 3600  # 30 days


def hash_access_code(code: str, salt: Optional[bytes] = None) -> str:
    """Generate a PBKDF2-HMAC-SHA256 hash with an individual random salt."""
    if salt is None:
        salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", code.encode("utf-8"), salt, 100_000)
    return f"{salt.hex()}${dk.hex()}"


def verify_access_code(code: str, stored_hash: str) -> bool:
    """Verify an access code against a stored PBKDF2-HMAC-SHA256 hash."""
    try:
        salt_hex, hash_hex = stored_hash.split("$")
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        calculated = hashlib.pbkdf2_hmac("sha256", code.encode("utf-8"), salt, 100_000)
        return secrets.compare_digest(calculated, expected_hash)
    except Exception:
        return False


def create_session_token(annotator_id: str, role: str, display_name: str) -> str:
    """Serialize a cryptographically signed session token."""
    payload = {
        "annotator_id": annotator_id,
        "role": role,
        "display_name": display_name,
        "created_at": secrets.token_hex(8)
    }
    return serializer.dumps(payload)


def decode_session_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify signature and expiration of a session token."""
    try:
        payload = serializer.loads(token, max_age=SESSION_MAX_AGE_SECONDS)
        return payload
    except (SignatureExpired, BadSignature, Exception):
        return None


def authenticate_credentials(access_code: str) -> Optional[Dict[str, str]]:
    """
    Authenticate an incoming raw access code against configured keys.
    Returns user info dict if valid, else None.
    """
    clean_code = access_code.strip()
    if clean_code == ANNOTATOR_A_KEY:
        return {"id": "annotator_a", "role": "annotator", "display_name": "Annotator A"}
    elif clean_code == ANNOTATOR_B_KEY:
        return {"id": "annotator_b", "role": "annotator", "display_name": "Annotator B"}
    elif clean_code == ADMIN_SECRET:
        return {"id": "admin", "role": "admin", "display_name": "Administrator"}
    return None


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    FastAPI dependency: Resolves current user with standard precedence:
    1. Authorization: Bearer <token> header
    2. Query param ?token=...
    3. HTTP-only session cookie
    """
    # 1. Check Authorization header: Bearer <token>
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token_str = auth_header.split(" ", 1)[1].strip()
        user = decode_session_token(token_str)
        if user:
            return user
        user = authenticate_credentials(token_str)
        if user:
            return user

    # 2. Check query param: ?token=...
    token_param = request.query_params.get("token")
    if token_param:
        token_str = token_param.strip()
        user = decode_session_token(token_str)
        if user:
            return user
        user = authenticate_credentials(token_str)
        if user:
            return user

    # 3. Check HTTP-only cookie
    cookie_token = request.cookies.get(SESSION_COOKIE_NAME)
    if cookie_token:
        user = decode_session_token(cookie_token)
        if user:
            return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Please sign in with your access code."
    )


async def get_optional_user(request: Request) -> Optional[Dict[str, Any]]:
    """Helper to check if request is authenticated without raising an exception."""
    try:
        return await get_current_user(request)
    except HTTPException:
        return None


async def require_admin(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """FastAPI dependency: Enforces administrative privileges."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required."
        )
    return current_user
