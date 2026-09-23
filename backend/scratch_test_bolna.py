import asyncio
import mongodb
import json

async def test_bolna():
    db = mongodb.get_db()
    current_user = await db.users.find_one({"company_id": "209cb85e-5ce7-449e-b32c-ad5ca4c6c635"})
    
    prompt_doc = await db.prompts.find_one({"company_id": current_user["company_id"]})
    welcome_message = prompt_doc.get("welcome_message")
    
    customer_name = "Malik Test"
    company = await db.companies.find_one({"company_id": current_user["company_id"]})
    company_name_val = company.get("name") if company else "Company"
    
    welcome_text = welcome_message.replace("{{customer_name}}", customer_name)
    welcome_text = welcome_text.replace("{{company_name}}", company_name_val)
    
    print("UUID in welcome_text?", "209cb85e-5ce7-449e-b32c-ad5ca4c6c635" in welcome_text)
    print("TCS in welcome_text?", "TCS" in welcome_text)

asyncio.run(test_bolna())
