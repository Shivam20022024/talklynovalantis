import uuid
from datetime import datetime
import mongodb

async def create_inbound_session(phone_number: str, call_id: str = None) -> dict:
    """
    Creates a new session for an inbound call in the database.
    Reuses the existing `calls` collection.
    """
    db = mongodb.get_db()
    
    session_id = call_id or f"inb_{uuid.uuid4().hex[:12]}"
    
    doc = {
        "call_id": session_id,
        "customer_id": phone_number,
        "customer_name": "Inbound Caller",
        "direction": "inbound",
        "status": "Active",
        "transcript": "",
        "language": "English/Hindi",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.calls.insert_one(doc)
    doc["_id"] = None
    return doc

async def get_inbound_session(call_id: str, company_id: str = None) -> dict:
    db = mongodb.get_db()
    query = {"call_id": call_id, "direction": "inbound"}
    if company_id:
        query["company_id"] = company_id
    return await db.calls.find_one(query)

async def update_inbound_session(call_id: str, updates: dict):
    db = mongodb.get_db()
    updates["updated_at"] = datetime.utcnow()
    await db.calls.update_one(
        {"call_id": call_id, "direction": "inbound"},
        {"$set": updates}
    )

async def get_all_inbound_calls(limit: int = 20, skip: int = 0, company_id: str = None):
    db = mongodb.get_db()
    query = {"direction": "inbound"}
    if company_id:
        query["company_id"] = company_id
    cursor = db.calls.find(query).sort("created_at", -1).skip(skip).limit(limit)
    calls = []
    async for d in cursor:
        d["_id"] = None
        calls.append(d)
    return calls
