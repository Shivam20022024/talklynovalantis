"""Multi-tenant hardening migration (v2).

Idempotent. Dry-run by default; pass --commit to write.

  python migrate_multi_tenant_v2.py                 # show what would change
  python migrate_multi_tenant_v2.py --commit        # apply
  python migrate_multi_tenant_v2.py --commit --assign-orphans-to <company_id>

What it does:
  * normalises user roles   SUPER_ADMIN -> super_admin, COMPANY_ADMIN -> company_admin
    (ORGANIZATION_ADMIN and any other role are left untouched - different app)
  * super admins: company_id = None, is_active = True
  * every Talkly user (has user_id): ensure is_active, name, updated_at
  * every company: ensure status, bolna_agent_id, created_at, updated_at
  * prompts: legacy {prompt, welcome_message} -> {draft_*, published_*, status}
  * company_id backfill safety net for tenant collections (reports orphans, only
    assigns them when --assign-orphans-to is given)
  * fixes the language_mappings unique index
"""
import argparse
import asyncio
import os
from datetime import datetime

import motor.motor_asyncio
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env.local"))

MONGO_URI = os.environ["MONGODB_URI"]
MONGO_DB_NAME = os.environ.get("MONGODB_DB", "voiceai")

TENANT_COLLECTIONS = [
    "calls", "leads", "campaigns", "prompts", "wallets",
    "transactions", "usage_records", "phone_numbers",
]


def norm_role(raw):
    if not raw:
        return None
    k = str(raw).strip().lower()
    if k in ("super_admin", "superadmin", "super-admin"):
        return "super_admin"
    if k in ("company_admin", "companyadmin", "company-admin"):
        return "company_admin"
    return str(raw)


async def main(commit: bool, assign_orphans_to: str | None):
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    now = datetime.utcnow()
    tag = "APPLY" if commit else "DRY-RUN"
    print(f"=== Multi-tenant migration v2 [{tag}] db={MONGO_DB_NAME} ===\n")

    # 1. Users -----------------------------------------------------------------
    role_changes = 0
    user_field_fills = 0
    super_admins = 0
    async for u in db.users.find({}):
        set_fields = {}
        canonical = norm_role(u.get("role"))
        if canonical and canonical != u.get("role") and canonical in ("super_admin", "company_admin"):
            set_fields["role"] = canonical
            role_changes += 1
        effective_role = canonical or u.get("role")

        # Only touch Talkly users (they carry user_id). The hiring app's users don't.
        if u.get("user_id"):
            if effective_role == "super_admin":
                super_admins += 1
                if u.get("company_id") is not None:
                    set_fields["company_id"] = None
                if u.get("is_active") is not True:
                    set_fields["is_active"] = True
            else:
                if "is_active" not in u:
                    set_fields["is_active"] = u.get("status") != "PENDING_ACTIVATION"
            if not u.get("name"):
                set_fields["name"] = u.get("email", "User")
            if "updated_at" not in u:
                set_fields["updated_at"] = now

        if set_fields:
            user_field_fills += 1
            if commit:
                await db.users.update_one({"_id": u["_id"]}, {"$set": set_fields})
    print(f"users: role normalisations={role_changes}, field fills={user_field_fills}, super_admins={super_admins}")

    # 2. Companies -----------------------------------------------------------
    company_fills = 0
    async for c in db.companies.find({}):
        set_fields = {}
        if "status" not in c:
            set_fields["status"] = "ACTIVE"
        if "bolna_agent_id" not in c:
            set_fields["bolna_agent_id"] = None
        if "created_at" not in c:
            set_fields["created_at"] = now
        if "updated_at" not in c:
            set_fields["updated_at"] = now
        if set_fields:
            company_fills += 1
            if commit:
                await db.companies.update_one({"_id": c["_id"]}, {"$set": set_fields})
    print(f"companies: field fills={company_fills}")

    # 3. Prompts -----------------------------------------------------------
    prompt_migrations = 0
    async for p in db.prompts.find({}):
        if "published_prompt" in p or "draft_prompt" in p:
            continue
        legacy_prompt = p.get("prompt")
        legacy_welcome = p.get("welcome_message")
        set_fields = {
            "draft_prompt": legacy_prompt,
            "draft_welcome_message": legacy_welcome,
            "published_prompt": legacy_prompt,
            "published_welcome_message": legacy_welcome,
            "status": "Published" if legacy_prompt else "Draft",
            "updated_at": now,
        }
        prompt_migrations += 1
        if commit:
            await db.prompts.update_one({"_id": p["_id"]}, {"$set": set_fields})
    print(f"prompts: migrated to draft/published shape={prompt_migrations}")

    # 4. company_id backfill safety net --------------------------------------
    valid_company_ids = {c["company_id"] async for c in db.companies.find({}, {"company_id": 1})}
    for coll in TENANT_COLLECTIONS:
        missing = await db[coll].count_documents({"company_id": {"$in": [None]}}) \
            + await db[coll].count_documents({"company_id": {"$exists": False}})
        bad = await db[coll].count_documents(
            {"company_id": {"$exists": True, "$nin": list(valid_company_ids) + [None]}}
        )
        note = ""
        if missing and assign_orphans_to:
            note = f" -> assigning to {assign_orphans_to}"
            if commit:
                await db[coll].update_many(
                    {"$or": [{"company_id": {"$exists": False}}, {"company_id": None}]},
                    {"$set": {"company_id": assign_orphans_to}},
                )
        elif missing:
            note = " (pass --assign-orphans-to to fix)"
        print(f"{coll}: missing company_id={missing}, unknown company_id={bad}{note}")

    # 5. language_mappings index -------------------------------------------
    try:
        if commit:
            await db.language_mappings.drop_index("language_1")
        print("language_mappings: dropped unique index language_1" + ("" if commit else " (would)"))
    except Exception as e:
        print(f"language_mappings: no language_1 index to drop ({e})")
    if commit:
        await db.language_mappings.create_index([("company_id", 1), ("language", 1)])

    print(f"\n=== done [{tag}] ===")
    if not commit:
        print("Re-run with --commit to apply.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--assign-orphans-to", default=None)
    args = ap.parse_args()
    asyncio.run(main(args.commit, args.assign_orphans_to))
