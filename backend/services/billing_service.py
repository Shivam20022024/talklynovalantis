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

# Every new company gets exactly this many seconds of free calling (any mix
# of inbound/outbound), tracked against actual call duration - not a cash
# grant that only approximates minutes depending on call direction.
TRIAL_FREE_SECONDS = 10 * 60

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

    async def reconcile_wallet(self, db, company_id: str) -> dict:
        """Recompute wallet.balance from the company's own transaction ledger
        and correct any drift. Needed because balance updates used to be
        read-then-$set (a lost-update race under concurrent writes, fixed to
        $inc) - this repairs drift that already happened before that fix."""
        wallet = await self.get_or_create_wallet(db, company_id)

        pipeline = [
            {"$match": {"company_id": company_id, "status": "COMPLETED"}},
            {"$group": {
                "_id": "$type",
                "total": {"$sum": "$amount"}
            }}
        ]
        totals = {"CREDIT": 0.0, "DEBIT": 0.0}
        async for doc in db.transactions.aggregate(pipeline):
            if doc["_id"] in totals:
                totals[doc["_id"]] = float(doc.get("total") or 0)

        correct_balance = round(totals["CREDIT"] - totals["DEBIT"], 2)
        old_balance = round(wallet.get("balance", 0.0), 2)
        drift = round(correct_balance - old_balance, 2)

        if drift != 0:
            await db.wallets.update_one(
                {"id": wallet["id"]},
                {"$set": {"balance": correct_balance, "updated_at": datetime.utcnow()}}
            )

        return {
            "company_id": company_id,
            "old_balance": old_balance,
            "correct_balance": correct_balance,
            "drift_corrected": drift
        }

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

        await db.wallets.update_one(
            {"id": wallet["id"]},
            {"$inc": {"balance": amount}, "$set": {"updated_at": datetime.utcnow()}}
        )
        return tx

    async def get_trial_seconds_used(self, db, company_id: str) -> float:
        """Cumulative call duration ever billed for this company - the trial
        allowance is consumed by actual call time, free or not, not reset."""
        pipeline = [
            {"$match": {"company_id": company_id}},
            {"$group": {"_id": None, "total": {"$sum": "$duration_seconds"}}}
        ]
        agg = await db.usage_records.aggregate(pipeline).to_list(1)
        return float(agg[0]["total"]) if agg and agg[0].get("total") else 0.0

    async def check_call_allowance(self, db, company_id: str) -> dict:
        """Whether this company may place/answer another call right now.
        Trial companies get TRIAL_FREE_SECONDS of free calling; everyone
        (trial or not) needs a positive wallet balance once that runs out -
        no company could be blocked by insufficient funds before this."""
        company = await db.companies.find_one({"company_id": company_id})

        # Internal/demo companies on the "unlimited" plan are never metered -
        # always allowed, regardless of trial status or wallet balance.
        if company and company.get("plan_type") == "unlimited":
            return {"allowed": True, "reason": "unlimited_plan"}

        is_trial = not company or company.get("plan_type") == "trial"

        if is_trial:
            used = await self.get_trial_seconds_used(db, company_id)
            if used < TRIAL_FREE_SECONDS:
                return {"allowed": True, "reason": "trial_minutes_remaining"}

        wallet = await self.get_or_create_wallet(db, company_id)
        if wallet.get("balance", 0.0) > 0:
            return {"allowed": True, "reason": "has_balance"}

        return {
            "allowed": False,
            "reason": "Your free trial minutes are used up and your wallet balance is ₹0. Add credits to continue making or receiving calls."
        }

    async def process_call_billing(self, db, call_id: str, company_id: str, direction: str, duration_seconds: float, provider: str = "bolna"):
        if duration_seconds <= 0:
            return None # No duration, no cost

        # Check idempotency
        existing_usage = await db.usage_records.find_one({"call_id": call_id})
        if existing_usage:
            return existing_usage # Already billed

        duration_seconds = float(duration_seconds)
        pricing = DEFAULT_PRICING.get(direction, DEFAULT_PRICING["default"])

        free_seconds_applied = 0.0

        # Fair billing policy:
        # 1. Under 5 seconds (immediate hangup / quick drop): FREE (₹0.00)
        # 2. 5 seconds and above: Fair prorated per-second billing (₹12.00 / 60 = ₹0.20/second),
        #    minus whatever's left of the trial company's free allowance.
        if duration_seconds < 5.0:
            customer_cost = 0.0
            provider_cost = 0.0
            billed_minutes = 0.0
        else:
            provider_cost = round(duration_seconds * (pricing["provider_cost"] / 60.0), 2)
            billed_minutes = round(duration_seconds / 60.0, 2)

            billable_seconds = duration_seconds
            company = await db.companies.find_one({"company_id": company_id})
            is_unlimited = bool(company) and company.get("plan_type") == "unlimited"
            is_trial = not company or company.get("plan_type") == "trial"
            if is_trial:
                used_so_far = await self.get_trial_seconds_used(db, company_id)
                free_remaining = max(0.0, TRIAL_FREE_SECONDS - used_so_far)
                free_seconds_applied = min(duration_seconds, free_remaining)
                billable_seconds = duration_seconds - free_seconds_applied

            # Unlimited companies: still logged below for usage visibility,
            # just never charged.
            customer_cost = 0.0 if is_unlimited else round(billable_seconds * (pricing["customer_price"] / 60.0), 2)

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
            "free_seconds_applied": free_seconds_applied,
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

            await db.wallets.update_one(
                {"id": wallet["id"]},
                {"$inc": {"balance": -customer_cost}, "$set": {"updated_at": datetime.utcnow()}}
            )
        
        return usage_record

    async def get_dashboard_data(self, db, company_id: str):
        wallet = await self.get_or_create_wallet(db, company_id)
        
        # Check company info and trial status
        company = await db.companies.find_one({"company_id": company_id})
        is_unlimited = bool(company) and company.get("plan_type") == "unlimited"
        is_trial = not company or company.get("plan_type") == "trial"
        if is_unlimited:
            plan_name = "Unlimited (Internal)"
        elif is_trial:
            plan_name = "Free Trial Starter"
        else:
            plan_name = company.get("plan_type", "Pay-As-You-Go")
        included_minutes = TRIAL_FREE_SECONDS / 60.0 if is_trial else 0
        
        # Active Plan subscription if any
        sub = await db.company_subscriptions.find_one({"company_id": company_id, "status": "active"})
        if sub:
            plan = await db.subscription_plans.find_one({"id": sub["plan_id"]})
            if plan:
                plan_name = plan.get("name", plan_name)
                included_minutes = plan.get("included_minutes", included_minutes)
                
        now = datetime.utcnow()
        account_start = (company or {}).get("created_at") or now
        if isinstance(account_start, str):
            try:
                account_start = datetime.fromisoformat(account_start)
            except Exception:
                account_start = now

        pipeline = [
            {"$match": {"company_id": company_id}},
            {"$group": {
                "_id": "$service_type",
                "total_seconds": {"$sum": "$duration_seconds"},
                "total_cost": {"$sum": "$customer_cost"}
            }}
        ]

        cursor = db.usage_records.aggregate(pipeline)
        agg = []
        async for doc in cursor:
            agg.append(doc)

        by_direction = {
            "outbound": {"seconds": 0.0, "cost": 0.0},
            "inbound": {"seconds": 0.0, "cost": 0.0}
        }
        for doc in agg:
            direction = str(doc.get("_id") or "outbound_call").replace("_call", "")
            if direction not in by_direction:
                by_direction[direction] = {"seconds": 0.0, "cost": 0.0}
            by_direction[direction]["seconds"] += float(doc.get("total_seconds") or 0)
            by_direction[direction]["cost"] += float(doc.get("total_cost") or 0)

        minutes_used = round(sum(d["seconds"] for d in by_direction.values()) / 60.0, 1)
        total_spending = round(sum(d["cost"] for d in by_direction.values()), 2)

        if minutes_used == 0.0:
            # Fallback to calls collection if usage_records was not created for legacy calls
            calls_cursor = db.calls.find({"company_id": company_id})
            per_second_rate = {
                "outbound": DEFAULT_PRICING["outbound"]["customer_price"] / 60.0,
                "inbound": DEFAULT_PRICING["inbound"]["customer_price"] / 60.0
            }
            async for c in calls_cursor:
                dur = float(c.get("duration_seconds") or 0)
                if dur <= 0:
                    continue
                direction = c.get("direction") or "outbound"
                if direction not in by_direction:
                    by_direction[direction] = {"seconds": 0.0, "cost": 0.0}
                by_direction[direction]["seconds"] += dur
                by_direction[direction]["cost"] += dur * per_second_rate.get(direction, per_second_rate["outbound"])

            minutes_used = round(sum(d["seconds"] for d in by_direction.values()) / 60.0, 1)
            total_spending = round(sum(d["cost"] for d in by_direction.values()), 2)

        breakdown = {
            direction: {
                "minutes": round(d["seconds"] / 60.0, 1),
                "spending": round(d["cost"], 2)
            }
            for direction, d in by_direction.items()
        }

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
            "breakdown": breakdown,
            "total_calls": total_calls,
            "completed_calls": completed_calls,
            "rate_per_minute": 12.0,
            "company_name": company.get("name") if company else "Company",
            # minutes_used/total_spending above are all-time cumulative (not
            # scoped to this month - scoping them down would also reset the
            # trial's one-time 10-minute allowance every month, which is
            # wrong). The label used to claim "month 1 - today" while showing
            # all-time totals; say what it actually is instead.
            "billing_period": f"All-time (since {account_start.strftime('%B %d, %Y')})"
        }

billing_service = BillingService()
