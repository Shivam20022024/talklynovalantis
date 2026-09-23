import asyncio
import mongodb
import json

async def test_logic():
    db = mongodb.get_db()
    current_user = await db.users.find_one({"company_id": "209cb85e-5ce7-449e-b32c-ad5ca4c6c635"})
    print("current_user:", current_user)
    
    prompt_doc = await db.prompts.find_one({"company_id": current_user["company_id"]})
    print("prompt_doc company_id:", prompt_doc["company_id"])
    
    welcome_message = prompt_doc.get("welcome_message")
    
    company = await db.companies.find_one({"company_id": current_user["company_id"]})
    company_name_val = company.get("name") if company else "Company"
    print("company_name_val:", company_name_val)
    
    welcome_text = welcome_message.replace("{{customer_name}}", "Aniket")
    welcome_text = welcome_text.replace("{{company_name}}", company_name_val)
    
    with open('test_output.txt', 'w', encoding='utf-8') as out:
        out.write(welcome_text)

asyncio.run(test_logic())
