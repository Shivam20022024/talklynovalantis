"""Test harness for tenant-isolation tests.

Runs against a dedicated `talkly_test` database on the configured Mongo cluster.
The database is dropped at the start and end of the session.
"""
import os
import sys
import uuid
from datetime import datetime

# Force the test DB BEFORE importing the app (mongodb.py reads this at import time;
# python-dotenv does not override already-set env vars).
os.environ["MONGODB_DB"] = os.environ.get("TEST_MONGODB_DB", "talkly_test")
os.environ.setdefault("STRICT_BOLNA_AGENT", "true")
os.environ.setdefault("BOLNA_API_KEY", "")  # keep publish path from calling Bolna

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pytest_asyncio
import httpx

import mongodb
from auth import get_password_hash, create_access_token
import server


@pytest_asyncio.fixture
async def db():
    database = mongodb.get_db()
    # clean slate
    for coll in await database.list_collection_names():
        await database[coll].drop()
    yield database
    for coll in await database.list_collection_names():
        await database[coll].drop()


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def _make_company(db, name, *, bolna_agent_id=None, status="ACTIVE"):
    company_id = str(uuid.uuid4())
    now = datetime.utcnow()
    await db.companies.insert_one({
        "company_id": company_id, "name": name, "status": status,
        "bolna_agent_id": bolna_agent_id, "created_at": now, "updated_at": now,
    })
    return company_id


async def _make_user(db, email, role, company_id):
    user_id = str(uuid.uuid4())
    await db.users.insert_one({
        "user_id": user_id, "email": email, "name": email.split("@")[0],
        "password_hash": get_password_hash("pw"), "role": role,
        "company_id": company_id, "is_active": True,
        "created_at": datetime.utcnow(), "updated_at": datetime.utcnow(),
    })
    return user_id


def _token(user_id):
    return create_access_token(data={"sub": user_id})


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def world(db):
    """Two companies with data + one super admin."""
    a_id = await _make_company(db, "Company A", bolna_agent_id="agent-A")
    b_id = await _make_company(db, "Company B", bolna_agent_id="agent-B")

    a_user = await _make_user(db, "a-admin@test.com", "company_admin", a_id)
    b_user = await _make_user(db, "b-admin@test.com", "company_admin", b_id)
    sa_user = await _make_user(db, "root@test.com", "super_admin", None)

    async def seed(company_id, prefix):
        camp_id = str(uuid.uuid4())
        lead_id = str(uuid.uuid4())
        call_id = f"{prefix}-call-1"
        now = datetime.utcnow()
        await db.campaigns.insert_one({
            "campaign_id": camp_id, "company_id": company_id, "name": f"{prefix} Campaign",
            "status": "Active", "created_at": now,
        })
        await db.leads.insert_one({
            "lead_id": lead_id, "company_id": company_id, "campaign_id": camp_id,
            "name": f"{prefix} Lead", "phone": "+910000000000", "status": "New", "created_at": now,
        })
        await db.calls.insert_one({
            "call_id": call_id, "company_id": company_id, "customer_name": f"{prefix} Caller",
            "direction": "outbound", "status": "Completed", "created_at": now,
        })
        await db.prompts.insert_one({
            "company_id": company_id, "draft_prompt": f"{prefix} prompt",
            "published_prompt": f"{prefix} prompt", "status": "Published",
        })
        return {"campaign_id": camp_id, "lead_id": lead_id, "call_id": call_id}

    a_data = await seed(a_id, "A")
    b_data = await seed(b_id, "B")

    return {
        "a": {"company_id": a_id, "user_id": a_user, "token": _token(a_user), **a_data},
        "b": {"company_id": b_id, "user_id": b_user, "token": _token(b_user), **b_data},
        "super": {"user_id": sa_user, "token": _token(sa_user)},
        "auth": _auth,
    }
