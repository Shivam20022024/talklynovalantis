import asyncio
import mongodb
from datetime import datetime

async def check():
    db = mongodb.get_db()
    calls = await db.calls.find().sort("created_at", -1).limit(5).to_list(5)
    for c in calls:
        print(f"Call ID: {c.get('call_id')} | Status: {c.get('status')} | Cust: {c.get('customer_name')} | Created: {c.get('created_at')}")

asyncio.run(check())
