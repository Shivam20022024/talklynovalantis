import asyncio
import mongodb

async def check():
    db = mongodb.get_db()
    current_user = await db.users.find_one({"company_id": "209cb85e-5ce7-449e-b32c-ad5ca4c6c635"})
    prompt_doc = await db.prompts.find_one({"company_id": current_user["company_id"]})
    print(repr(prompt_doc.get("welcome_message")))

asyncio.run(check())
