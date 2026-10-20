import asyncio
import mongodb

async def main():
    db = mongodb.get_db()
    
    # 1. Backfill all campaigns where industry is missing or None
    camp_res = await db.campaigns.update_many(
        {"$or": [{"industry": None}, {"industry": {"$exists": False}}]},
        {"$set": {"industry": "real_estate"}}
    )
    print(f"Backfilled {camp_res.modified_count} campaigns to 'real_estate'")

    # 2. Backfill all leads where industry is missing or None
    lead_res = await db.leads.update_many(
        {"$or": [{"industry": None}, {"industry": {"$exists": False}}]},
        {"$set": {"industry": "real_estate"}}
    )
    print(f"Backfilled {lead_res.modified_count} leads to 'real_estate'")

    # 3. Check TCS company campaigns breakdown by industry
    cid = "209cb85e-5ce7-449e-b32c-ad5ca4c6c635"
    tcs_camps = await db.campaigns.find({"company_id": cid}).to_list(100)
    print(f"TCS now has {len(tcs_camps)} campaigns:")
    for c in tcs_camps:
        print(f" - {c.get('name')} | Industry: {c.get('industry')} | Offering: {c.get('offering') or c.get('property')}")

if __name__ == "__main__":
    asyncio.run(main())
