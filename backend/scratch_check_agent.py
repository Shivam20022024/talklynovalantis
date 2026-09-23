import asyncio
import mongodb

async def check():
    db = mongodb.get_db()
    user = await db.users.find_one({"company_id": "209cb85e-5ce7-449e-b32c-ad5ca4c6c635"})
    print("User agent_id:", user.get("agent_id"))
    
    # Or campaigns
    camps = await db.campaigns.find({"company_id": "209cb85e-5ce7-449e-b32c-ad5ca4c6c635"}).to_list(5)
    for c in camps:
        print("Campaign agent_id:", c.get("agent_id"), "Name:", c.get("name"))

asyncio.run(check())
