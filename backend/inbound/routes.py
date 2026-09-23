from fastapi import APIRouter, Request, Response, Depends
from pydantic import BaseModel
from typing import Optional

from .controller import handle_incoming_call, transfer_call, hangup_call
from .session_manager import get_all_inbound_calls, get_inbound_session

inbound_router = APIRouter()

class TransferRequest(BaseModel):
    destination_number: str

class PurchaseRequest(BaseModel):
    area_code: str = ""

class WebhookRequest(BaseModel):
    webhook_url: str

from auth import get_current_user, require_company_admin, require_company_access, tenant_filter
import mongodb
import datetime

# Mock storage removed in favor of MongoDB


@inbound_router.get("/numbers")
async def get_numbers(current_user: dict = Depends(require_company_access)):
    db = mongodb.get_db()
    numbers = []
    cursor = db.phone_numbers.find(tenant_filter(current_user))
    async for num in cursor:
        num["_id"] = str(num["_id"])
        numbers.append(num)
    return {"status": "success", "numbers": numbers}

@inbound_router.post("/numbers/purchase")
async def purchase_number(req: PurchaseRequest, current_user: dict = Depends(require_company_admin)):
    db = mongodb.get_db()
    company_id = current_user["company_id"]
    new_num = f"+1{req.area_code}5551234" # Mock Twilio purchase
    
    # Generate a dummy agent ID for this new number's company
    agent_id = f"agent_{company_id[:8]}"
    bolna_sip_uri = f"sip:{agent_id}@sip.bolna.ai"
    
    doc = {
        "phone_number": new_num,
        "company_id": company_id,
        "agent_id": agent_id,
        "bolna_sip_uri": bolna_sip_uri,
        "provider": "twilio",
        "provider_number_id": "PN1234567890",
        "status": "active",
        "created_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow()
    }
    await db.phone_numbers.insert_one(doc)
    doc["_id"] = str(doc["_id"])
    
    return {"status": "success", "number": doc}

@inbound_router.post("/numbers/{number}/webhook")
async def configure_webhook(number: str, req: WebhookRequest, current_user: dict = Depends(require_company_admin)):
    db = mongodb.get_db()
    # Ensure number belongs to company
    phone = await db.phone_numbers.find_one({"phone_number": number, "company_id": current_user["company_id"]})
    if not phone:
        return {"status": "error", "message": "Number not found or unauthorized"}
        
    await db.phone_numbers.update_one(
        {"phone_number": number},
        {"$set": {"webhook_url": req.webhook_url, "updated_at": datetime.datetime.utcnow()}}
    )
    return {"status": "success", "message": "Webhook updated"}

@inbound_router.post("/webhook")
async def inbound_webhook(request: Request):
    """
    Receives incoming call event from telephony provider (e.g. Twilio).
    Returns TwiML to connect to AI engine.
    """
    form_data = dict(await request.form())
    twiml_response = await handle_incoming_call(form_data)
    return Response(content=twiml_response, media_type="application/xml")

@inbound_router.get("/calls")
async def get_calls(limit: int = 20, skip: int = 0, current_user: dict = Depends(require_company_access)):
    calls = await get_all_inbound_calls(limit=limit, skip=skip, company_id=current_user["company_id"])
    return {"status": "success", "calls": calls}

@inbound_router.get("/{id}")
async def get_call(id: str, current_user: dict = Depends(require_company_access)):
    call = await get_inbound_session(id, company_id=current_user["company_id"])
    if call:
        call["_id"] = None
        return {"status": "success", "call": call}
    return {"status": "error", "message": "Not found"}

async def _assert_owns_inbound(id: str, current_user: dict):
    db = mongodb.get_db()
    call = await db.calls.find_one(tenant_filter(current_user, {"call_id": id}))
    if not call:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Call not found")

@inbound_router.post("/{id}/transfer")
async def transfer(id: str, request: TransferRequest, current_user: dict = Depends(require_company_access)):
    await _assert_owns_inbound(id, current_user)
    result = await transfer_call(id, request.destination_number)
    return result

@inbound_router.post("/{id}/hangup")
async def hangup(id: str, current_user: dict = Depends(require_company_access)):
    await _assert_owns_inbound(id, current_user)
    result = await hangup_call(id)
    return result
