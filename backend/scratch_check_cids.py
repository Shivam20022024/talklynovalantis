import asyncio
import mongodb
import json

async def check_all():
    db = mongodb.get_db()
    users = await db.users.find().to_list(10)
    companies = await db.companies.find().to_list(10)
    
    print("Users:")
    for u in users:
        print(f"  - user_id: {u.get('user_id')}, company_id: {u.get('company_id')}, name: {u.get('name')}")
        
    print("\nCompanies:")
    for c in companies:
        print(f"  - company_id: {c.get('company_id')}, name: {c.get('name')}")

asyncio.run(check_all())
