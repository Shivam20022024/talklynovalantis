import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Load env from .env.local
from dotenv import load_dotenv
load_dotenv('.env.local')

async def main():
    MONGO_URI = os.environ.get("MONGODB_URI")
    
    MONGO_DB_NAME = os.environ.get("MONGODB_DB", "voiceai")
    
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    
    today = datetime.utcnow()
    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
    
    query = {
        "status": "Qualified"
    }
    
    leads = await db.leads.find(query).to_list(length=10)
    for l in leads:
        print(f"Lead ID: {l.get('lead_id')}")
        print(f"  Created: {l.get('created_at')}")
        print(f"  LastContact: {l.get('lastContact')}")
        print(f"  Campaign: {l.get('campaign_id')}")
        print(f"  Status: {l.get('status')}")
        print(f"  Matches $or? {l.get('created_at') >= start_date or (l.get('lastContact') and l.get('lastContact') >= start_date.isoformat())}")

if __name__ == "__main__":
    asyncio.run(main())
