import datetime
import asyncio
import json
import requests
from starlette.concurrency import run_in_threadpool

class CRMService:
    async def sync_call_to_crm(self, db, call_id: str) -> bool:
        """
        Dispatches call intelligence data to the tenant's configured webhook URL
        (Zapier, Make.com, HubSpot, Salesforce, or custom CRM).
        """
        # Look up the call
        call_doc = await db.calls.find_one({"call_id": call_id})
        if not call_doc:
            raise ValueError(f"Call {call_id} not found")

        company_id = call_doc.get("company_id")
        webhook_url = None
        if company_id:
            company = await db.companies.find_one({"company_id": company_id})
            if company and company.get("webhook_url"):
                webhook_url = str(company.get("webhook_url")).strip()

        # Fetch lead if available for extra metadata
        lead_doc = None
        if call_doc.get("call_id"):
            lead_doc = await db.leads.find_one({"lead_id": call_doc.get("call_id")})
        if not lead_doc and call_doc.get("customer_id"):
            lead_doc = await db.leads.find_one({"phone": call_doc.get("customer_id")})

        analysis = call_doc.get("analysis", {})
        requirements = analysis.get("requirements") or analysis.get("property_requirements") or {}

        payload = {
            "event": "call.completed",
            "call_id": call_id,
            "company_id": company_id,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "lead": {
                "name": call_doc.get("customer_name") or (lead_doc.get("name") if lead_doc else "Unknown"),
                "phone": call_doc.get("customer_phone") or call_doc.get("customer_id") or (lead_doc.get("phone") if lead_doc else ""),
                "offering": lead_doc.get("offering") if lead_doc else lead_doc.get("property") if lead_doc else "",
                "status": lead_doc.get("status") if lead_doc else "Contacted",
                "custom_fields": lead_doc.get("custom_fields", {}) if lead_doc else {}
            },
            "call_metrics": {
                "duration_seconds": call_doc.get("duration_seconds", 0),
                "direction": call_doc.get("direction", "outbound"),
                "status": call_doc.get("status", "Completed"),
                "language": call_doc.get("language", "English")
            },
            "ai_intelligence": {
                "sentiment": call_doc.get("sentiment") or analysis.get("sentiment", "neutral"),
                "lead_score": analysis.get("lead_score", 0),
                "lead_temperature": analysis.get("lead_temperature", "Warm"),
                "summary": call_doc.get("summary") or analysis.get("summary", ""),
                "intents": analysis.get("intents", []),
                "action_items": analysis.get("action_items", []),
                "requirements": requirements
            },
            "transcript": call_doc.get("transcript", "")
        }

        webhook_success = True
        webhook_status_code = None

        if webhook_url:
            try:
                def _dispatch():
                    return requests.post(
                        webhook_url,
                        json=payload,
                        headers={"Content-Type": "application/json", "User-Agent": "TalklyAI-Webhook/1.0"},
                        timeout=10
                    )
                resp = await run_in_threadpool(_dispatch)
                webhook_status_code = resp.status_code
                webhook_success = resp.ok
                print(f"CRM Webhook dispatched to {webhook_url} -> Status {resp.status_code}")
            except Exception as ex:
                webhook_success = False
                print(f"CRM Webhook delivery error for call {call_id}: {ex}")

        # Update the database record
        await db.calls.update_one(
            {"call_id": call_id},
            {"$set": {
                "crm_synced": webhook_success,
                "crm_webhook_url": webhook_url,
                "crm_status_code": webhook_status_code,
                "crm_sync_timestamp": datetime.datetime.utcnow().isoformat()
            }}
        )

        return True

    async def send_test_webhook(self, webhook_url: str) -> dict:
        """Sends a verification ping to validate the webhook URL."""
        test_payload = {
            "event": "webhook.test",
            "message": "TalklyAI Webhook connection verified successfully!",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
        def _ping():
            return requests.post(
                webhook_url,
                json=test_payload,
                headers={"Content-Type": "application/json", "User-Agent": "TalklyAI-Webhook/1.0"},
                timeout=8
            )
        resp = await run_in_threadpool(_ping)
        return {
            "success": resp.ok,
            "status_code": resp.status_code,
            "response_text": resp.text[:200]
        }

crm_service = CRMService()
