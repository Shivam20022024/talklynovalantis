from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any, List
import mongodb
from auth import require_company_access as get_current_user
from services.billing_service import billing_service
from services.payment_provider import payment_provider

billing_router = APIRouter()

class OrderRequest(BaseModel):
    amount: float
    currency: str = "INR"

class VerifyRequest(BaseModel):
    order_id: str

class TopUpRequest(BaseModel):
    amount: float
    description: str = "Wallet Recharge"

@billing_router.get("/wallet")
async def get_wallet_dashboard(current_user: dict = Depends(get_current_user)):
    db = mongodb.get_db()
    return await billing_service.get_dashboard_data(db, current_user["company_id"])

@billing_router.get("/transactions")
async def get_transactions(limit: int = 50, skip: int = 0, current_user: dict = Depends(get_current_user)):
    db = mongodb.get_db()
    cursor = db.transactions.find({"company_id": current_user["company_id"]}).sort("created_at", -1).skip(skip).limit(limit)
    transactions = []
    async for tx in cursor:
        tx["_id"] = None
        transactions.append(tx)
    return transactions

@billing_router.get("/usage")
async def get_usage(limit: int = 50, skip: int = 0, current_user: dict = Depends(get_current_user)):
    db = mongodb.get_db()
    cursor = db.usage_records.find({"company_id": current_user["company_id"]}).sort("created_at", -1).skip(skip).limit(limit)
    usage = []
    call_ids = []
    async for u in cursor:
        u["_id"] = None
        usage.append(u)
        if u.get("call_id"):
            call_ids.append(u["call_id"])
            
    # Enrich with customer name and phone from calls collection
    if call_ids:
        calls = await db.calls.find({"call_id": {"$in": call_ids}}).to_list(len(call_ids))
        call_map = {c["call_id"]: c for c in calls}
        for u in usage:
            cid = u.get("call_id")
            if cid in call_map:
                u["customer_name"] = call_map[cid].get("customer_name") or "Valued Customer"
                u["phone"] = call_map[cid].get("customer_id") or ""
                u["status"] = call_map[cid].get("status") or "Completed"
                u["language"] = call_map[cid].get("language") or "English"

    # Fallback: if usage_records was empty but calls exist, synthesize usage from completed calls
    if not usage:
        calls_cursor = db.calls.find({"company_id": current_user["company_id"]}).sort("created_at", -1).skip(skip).limit(limit)
        async for c in calls_cursor:
            dur = float(c.get("duration_seconds") or 0)
            if dur < 5.0:
                cost = 0.0
                mins = 0.0
            else:
                cost = round(dur * 0.20, 2)
                mins = round(dur / 60.0, 2)
            usage.append({
                "id": str(c.get("_id")),
                "call_id": c.get("call_id"),
                "customer_name": c.get("customer_name") or "Valued Customer",
                "phone": c.get("customer_id") or "",
                "duration_seconds": dur,
                "billed_minutes": mins,
                "customer_cost": cost,
                "service_type": f"{c.get('direction', 'outbound')}_call",
                "status": c.get("status") or "Completed",
                "created_at": c.get("created_at")
            })

    return usage

@billing_router.post("/wallet/topup")
async def direct_topup(req: TopUpRequest, current_user: dict = Depends(get_current_user)):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Recharge amount must be greater than 0")
    import time
    db = mongodb.get_db()
    tx = await billing_service.add_credits(
        db=db,
        company_id=current_user["company_id"],
        amount=float(req.amount),
        payment_provider="direct_topup",
        provider_transaction_id=f"topup_{int(time.time()*1000)}",
        description=req.description or f"Wallet top-up (₹{req.amount})"
    )
    return {"status": "success", "message": f"Successfully credited ₹{req.amount} to your wallet.", "transaction": tx}

@billing_router.post("/wallet/create-order")
async def create_order(req: OrderRequest, current_user: dict = Depends(get_current_user)):
    try:
        # Create Razorpay order
        notes = {"company_id": current_user["company_id"]}
        order = payment_provider.create_order(amount=req.amount, currency=req.currency, notes=notes)
        return {"status": "success", "order": order}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@billing_router.post("/wallet/verify-payment")
async def verify_payment(req: VerifyRequest, current_user: dict = Depends(get_current_user)):
    order_data = payment_provider.fetch_order(req.order_id)
    
    if order_data.get("order_status") != "PAID":
        raise HTTPException(status_code=400, detail="Payment not successful")
        
    amount = order_data["order_amount"]
    
    # Credit the user instantly
    db = mongodb.get_db()
    from services.billing_service import billing_service
    await billing_service.add_credits(
        db=db,
        company_id=current_user["company_id"],
        amount=amount,
        payment_provider="cashfree",
        provider_transaction_id=req.order_id,
        description="Wallet top-up via Cashfree"
    )
        
    return {"status": "success", "message": "Payment verified and wallet credited."}

@billing_router.post("/webhook/cashfree")
async def cashfree_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("x-webhook-signature", "")
    timestamp = request.headers.get("x-webhook-timestamp", "")
    
    is_valid = payment_provider.verify_webhook_signature(payload.decode('utf-8'), signature, timestamp)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    import json
    data = json.loads(payload)
    
    if data.get("type") == "PAYMENT_SUCCESS_WEBHOOK":
        payment_data = data.get("data", {}).get("payment", {})
        order_data = data.get("data", {}).get("order", {})
        amount = order_data.get("order_amount", 0)
        company_id = order_data.get("order_tags", {}).get("company_id")
        transaction_id = order_data.get("order_id")
        
        if company_id and payment_data.get("payment_status") == "SUCCESS":
            db = mongodb.get_db()
            from services.billing_service import billing_service
            await billing_service.add_credits(
                db=db,
                company_id=company_id,
                amount=amount,
                payment_provider="cashfree",
                provider_transaction_id=transaction_id,
                description=f"Wallet top-up via Cashfree webhook"
            )
            
    return {"status": "ok"}
