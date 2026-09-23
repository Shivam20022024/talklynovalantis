"""Company-scoped Bolna agent configuration (own company only)."""
from fastapi import APIRouter, Depends, Body
from datetime import datetime

import mongodb
from auth import require_company_access, tenant_filter, enforce_no_foreign_company

agent_router = APIRouter()


@agent_router.get("/agent")
async def get_agent(current_user: dict = Depends(require_company_access)):
    db = mongodb.get_db()
    company = await db.companies.find_one(tenant_filter(current_user, {}))
    mappings = []
    async for m in db.language_mappings.find({"company_id": current_user["company_id"]}):
        m["_id"] = None
        mappings.append(m)
    return {
        "status": "success",
        "data": {
            "bolna_agent_id": (company or {}).get("bolna_agent_id"),
            "language_mappings": mappings,
        },
    }


@agent_router.put("/agent")
async def update_agent(payload: dict = Body(...), current_user: dict = Depends(require_company_access)):
    enforce_no_foreign_company(current_user, payload)
    db = mongodb.get_db()
    company_id = current_user["company_id"]

    # A company admin may set their own default agent id and per-language mappings.
    if "bolna_agent_id" in payload:
        await db.companies.update_one(
            {"company_id": company_id},
            {"$set": {"bolna_agent_id": payload.get("bolna_agent_id"), "updated_at": datetime.utcnow()}},
        )

    for m in payload.get("language_mappings", []) or []:
        lang = m.get("language")
        if not lang:
            continue
        await db.language_mappings.update_one(
            {"company_id": company_id, "language": lang},
            {"$set": {
                "company_id": company_id,
                "language": lang,
                "bolna_agent_id": m.get("bolna_agent_id"),
                "status": m.get("status", "Supported"),
                "updated_at": datetime.utcnow(),
            }},
            upsert=True,
        )

    return {"status": "success"}
