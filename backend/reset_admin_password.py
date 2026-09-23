import asyncio
import mongodb
from auth import get_password_hash

async def reset_password():
    db = mongodb.get_db()
    email = "admin@talkly.ai"
    password = "admin"
    
    existing = await db.users.find_one({"email": email})
    if not existing:
        print("Admin user doesn't exist.")
        return
        
    await db.users.update_one(
        {"email": email},
        {"$set": {
            "password_hash": get_password_hash(password),
            "role": "super_admin",
            "company_id": None,
            "is_active": True,
        }}
    )
    print("Admin password reset to 'admin' (role=super_admin, company_id=None).")

if __name__ == "__main__":
    asyncio.run(reset_password())
