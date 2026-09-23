import os
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import mongodb

# Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Canonical role values (server-side source of truth).
ROLE_SUPER_ADMIN = "super_admin"
ROLE_COMPANY_ADMIN = "company_admin"


def normalize_role(raw: Optional[str]) -> Optional[str]:
    """Map any historical casing to the canonical role value.

    Unknown roles (e.g. the unrelated hiring app's ``ORGANIZATION_ADMIN``) are
    returned unchanged - those users simply cannot pass the Talkly role gates.
    """
    if not raw:
        return None
    key = str(raw).strip().lower()
    if key in ("super_admin", "superadmin", "super-admin"):
        return ROLE_SUPER_ADMIN
    if key in ("company_admin", "companyadmin", "company-admin"):
        return ROLE_COMPANY_ADMIN
    return str(raw)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Resolve the authenticated user.

    The JWT is only trusted to identify *who* is calling (``sub``). The
    authoritative ``role`` / ``company_id`` / ``is_active`` are always read from
    the database so that a stale or tampered token cannot escalate privileges or
    switch tenants.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    db = mongodb.get_db()
    user = await db.users.find_one({"user_id": user_id})
    if not user:
        # Legacy fallback: some very old records keyed only on _id.
        try:
            from bson import ObjectId
            user = await db.users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            user = None
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if user.get("is_active") is False:
        raise HTTPException(status_code=403, detail="Your account has been deactivated")

    role = normalize_role(user.get("role")) or ROLE_COMPANY_ADMIN
    company_id = None if role == ROLE_SUPER_ADMIN else user.get("company_id")

    return {
        "user_id": user_id,
        "company_id": company_id,
        "role": role,
        "email": user.get("email") or payload.get("email"),
        "name": user.get("name"),
        "is_active": user.get("is_active", True),
    }


def require_super_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != ROLE_SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Super Admin access required")
    return current_user


def require_company_access(current_user: dict = Depends(get_current_user)):
    """Standard dependency for company-scoped (tenant) endpoints.

    Company admins are always scoped to their own ``company_id``. Super admins do
    not belong to a company - they must use the ``/api/v1/admin`` routes to view a
    specific company, so they are rejected here with a 400 rather than being
    handed unrestricted access to a company-admin endpoint.
    """
    role = current_user.get("role")
    if role == ROLE_SUPER_ADMIN:
        raise HTTPException(
            status_code=400,
            detail="Super admins must access company data via the /api/v1/admin routes",
        )
    if role != ROLE_COMPANY_ADMIN:
        raise HTTPException(status_code=403, detail="Company access required")
    if not current_user.get("company_id"):
        raise HTTPException(status_code=403, detail="No company associated with this account")
    return current_user


# Backwards-compatible alias (older imports).
require_company_admin = require_company_access


# --- Tenant helpers -------------------------------------------------------------

def tenant_filter(current_user: dict, base: Optional[dict] = None) -> dict:
    """Return a Mongo filter that pins the query to the caller's company."""
    query = dict(base or {})
    if current_user.get("role") != ROLE_SUPER_ADMIN:
        query["company_id"] = current_user["company_id"]
    return query


def enforce_no_foreign_company(current_user: dict, *payloads: Optional[dict]) -> None:
    """Reject any request that tries to supply a different company_id.

    No-op for super admins (who legitimately act across companies via admin routes).
    """
    if current_user.get("role") == ROLE_SUPER_ADMIN:
        return
    own = current_user.get("company_id")
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        supplied = payload.get("company_id")
        if supplied is not None and supplied != own:
            raise HTTPException(status_code=403, detail="Cannot act on another company's data")


def stamp_company(current_user: dict, doc: dict) -> dict:
    """Force the document's company_id to the caller's company (drop any client value)."""
    doc.pop("company_id", None)
    if current_user.get("role") != ROLE_SUPER_ADMIN:
        doc["company_id"] = current_user["company_id"]
    return doc


def assert_owned(doc: Optional[dict], current_user: dict) -> dict:
    """404 if the document is missing or belongs to another company."""
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    if current_user.get("role") != ROLE_SUPER_ADMIN and doc.get("company_id") != current_user.get("company_id"):
        raise HTTPException(status_code=404, detail="Not found")
    return doc
