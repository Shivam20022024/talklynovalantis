"""Tenant-isolation security tests (the 13 required properties)."""
import uuid
from datetime import datetime

import pytest

A = lambda w: {"Authorization": f"Bearer {w['a']['token']}"}
B = lambda w: {"Authorization": f"Bearer {w['b']['token']}"}
SA = lambda w: {"Authorization": f"Bearer {w['super']['token']}"}


# 1
async def test_company_a_cannot_read_company_b_leads(client, world):
    r = await client.get("/api/v1/leads", headers=A(world))
    assert r.status_code == 200
    ids = {l["lead_id"] for l in r.json()}
    assert world["a"]["lead_id"] in ids
    assert world["b"]["lead_id"] not in ids


# 2
async def test_company_a_cannot_read_company_b_campaigns(client, world):
    r = await client.get("/api/v1/campaigns", headers=A(world))
    assert r.status_code == 200
    ids = {c["campaign_id"] for c in r.json()}
    assert world["b"]["campaign_id"] not in ids


# 3
async def test_company_a_cannot_read_company_b_calls(client, world):
    r = await client.get("/api/v1/calls", headers=A(world))
    assert r.status_code == 200
    ids = {c["call_id"] for c in r.json()}
    assert world["a"]["call_id"] in ids
    assert world["b"]["call_id"] not in ids

    # direct fetch of B's call as A -> 404
    r = await client.get(f"/api/v1/calls/{world['b']['call_id']}", headers=A(world))
    assert r.status_code == 404


# 4
async def test_company_a_cannot_modify_company_b_records(client, world):
    r = await client.patch(
        f"/api/v1/campaigns/{world['b']['campaign_id']}",
        json={"name": "hacked"}, headers=A(world),
    )
    assert r.status_code == 404


# 5
async def test_company_a_cannot_delete_company_b_records(client, world):
    r = await client.request(
        "DELETE", "/api/v1/leads/delete-bulk",
        json={"lead_ids": [world["b"]["lead_id"]]}, headers=A(world),
    ) if False else await client.post(
        "/api/v1/leads/delete-bulk",
        json={"lead_ids": [world["b"]["lead_id"]]}, headers=A(world),
    )
    assert r.status_code == 200
    assert r.json()["deleted_count"] == 0

    r = await client.delete(f"/api/v1/campaigns/{world['b']['campaign_id']}", headers=A(world))
    assert r.status_code == 404


# 6
async def test_company_a_cannot_use_company_b_bolna_agent(client, world, db):
    # A publishes -> targets ONLY A's agent; a foreign company_id in the body is rejected.
    r = await client.post(
        "/api/v1/prompt/publish",
        json={"prompt": "x", "company_id": world["b"]["company_id"]}, headers=A(world),
    )
    assert r.status_code == 403

    r = await client.post("/api/v1/prompt/publish", json={"prompt": "legit"}, headers=A(world))
    assert r.status_code == 200
    assert r.json()["agent_id"] == "agent-A"

    # B's prompt/agent untouched
    b_prompt = await db.prompts.find_one({"company_id": world["b"]["company_id"]})
    assert b_prompt["published_prompt"] == "B prompt"


# 7
async def test_company_admin_cannot_access_super_admin_apis(client, world):
    for path in ("/api/v1/admin/dashboard", "/api/v1/admin/companies",
                 f"/api/v1/admin/companies/{world['b']['company_id']}/calls"):
        r = await client.get(path, headers=A(world))
        assert r.status_code == 403, path


# 8
async def test_company_a_cannot_change_its_company_id(client, world, db):
    r = await client.post(
        "/api/v1/campaigns",
        json={"name": "c1", "company_id": world["b"]["company_id"]}, headers=A(world),
    )
    assert r.status_code == 403  # enforce_no_foreign_company

    # even without an explicit reject, a created record is stamped with the caller's company
    r = await client.post("/api/v1/campaigns", json={"name": "c2"}, headers=A(world))
    assert r.status_code == 200
    assert r.json()["company_id"] == world["a"]["company_id"]


# 9
async def test_company_a_cannot_impersonate_super_admin(client, world):
    from auth import create_access_token
    # forge a token that *claims* super_admin for A's user id
    forged = create_access_token(data={"sub": world["a"]["user_id"], "role": "super_admin", "company_id": None})
    r = await client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 403  # role is resolved from the DB, not the token


# 10
async def test_super_admin_can_access_all_companies(client, world):
    r = await client.get("/api/v1/admin/companies", headers=SA(world))
    assert r.status_code == 200
    ids = {c["company_id"] for c in r.json()["data"]}
    assert {world["a"]["company_id"], world["b"]["company_id"]} <= ids

    for cid in (world["a"]["company_id"], world["b"]["company_id"]):
        r = await client.get(f"/api/v1/admin/companies/{cid}/overview", headers=SA(world))
        assert r.status_code == 200


# 11
async def test_super_admin_can_switch_company_context(client, world):
    ra = await client.get(f"/api/v1/admin/companies/{world['a']['company_id']}/calls", headers=SA(world))
    rb = await client.get(f"/api/v1/admin/companies/{world['b']['company_id']}/calls", headers=SA(world))
    a_ids = {c["call_id"] for c in ra.json()["data"]}
    b_ids = {c["call_id"] for c in rb.json()["data"]}
    assert world["a"]["call_id"] in a_ids and world["a"]["call_id"] not in b_ids
    assert world["b"]["call_id"] in b_ids and world["b"]["call_id"] not in a_ids

    # unknown company -> 404
    r = await client.get(f"/api/v1/admin/companies/{uuid.uuid4()}/calls", headers=SA(world))
    assert r.status_code == 404


# 12
async def test_new_records_get_correct_company_id(client, world, db):
    r = await client.post("/api/v1/leads", json={"name": "L", "phone": "+911111111111"}, headers=A(world))
    assert r.status_code == 200
    lead = await db.leads.find_one({"lead_id": r.json()["lead_id"]})
    assert lead["company_id"] == world["a"]["company_id"]

    r = await client.post("/api/v1/campaigns", json={"name": "K"}, headers=A(world))
    camp = await db.campaigns.find_one({"campaign_id": r.json()["campaign_id"]})
    assert camp["company_id"] == world["a"]["company_id"]


# 13
async def test_access_request_approval_assigns_company_id(client, world, db):
    req_id = str(uuid.uuid4())
    await db.access_requests.insert_one({
        "id": req_id, "company_name": "Newco", "contact_name": "New Admin",
        "email": "new@newco.com", "password_hash": "x", "status": "PENDING",
        "created_at": datetime.utcnow(),
    })
    r = await client.post(f"/api/v1/access-requests/{req_id}/approve", headers=SA(world))
    assert r.status_code == 200

    user = await db.users.find_one({"email": "new@newco.com"})
    company = await db.companies.find_one({"name": "Newco"})
    assert user["company_id"] == company["company_id"]
    assert user["role"] == "company_admin"
    assert user["is_active"] is True


# extra: deactivated user is locked out
async def test_deactivated_user_rejected(client, world, db):
    await db.users.update_one({"user_id": world["a"]["user_id"]}, {"$set": {"is_active": False}})
    r = await client.get("/api/v1/campaigns", headers=A(world))
    assert r.status_code == 403
