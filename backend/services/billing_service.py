import uuid
from datetime import datetime
import mongodb
from typing import Dict, Any, Optional

# Basic hardcoded pricing for now, can be moved to DB
DEFAULT_PRICING = {
    "outbound": {"provider_cost": 8.0, "customer_price": 12.0},
    "inbound": {"provider_cost": 7.0, "customer_price": 11.0},
    "default": {"provider_cost": 8.0, "customer_price": 12.0}
}

class BillingService:
    async def get_or_create_wallet(self, db, company_id: str):
        wallet = await db.wallets.find_one({"company_id": company_id})
        if not wallet:
            wallet = {
                "id": str(uuid.uuid4()),
                "company_id": company_id,
                "balance": 0.0,
                "currency": "INR",
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await db.wallets.insert_one(wallet)
        return wallet

    async def add_credits(self, db, company_id: str, amount: float, payment_provider: str, provider_transaction_id: str, description: str):
        # Idempotency check
        existing_tx = await db.transactions.find_one({
            "provider_transaction_id": provider_transaction_id,
            "type": "CREDIT",
            "status": "COMPLETED"
        })
        if existing_tx:
            return existing_tx
            
        wallet = await self.get_or_create_wallet(db, company_id)
        
        tx = {
            "id": str(uuid.uuid4()),
            "company_id": company_id,
            "wallet_id": wallet["id"],
            "type": "CREDIT",
            "amount": amount,
            "currency": wallet["currency"],
            "payment_provider": payment_provider,
            "provider_transaction_id": provider_transaction_id,
            "status": "COMPLETED",
            "description": description,
            "created_at": datetime.utcnow()
        }
        
        await db.transactions.insert_one(tx)
        
        new_balance = wallet["balance"] + amount
        await db.wallets.update_one(
            {"id": wallet["id"]},
            {"$set": {"balance": new_balance, "updated_at": datetime.utcnow()}}
        )
        return tx

    async def process_call_billing(self, db, call_id: str, company_id: str, direction: str, duration_seconds: float, provider: str = "bolna"):
        if duration_seconds <= 0:
            return None # No duration, no cost
            
        # Check idempotency
        existing_usage = await db.usage_records.find_one({"call_id": call_id})
        if existing_usage:
            return existing_usage # Already billed
            
        duration_seconds = float(duration_seconds)
        pricing = DEFAULT_PRICING.get(direction, DEFAULT_PRICING["default"])
        
        # Fair billing policy:
        # 1. Under 5 seconds (immediate hangup / quick drop): FREE (₹0.00)
        # 2. 5 seconds and above: Fair prorated per-second billing (₹12.00 / 60 = ₹0.20/second)
        if duration_seconds < 5.0:
            customer_cost = 0.0
            provider_cost = 0.0
            billed_minutes = 0.0
        else:
            customer_cost = round(duration_seconds * (pricing["customer_price"] / 60.0), 2)
            provider_cost = round(duration_seconds * (pricing["provider_cost"] / 60.0), 2)
            billed_minutes = round(duration_seconds / 60.0, 2)
        
        # Check active subscription first
        subscription = await db.company_subscriptions.find_one({
            "company_id": company_id, 
            "status": "active"
        })
        
        wallet = await self.get_or_create_wallet(db, company_id)
        
        usage_record = {
            "id": str(uuid.uuid4()),
            "company_id": company_id,
            "call_id": call_id,
            "provider": provider,
            "duration_seconds": duration_seconds,
            "billed_minutes": billed_minutes,
            "provider_cost": provider_cost,
            "customer_cost": customer_cost,
            "service_type": f"{direction}_call",
            "created_at": datetime.utcnow()
        }
        
        await db.usage_records.insert_one(usage_record)
        
        # Only debit wallet if cost > 0
        if customer_cost > 0:
            tx = {
                "id": str(uuid.uuid4()),
                "company_id": company_id,
                "wallet_id": wallet["id"],
                "type": "DEBIT",
                "amount": customer_cost,
                "currency": wallet["currency"],
                "payment_provider": "wallet",
                "provider_transaction_id": call_id,
                "status": "COMPLETED",
                "description": f"Voice usage: {int(round(duration_seconds))}s ({direction})",
                "created_at": datetime.utcnow()
            }
            await db.transactions.insert_one(tx)
            
            new_balance = round(wallet["balance"] - customer_cost, 2)
            await db.wallets.update_one(
                {"id": wallet["id"]},
                {"$set": {"balance": new_balance, "updated_at": datetime.utcnow()}}
            )
        
        return usage_record

    async def get_dashboard_data(self, db, company_id: str):
        wallet = await self.get_or_create_wallet(db, company_id)
        
        # Check company info and trial status
        company = await db.companies.find_one({"company_id": company_id})
        is_trial = not company or company.get("plan_type") == "trial"
        plan_name = "Free Trial Starter" if is_trial else company.get("plan_type", "Pay-As-You-Go")
        included_minutes = 10 if is_trial else 0
        
        # Active Plan subscription if any
        sub = await db.company_subscriptions.find_one({"company_id": company_id, "status": "active"})
        if sub:
            plan = await db.subscription_plans.find_one({"id": sub["plan_id"]})
            if plan:
                plan_name = plan.get("name", plan_name)
                included_minutes = plan.get("included_minutes", included_minutes)
                
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)
        
        pipeline = [
            {"$match": {"company_id": company_id}},
            {"$group": {"_id": None, "total_seconds": {"$sum": "$duration_seconds"}, "total_cost": {"$sum": "$customer_cost"}}}
        ]
        
        cursor = db.usage_records.aggregate(pipeline)
        agg = []
        async for doc in cursor:
            agg.append(doc)
            
        minutes_used = 0.0
        total_spending = 0.0
        if agg and agg[0].get("total_seconds"):
            minutes_used = round(agg[0]["total_seconds"] / 60.0, 1)
            total_spending = round(agg[0].get("total_cost", 0.0), 2)
        else:
            # Fallback to calls collection if usage_records was not created for legacy calls
            calls_cursor = db.calls.find({"company_id": company_id})
            calls_seconds = 0.0
            async for c in calls_cursor:
                calls_seconds += float(c.get("duration_seconds") or 0)
            if calls_seconds > 0:
                minutes_used = round(calls_seconds / 60.0, 1)
                total_spending = round(calls_seconds * 0.20, 2)

        total_calls = await db.calls.count_documents({"company_id": company_id})
        completed_calls = await db.calls.count_documents({"company_id": company_id, "status": {"$in": ["Completed", "Analyzed"]}})
        
        minutes_remaining = max(0.0, round(included_minutes - minutes_used, 1)) if included_minutes > 0 else 0.0
            
        return {
            "balance": round(wallet.get("balance", 0.0), 2),
            "currency": wallet.get("currency", "INR"),
            "plan_name": plan_name,
            "is_trial": is_trial,
            "minutes_used": minutes_used,
            "minutes_included": included_minutes,
            "minutes_remaining": minutes_remaining,
            "total_spending": total_spending,
            "total_calls": total_calls,
            "completed_calls": completed_calls,
            "rate_per_minute": 12.0,
            "company_name": company.get("name") if company else "Company",
            "billing_period": f"{start_of_month.strftime('%B 1')} - {now.strftime('%B %d, %Y')}"
        }

billing_service = BillingService()
