from fastapi import APIRouter, HTTPException, Depends, Body
from datetime import datetime
import os
import uuid
import mongodb
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    normalize_role,
    ROLE_SUPER_ADMIN,
)

auth_router = APIRouter()


def _self_register_enabled() -> bool:
    return str(os.environ.get("ALLOW_SELF_REGISTER", "")).strip().lower() in ("1", "true", "yes", "on")


@auth_router.post("/register")
async def register_company(payload: dict = Body(...)):
    """Public sign-up.

    By default this does NOT create an active company - it files a pending
    ``access_requests`` row so a super admin can review it (preserving the
    Request Access workflow). Set ``ALLOW_SELF_REGISTER=true`` to restore instant
    self-service company creation.
    """
    company_name = payload.get("company_name")
    email = payload.get("email")
    password = payload.get("password")
    user_name = payload.get("name")

    if not all([company_name, email, password, user_name]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    db = mongodb.get_db()

    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    if not _self_register_enabled():
        if await db.access_requests.find_one({"email": email, "status": "PENDING"}):
            raise HTTPException(status_code=400, detail="Your access request is already under review.")
        await db.access_requests.insert_one({
            "id": str(uuid.uuid4()),
            "company_name": company_name,
            "contact_name": user_name,
            "email": email,
            "password_hash": get_password_hash(password),
            "status": "PENDING",
            "source": "self_register",
            "created_at": datetime.utcnow(),
        })
        return {
            "status": "pending_review",
            "message": "Your request has been submitted and is pending approval.",
        }

    company_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    now = datetime.utcnow()

    await db.companies.insert_one({
        "company_id": company_id, "name": company_name, "plan_type": "trial",
        "status": "ACTIVE", "bolna_agent_id": None, "created_at": now, "updated_at": now,
    })
    await db.users.insert_one({
        "user_id": user_id, "company_id": company_id, "name": user_name, "email": email,
        "password_hash": get_password_hash(password), "role": "company_admin",
        "is_active": True, "created_at": now, "updated_at": now,
    })

    access_token = create_access_token(data={"sub": user_id, "email": email})
    return {
        "status": "success",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id, "name": user_name, "email": email,
            "role": "company_admin", "company_id": company_id, "company_name": company_name,
        },
    }


@auth_router.post("/login")
async def login(payload: dict = Body(...)):
    email = payload.get("email")
    password = payload.get("password")

    if not all([email, password]):
        raise HTTPException(status_code=400, detail="Missing email or password")

    db = mongodb.get_db()
    user = await db.users.find_one({"email": email})

    if not user or not verify_password(password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.get("is_active") is False or user.get("status") == "PENDING_ACTIVATION":
        raise HTTPException(status_code=401, detail="Your account is not active yet. Please contact support.")

    role = normalize_role(user.get("role")) or "company_admin"
    company_id = None if role == ROLE_SUPER_ADMIN else user.get("company_id")

    company_name = "Platform" if role == ROLE_SUPER_ADMIN else "Unknown"
    if company_id:
        company = await db.companies.find_one({"company_id": company_id})
        if company:
            company_name = company.get("name", "Unknown")

    # The token only needs to identify the user; role/company are re-resolved from
    # the DB on every request by auth.get_current_user.
    access_token = create_access_token(data={"sub": user["user_id"], "email": email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["user_id"],
            "name": user.get("name"),
            "email": email,
            "role": role,
            "company_id": company_id,
            "company_name": company_name,
        },
    }


@auth_router.post("/activate")
async def activate_account(payload: dict = Body(...)):
    token = payload.get("token")
    password = payload.get("password")

    if not token or not password:
        raise HTTPException(status_code=400, detail="Missing token or password")

    db = mongodb.get_db()
    token_doc = await db.activation_tokens.find_one({"token": token, "used": False})

    if not token_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired activation link.")

    if datetime.utcnow() > token_doc["expires_at"]:
        raise HTTPException(status_code=400, detail="Your activation link has expired. Please contact support.")

    user_id = token_doc["user_id"]

    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {
            "password_hash": get_password_hash(password),
            "status": "ACTIVE",
            "is_active": True,
            "updated_at": datetime.utcnow(),
        }},
    )
    await db.activation_tokens.update_one({"token": token}, {"$set": {"used": True}})

    return {"status": "success", "message": "Account activated successfully."}


@auth_router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    db = mongodb.get_db()
    company_name = "Platform" if current_user["role"] == ROLE_SUPER_ADMIN else None
    if current_user.get("company_id"):
        company = await db.companies.find_one({"company_id": current_user["company_id"]})
        if company:
            company_name = company.get("name")
    return {
        "id": current_user["user_id"],
        "user_id": current_user["user_id"],
        "name": current_user.get("name"),
        "email": current_user.get("email"),
        "role": current_user["role"],
        "company_id": current_user.get("company_id"),
        "company_name": company_name,
        "is_active": current_user.get("is_active", True),
    }
