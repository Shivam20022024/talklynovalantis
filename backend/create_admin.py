"""Create (or repair) the single global super-admin account.

Super admins are platform-level: role == "super_admin", company_id == None.
Idempotent - safe to run repeatedly.
"""
import asyncio
import os
import uuid
from datetime import datetime
import mongodb
from auth import get_password_hash

ADMIN_EMAIL = os.environ.get("SUPER_ADMIN_EMAIL", "admin@talkly.ai")
ADMIN_PASSWORD = os.environ.get("SUPER_ADMIN_PASSWORD", "admin")
ADMIN_NAME = os.environ.get("SUPER_ADMIN_NAME", "Talkly Platform Admin")


async def create_admin():
    db = mongodb.get_db()
    now = datetime.utcnow()

    existing = await db.users.find_one({"email": ADMIN_EMAIL})
    if existing:
        await db.users.update_one(
            {"email": ADMIN_EMAIL},
            {"$set": {
                "role": "super_admin",
                "company_id": None,
                "is_active": True,
                "updated_at": now,
            }},
        )
        print(f"Repaired existing super admin {ADMIN_EMAIL} (role=super_admin, company_id=None)")
        return

    await db.users.insert_one({
        "user_id": str(uuid.uuid4()),
        "name": ADMIN_NAME,
        "email": ADMIN_EMAIL,
        "password_hash": get_password_hash(ADMIN_PASSWORD),
        "role": "super_admin",
        "company_id": None,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    })
    print(f"Created super admin {ADMIN_EMAIL} / {ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(create_admin())
