import asyncio
import mongodb

async def mock_call():
    db = mongodb.get_db()
    current_user = await db.users.find_one({"company_id": "209cb85e-5ce7-449e-b32c-ad5ca4c6c635"})
    lead_id = "test-agent-call-12345"
    customer_name = "Deepak singh"
    campaign_language = "Hindi"
    
    prompt_doc = await db.prompts.find_one({"company_id": current_user["company_id"]})
    base_prompt = prompt_doc.get("prompt") if prompt_doc else ""
    
    prompt_text = base_prompt.replace("{{customer_name}}", customer_name)
    company = await db.companies.find_one({"company_id": current_user["company_id"]})
    company_name_val = company.get("name") if company else "Company"
    prompt_text = prompt_text.replace("{{company_name}}", company_name_val)
    
    welcome_message = prompt_doc.get("welcome_message") if prompt_doc else None
    if welcome_message:
        welcome_text = welcome_message.replace("{{customer_name}}", customer_name)
        welcome_text = welcome_text.replace("{{company_name}}", company_name_val)
    else:
        welcome_text = None
        
    print("UUID in prompt_text:", "209cb85e" in prompt_text)
    print("UUID in welcome_text:", "209cb85e" in welcome_text if welcome_text else False)

asyncio.run(mock_call())
