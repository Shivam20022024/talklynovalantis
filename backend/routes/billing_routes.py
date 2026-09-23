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
    async for u in cursor:
        u["_id"] = None
        usage.append(u)
    return usage

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
