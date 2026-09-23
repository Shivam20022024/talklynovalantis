# server.py
import os
import sys
import warnings

# Suppress pydub RuntimeWarnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")

# Configure FFmpeg paths at the very start to suppress pydub warnings
USER_FFMPEG_BIN = r"C:\Users\brijb\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
if os.path.exists(USER_FFMPEG_BIN):
    os.environ["PATH"] += os.pathsep + USER_FFMPEG_BIN

import time
import re
import json
import uuid
import asyncio
import requests
import mimetypes
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Form, BackgroundTasks, Depends
from auth import (
    require_company_access,
    tenant_filter,
    enforce_no_foreign_company,
)
from routes.auth_routes import auth_router
from fastapi.middleware.cors import CORSMiddleware
import io
import openpyxl
from fastapi.concurrency import run_in_threadpool
from process_audio import process_uploaded_audio, get_weekly_excel_file, analyze_transcript_text
import mongodb
from services.language_service import LanguageService
from services.intelligence_service import IntelligenceService
language_service = LanguageService()
intelligence_service = IntelligenceService()
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from contextlib import asynccontextmanager

# Load env values
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env.local"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await mongodb.ensure_indexes()
    print("--- PROVIDER CONFIG ---")
    print(f"OpenRouter Analysis: {os.environ.get('OPENROUTER_MODEL', 'Not Set')} (Key: {bool(os.environ.get('OPENROUTER_API_KEY'))})")
    print(f"OpenAI Analysis: gpt-4o (Key: {bool(os.environ.get('OPENAI_API_KEY'))})")
    yield
    # Shutdown logic (if any)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from routes.campaign_routes import campaign_router
from routes.lead_routes import lead_router
from routes.auth_routes import auth_router
from routes.billing_routes import billing_router
from routes.admin_routes import admin_router
from routes.agent_routes import agent_router
from routes.access_requests import access_requests_router
from inbound.routes import inbound_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(billing_router, prefix="/api/v1/billing", tags=["Billing"])
# Super-admin platform APIs. Mounted at /admin (canonical) and /super-admin (legacy alias).
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Super Admin"])
app.include_router(admin_router, prefix="/api/v1/super-admin", tags=["Super Admin (legacy)"])
app.include_router(campaign_router, prefix="/api/v1", tags=["Campaigns"])
app.include_router(lead_router, prefix="/api/v1", tags=["Leads"])
app.include_router(agent_router, prefix="/api/v1", tags=["Agent"])
app.include_router(inbound_router, prefix="/api/v1/inbound")
app.include_router(access_requests_router, prefix="/api/v1/access-requests")
app.include_router(access_requests_router, prefix="/api/v1/admin/access-requests")

from services.billing_service import billing_service
@app.get("/")
@app.head("/")
async def health_check():
    return {"status": "ok", "service": "TalklyAI Backend"}

@app.get("/api/v1/analytics/dashboard")
async def get_analytics_dashboard(range: str = "30 Days", campaign_id: str = None, current_user: dict = Depends(require_company_access)):
    db = mongodb.get_db()
    metrics = await intelligence_service.get_dashboard_metrics(db, current_user["company_id"], range, campaign_id)
    return {"status": "success", "data": metrics}

@app.get("/api/v1/analytics/overall")
async def get_overall_analytics(current_user: dict = Depends(require_company_access)):
    db = mongodb.get_db()
    metrics = await intelligence_service.get_overall_dashboard_metrics(db, current_user["company_id"])
    return {"status": "success", "data": metrics}

@app.get("/api/v1/customers/{customer_id}/timeline")
async def get_customer_timeline(customer_id: str, current_user: dict = Depends(require_company_access)):
    db = mongodb.get_db()
    timeline = await intelligence_service.get_customer_timeline(db, customer_id, current_user["company_id"])
    return {"status": "success", "data": timeline}


DEFAULT_PROMPT = "You are an AI sales agent for TalklyAI. You MUST speak entirely in English. Be polite and qualify the lead by asking if they are looking for a 2BHK or 3BHK apartment."
DEFAULT_WELCOME = "Hi, this is TalklyAI. How can I help you today?"


def _effective_prompt(doc: dict | None):
    """Prompt actually used for live calls: published, then draft, then legacy flat field."""
    if not doc:
        return None, None
    prompt = doc.get("published_prompt") or doc.get("draft_prompt") or doc.get("prompt")
    welcome = doc.get("published_welcome_message") or doc.get("draft_welcome_message") or doc.get("welcome_message")
    return prompt, welcome


def _prompt_view(doc: dict | None) -> dict:
    """Present a prompt doc, tolerating the legacy flat {prompt, welcome_message} shape."""
    if not doc:
        return {
            "status": "success",
            "prompt": DEFAULT_PROMPT,
            "welcome_message": DEFAULT_WELCOME,
            "published_prompt": None,
            "published_welcome_message": None,
            "prompt_status": "Draft",
        }
    draft = doc.get("draft_prompt") or doc.get("prompt")
    draft_welcome = doc.get("draft_welcome_message") or doc.get("welcome_message")
    published = doc.get("published_prompt") or doc.get("prompt")
    published_welcome = doc.get("published_welcome_message") or doc.get("welcome_message")
    return {
        "status": "success",
        "prompt": draft or published or DEFAULT_PROMPT,
        "welcome_message": draft_welcome or published_welcome or DEFAULT_WELCOME,
        "published_prompt": published,
        "published_welcome_message": published_welcome,
        "prompt_status": doc.get("status", "Published" if published else "Draft"),
        "published_at": doc.get("published_at"),
    }


@app.get("/api/v1/prompt")
async def get_prompt(current_user: dict = Depends(require_company_access)):
    db = mongodb.get_db()
    doc = await db.prompts.find_one({"company_id": current_user["company_id"]})
    return _prompt_view(doc)

@app.post("/api/v1/prompt")
async def save_prompt(payload: dict = Body(...), current_user: dict = Depends(require_company_access)):
    enforce_no_foreign_company(current_user, payload)
    db = mongodb.get_db()
    prompt = payload.get("prompt")
    welcome_message = payload.get("welcome_message")
    await db.prompts.update_one(
        {"company_id": current_user["company_id"]},
        {"$set": {
            "draft_prompt": prompt,
            "draft_welcome_message": welcome_message,
            "status": "Draft",
            "updated_at": datetime.utcnow(),
        }},
        upsert=True
    )
    return {"status": "success"}


@app.post("/api/v1/prompt/publish")
async def publish_prompt(payload: dict | None = Body(None), current_user: dict = Depends(require_company_access)):
    payload = payload or {}
    enforce_no_foreign_company(current_user, payload)
    db = mongodb.get_db()
    company_id = current_user["company_id"]

    doc = await db.prompts.find_one({"company_id": company_id})
    prompt = (payload or {}).get("prompt") or (doc or {}).get("draft_prompt") or (doc or {}).get("prompt")
    welcome = (payload or {}).get("welcome_message") or (doc or {}).get("draft_welcome_message") or (doc or {}).get("welcome_message")
    if not prompt:
        raise HTTPException(status_code=400, detail="Nothing to publish - save a draft first")

    company = await db.companies.find_one({"company_id": company_id})
    agent_id = (company or {}).get("bolna_agent_id")
    if not agent_id:
        raise HTTPException(
            status_code=400,
            detail="This company has no dedicated Bolna agent configured. Ask an administrator to set companies.bolna_agent_id.",
        )

    # Push the published prompt to THIS company's Bolna agent only.
    api_key = os.environ.get("BOLNA_API_KEY", "").strip()
    bolna_synced = False
    if api_key:
        try:
            resp = await run_in_threadpool(
                requests.patch,
                f"https://api.bolna.ai/agent/{agent_id}",
                json={"agent_prompts": {"task_1": {"system_prompt": prompt}},
                      "agent_config": {"agent_welcome_message": welcome or ""}},
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                timeout=30,
            )
            bolna_synced = resp.ok
            if not resp.ok:
                print(f"Bolna agent update failed for company {company_id}: {resp.status_code} {resp.text[:200]}")
        except Exception as e:
            print(f"Bolna agent update error for company {company_id}: {e}")

    await db.prompts.update_one(
        {"company_id": company_id},
        {"$set": {
            "published_prompt": prompt,
            "published_welcome_message": welcome,
            "draft_prompt": prompt,
            "draft_welcome_message": welcome,
            "status": "Published",
            "published_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }},
        upsert=True,
    )
    return {"status": "success", "bolna_synced": bolna_synced, "agent_id": agent_id}

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

# Startup logic moved to lifespan context manager above

@app.get("/api/v1/calls")
async def get_calls(limit: int = 20, skip: int = 0, current_user: dict = Depends(require_company_access)):
    db = mongodb.get_db()
    cursor = db.calls.find(tenant_filter(current_user)).sort("created_at", -1).skip(skip).limit(limit)
    calls = []
    async for d in cursor:
        d["_id"] = None
        calls.append(d)
    return calls

@app.delete("/api/v1/calls")
async def delete_all_calls(current_user: dict = Depends(require_company_access)):
    db = mongodb.get_db()
    result = await db.calls.delete_many(tenant_filter(current_user))
    return {"status": "success", "deleted_count": result.deleted_count}

@app.post("/api/v1/calls/delete-bulk")
async def delete_bulk_calls(payload: dict = Body(...), current_user: dict = Depends(require_company_access)):
    db = mongodb.get_db()
    call_ids = payload.get("call_ids", [])
    if not call_ids:
        return {"status": "success", "deleted_count": 0}

    result = await db.calls.delete_many(tenant_filter(current_user, {"call_id": {"$in": call_ids}}))
    return {"status": "success", "deleted_count": result.deleted_count}

@app.get("/api/v1/calls/{call_id}")
async def get_call(call_id: str, current_user: dict = Depends(require_company_access)):
    db = mongodb.get_db()
    doc = await db.calls.find_one(tenant_filter(current_user, {"call_id": call_id}))
    if not doc:
        raise HTTPException(status_code=404, detail="Call not found")
    doc["_id"] = None
    return doc

@app.post("/api/v1/calls/trigger")
async def trigger_bolna_call(payload: dict = Body(...), current_user: dict = Depends(require_company_access)):
    enforce_no_foreign_company(current_user, payload)
    phone_number = str(payload.get("phone_number", "")).replace(" ", "").replace("-", "").replace("(", "").replace(")", "").strip()
    if phone_number and not phone_number.startswith("+"):
        if len(phone_number) == 10 and phone_number.isdigit():
            phone_number = f"+91{phone_number}"
        else:
            phone_number = f"+{phone_number}"
    lead_id = payload.get("lead_id")
    if not lead_id or lead_id == "test-agent-call":
        import time
        lead_id = f"test-agent-call-{int(time.time()*1000)}"
    campaign_language = payload.get("campaign_language", "English")
    ai_voice = payload.get("ai_voice", "Default")
    voice_gender = payload.get("voice_gender", "Female")
    regional_accent = payload.get("regional_accent", "Default")

    api_key = os.environ.get("BOLNA_API_KEY", "").strip()
    
    db = mongodb.get_db()
    
    # Fetch real customer name if lead exists (scoped to this company)
    customer_name = "Phone Lead"
    if lead_id and not lead_id.startswith("test-agent-call-"):
        lead = await db.leads.find_one(tenant_filter(current_user, {"lead_id": payload.get("lead_id")}))
        if not lead:
            try:
                from bson import ObjectId
                lead = await db.leads.find_one(tenant_filter(current_user, {"_id": ObjectId(payload.get("lead_id"))}))
            except Exception:
                pass
        if lead and lead.get("name"):
            customer_name = lead.get("name").strip()

    # 2. Resolve this company's dedicated Bolna agent (never a shared global agent in strict mode)
    try:
        agent_id = await language_service.get_agent_id_for_language(db, campaign_language, current_user["company_id"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not api_key or not agent_id:
        raise HTTPException(status_code=400, detail="Bolna.ai API Key or Agent ID not configured for this company")

    
    # Always fetch latest BASE_URL to ensure it reflects current ngrok/tunnel
    current_base_url = os.environ.get("BASE_URL", "http://localhost:8000").strip()
    
    await db.calls.insert_one({
        "call_id": lead_id,
        "customer_id": phone_number,
        "customer_name": customer_name,
        "direction": "outbound",
        "transcript": "",
        "status": "Initiating",
        "created_at": datetime.utcnow(),
        "language": campaign_language,
        "detected_language": campaign_language,
        "preferred_language": campaign_language,
        "transcript_language": campaign_language,
        "ai_voice": ai_voice,
        "voice_gender": voice_gender,
        "regional_accent": regional_accent,
        "company_id": current_user["company_id"],
        "campaign_id": lead.get("campaign_id") if 'lead' in locals() and lead else None
    })

    url = "https://api.bolna.ai/call"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    bolna_payload = {
        "agent_id": agent_id,
        "recipient_phone_number": phone_number,
        "webhook_url": f"{current_base_url}/webhooks/bolna",
        "user_data": {
            "lead_id": lead_id,
            "customer_name": customer_name,
            "agent_name": "AI Agent",
            "campaign_language": campaign_language,
            "ai_voice": ai_voice,
            "voice_gender": voice_gender,
            "regional_accent": regional_accent,
            "company_id": current_user["company_id"]
        }
    }

    # Fetch custom prompt from DB (published prompt is what live calls use)
    prompt_doc = await db.prompts.find_one({"company_id": current_user["company_id"]})
    _bp, _wm = _effective_prompt(prompt_doc)
    base_prompt = _bp or "You are an AI sales agent for TalklyAI. Be polite and helpful."

    # Replace variables
    prompt_text = base_prompt.replace("{{customer_name}}", customer_name)
    company = await db.companies.find_one({"company_id": current_user["company_id"]})
    company_name_val = company.get("name") if company else "Company"
    prompt_text = prompt_text.replace("{{company_name}}", company_name_val)
    
    bolna_payload["user_data"]["company_name"] = company_name_val
    # Add language instructions if not English
    if campaign_language.lower() != "english":
        prompt_text += f"\n\nIMPORTANT: You MUST speak entirely in the {campaign_language} language. Please reply naturally in {campaign_language}."

    bolna_payload["user_data"]["system_prompt"] = prompt_text

    welcome_message = _wm
    if welcome_message:
        welcome_text = welcome_message.replace("{{customer_name}}", customer_name)
        welcome_text = welcome_text.replace("{{company_name}}", company_name_val)
        bolna_payload["agent_config"] = {
            "agent_welcome_message": welcome_text
        }
        bolna_payload["user_data"]["welcome_message"] = welcome_text

    try:
        import json
        with open("payload_dump.json", "w") as f:
            json.dump(bolna_payload, f, indent=2)
            
        print(f"Triggering Bolna call to {phone_number} with webhook_url: {bolna_payload['webhook_url']}")
        print(f"DUMPING BOLNA PAYLOAD: {json.dumps(bolna_payload, indent=2)}")
        response = requests.post(url, json=bolna_payload, headers=headers, timeout=30)
        
        if not response.ok:
            await db.calls.update_one({"call_id": lead_id}, {"$set": {"status": "Failed"}})
            raise HTTPException(status_code=response.status_code, detail=f"Bolna Error: {response.text}")
        
        bolna_data = response.json()
        execution_id = bolna_data.get("execution_id")
        
        if execution_id:
            # Start a background polling task as a fallback for webhooks
            asyncio.create_task(poll_bolna_execution(execution_id, lead_id, api_key))
            
        return bolna_data
    except HTTPException:
        raise
    except Exception as e:
        await db.calls.update_one({"call_id": lead_id}, {"$set": {"status": "Error"}})
        raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")

async def process_bulk_calls(contacts: list, campaign_language: str = "English", ai_voice: str = "Default", voice_gender: str = "Female", regional_accent: str = "Default", company_id: str = None):
    api_key = os.environ.get("BOLNA_API_KEY", "").strip()
    
    db = mongodb.get_db()
    
    # Dynamically fetch Agent ID based on Database mapping
    agent_id = await language_service.get_agent_id_for_language(db, campaign_language, company_id)
    
    if not api_key or not agent_id:
        return
    current_base_url = os.environ.get("BASE_URL", "http://localhost:8000").strip()
    url = "https://api.bolna.ai/call"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for idx, contact in enumerate(contacts):
        phone_str = str(contact.get("phone", "")).replace(" ", "").replace("-", "").replace("(", "").replace(")", "").strip()
        customer_name = str(contact.get("name", "Bulk Phone Lead")).strip()
        
        # Ensure it has a country code (assuming +91 for 10-digit Indian numbers)
        if phone_str and not phone_str.startswith("+"):
            if len(phone_str) == 10 and phone_str.isdigit():
                phone_str = f"+91{phone_str}"
            else:
                phone_str = f"+{phone_str}"
                
        if not phone_str:
            continue
            
        lead_id = contact.get("lead_id") or f"bulk_{int(time.time() * 1000)}_{idx}"
        
        campaign_id_val = contact.get("campaign_id")
        
        await db.calls.insert_one({
            "call_id": lead_id,
            "customer_id": phone_str,
            "customer_name": customer_name,
            "direction": "outbound",
            "transcript": "",
            "status": "Initiating",
            "created_at": datetime.utcnow(),
            "language": campaign_language,
            "detected_language": campaign_language,
            "preferred_language": campaign_language,
            "transcript_language": campaign_language,
            "ai_voice": ai_voice,
            "voice_gender": voice_gender,
            "regional_accent": regional_accent,
            "company_id": company_id,
            "campaign_id": campaign_id_val
        })
        
        bolna_payload = {
            "agent_id": agent_id,
            "recipient_phone_number": phone_str,
            "webhook_url": f"{current_base_url}/webhooks/bolna",
            "user_data": {
                "lead_id": lead_id,
                "customer_name": customer_name,
                "agent_name": "AI Agent",
                "campaign_language": campaign_language,
                "ai_voice": ai_voice,
                "voice_gender": voice_gender,
                "regional_accent": regional_accent
            }
        }

        # Fetch custom prompt from DB (published)
        prompt_doc = await db.prompts.find_one({"company_id": company_id})
        _bp, _wm = _effective_prompt(prompt_doc)
        base_prompt = _bp or "You are an AI sales agent for TalklyAI. Be polite and helpful."

        # Replace variables
        prompt_text = base_prompt.replace("{{customer_name}}", customer_name)
        company = await db.companies.find_one({"company_id": company_id})
        company_name_val = company.get("name") if company else "Company"
        prompt_text = prompt_text.replace("{{company_name}}", company_name_val)
        
        bolna_payload["user_data"]["company_name"] = company_name_val
        
        # Add language instructions if not English
        if campaign_language.lower() != "english":
            prompt_text += f"\n\nIMPORTANT: You MUST speak entirely in the {campaign_language} language. Please reply naturally in {campaign_language}."

        bolna_payload["user_data"]["system_prompt"] = prompt_text
        
        welcome_message = _wm
        if welcome_message:
            welcome_text = welcome_message.replace("{{customer_name}}", customer_name)
            welcome_text = welcome_text.replace("{{company_name}}", company_name_val)
            bolna_payload["agent_config"] = {
                "agent_welcome_message": welcome_text
            }
            bolna_payload["user_data"]["welcome_message"] = welcome_text
        
        print(f"DEBUG: Parsed name for {phone_str} is -> '{customer_name}'")
        
        try:
            import json
            print(f"Triggering Bulk Bolna call to {phone_str} with webhook_url: {bolna_payload['webhook_url']}")
            print(f"DUMPING BOLNA BULK PAYLOAD: {json.dumps(bolna_payload, indent=2)}")
            # Run blocking request in threadpool
            response = await run_in_threadpool(requests.post, url, json=bolna_payload, headers=headers, timeout=30)
            
            if response.ok:
                bolna_data = response.json()
                execution_id = bolna_data.get("execution_id")
                if execution_id:
                    asyncio.create_task(poll_bolna_execution(execution_id, lead_id, api_key))
            else:
                await db.calls.update_one({"call_id": lead_id}, {"$set": {"status": "Failed"}})
                print(f"Bolna Bulk Error for {phone_str}: {response.text}")
        except HTTPException:
            raise
        except Exception as e:
            print(f"Error processing bulk call for {phone_str}: {e}")
            await db.calls.update_one({"call_id": lead_id}, {"$set": {"status": "Error"}})
            print(f"API Bulk Error for {phone_str}: {str(e)}")
            
        await asyncio.sleep(0.5)

@app.post("/api/v1/calls/trigger-bulk")
async def trigger_bolna_bulk(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    campaign_language: str = Form("English"),
    ai_voice: str = Form("Default"),
    voice_gender: str = Form("Female"),
    regional_accent: str = Form("Default"),
    preview_only: bool = Form(False),
    current_user: dict = Depends(require_company_access)
):
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Only .xlsx and .csv files are supported")
        
    contents = await file.read()
    contacts = []
    
    try:
        if file.filename.endswith('.csv'):
            import csv
            content_str = contents.decode('utf-8', errors='replace')
            reader = csv.reader(io.StringIO(content_str))
            
            rows = list(reader)
            if rows:
                header_row = rows[0]
                phone_col_idx = 0
                name_col_idx = -1
                
                for idx, cell in enumerate(header_row):
                    cell_str = str(cell).lower().strip() if cell else ""
                    if cell_str in ["phone", "phone number", "phone_number", "number", "mobile"]:
                        phone_col_idx = idx
                    elif cell_str in ["name", "customer name", "customer_name", "first name", "full name"]:
                        name_col_idx = idx
                        
                for row in rows[1:]:
                    if row and len(row) > phone_col_idx and row[phone_col_idx]:
                        phone_val = str(row[phone_col_idx]).strip()
                        digits = re.sub(r'\D', '', phone_val)
                        if len(digits) >= 10:
                            name = "Bulk Phone Lead"
                            if name_col_idx != -1 and len(row) > name_col_idx and row[name_col_idx]:
                                name = str(row[name_col_idx]).strip()
                            contacts.append({"phone": phone_val, "name": name})
        else:
            wb = openpyxl.load_workbook(io.BytesIO(contents))
            sheet = wb.active
            
            header_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), None)
            phone_col_idx = 0
            name_col_idx = -1
            
            if header_row:
                for idx, cell in enumerate(header_row):
                    cell_str = str(cell).lower().strip() if cell else ""
                    if cell_str in ["phone", "phone number", "phone_number", "number", "mobile"]:
                        phone_col_idx = idx
                    elif cell_str in ["name", "customer name", "customer_name", "first name", "full name"]:
                        name_col_idx = idx
                        
            for row in sheet.iter_rows(min_row=2 if header_row else 1, values_only=True):
                if row and len(row) > phone_col_idx and row[phone_col_idx]:
                    phone_val = str(row[phone_col_idx]).strip()
                    digits = re.sub(r'\D', '', phone_val)
                    if len(digits) >= 10:
                        name = "Bulk Phone Lead"
                        if name_col_idx != -1 and len(row) > name_col_idx and row[name_col_idx]:
                            name = str(row[name_col_idx]).strip()
                        contacts.append({"phone": phone_val, "name": name})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading Excel file: {str(e)}")
        
    if not contacts:
        raise HTTPException(status_code=400, detail="No phone numbers found in the Excel file.")
        
    if preview_only:
        return {
            "status": "success",
            "message": f"Parsed {len(contacts)} numbers for preview.",
            "contacts": contacts,
            "count": len(contacts)
        }
        
    background_tasks.add_task(process_bulk_calls, contacts, campaign_language, ai_voice, voice_gender, regional_accent, current_user["company_id"])
    
    return {
        "status": "success",
        "message": f"Successfully initiated bulk calls for {len(contacts)} numbers.",
        "contacts": contacts,
        "count": len(contacts)
    }

@app.post("/api/v1/calls/trigger-campaigns")
async def trigger_campaign_calls(
    background_tasks: BackgroundTasks,
    payload: dict = Body(...),
    current_user: dict = Depends(require_company_access)
):
    campaign_ids = payload.get("campaign_ids", [])
    if not campaign_ids:
        raise HTTPException(status_code=400, detail="No campaigns selected")
        
    db = mongodb.get_db()
    contacts = []
    
    leads = await db.leads.find({
        "campaign_id": {"$in": campaign_ids},
        "company_id": current_user["company_id"],
        "status": "New"
    }).to_list(length=1000)
    
    for lead in leads:
        if lead.get("phone"):
            contacts.append({
                "lead_id": lead.get("lead_id"),
                "phone": lead.get("phone"),
                "name": lead.get("name", "Lead"),
                "campaign_id": lead.get("campaign_id")
            })
            
    if not contacts:
        raise HTTPException(status_code=400, detail="No new leads found in selected campaigns.")
        
    campaign_language = "English"
    ai_voice = "Default"
    voice_gender = "Female"
    regional_accent = "Default"
    
    background_tasks.add_task(process_bulk_calls, contacts, campaign_language, ai_voice, voice_gender, regional_accent, current_user["company_id"])
    
    # Mark them as Contacted/Initiating so they aren't triggered again
    await db.leads.update_many(
        {"_id": {"$in": [l["_id"] for l in leads]}},
        {"$set": {"status": "Contacted", "lastContact": datetime.utcnow()}}
    )
    
    return {
        "status": "success",
        "message": f"Successfully initiated calls for {len(contacts)} leads.",
        "count": len(contacts)
    }

@app.post("/api/v1/calls/send-email")
async def send_email(payload: dict = Body(...), current_user: dict = Depends(require_company_access)):
    to_email = payload.get("to")
    subject = payload.get("subject")
    body = payload.get("body")
    
    if not to_email:
        raise HTTPException(status_code=400, detail="Missing 'to' email address.")
        
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    
    if smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject or "Message from Talkly AI"
            msg.attach(MIMEText(body or "", 'plain'))
            
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            return {"status": "success", "message": "Email sent successfully via SMTP."}
        except Exception as e:
            print(f"SMTP Error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    else:
        print(f"--- Simulating Email Send (SMTP config missing) ---")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body Snippet: {str(body)[:100]}...")
        print(f"-----------------------------")
        
        # Simulate network delay
        await asyncio.sleep(1.5)
        
        return {"status": "success", "message": "Email simulated (Configure SMTP_USER & SMTP_PASS in .env to send real emails)."}


async def sync_lead_status_from_call(db, lead_id: str, analysis_result: dict):
    if not analysis_result:
        return
    lead_temperature = analysis_result.get("lead_temperature")
    if lead_temperature in ["Hot", "Warm"]:
        lead_status = "Interested" if lead_temperature == "Warm" else "Qualified"
    elif analysis_result.get("conversion_probability", 0) > 80:
        lead_status = "Converted"
    else:
        lead_status = "Contacted"
        
    update_data = {
        "status": lead_status,
        "aiScore": analysis_result.get("lead_score", 0),
        "lastContact": datetime.utcnow().isoformat()
    }
    
    # Extract property and location if available
    reqs = analysis_result.get("property_requirements", {})
    if isinstance(reqs, dict):
        if reqs.get("propertyType") or reqs.get("property_type"):
            update_data["property"] = reqs.get("propertyType") or reqs.get("property_type")
        if reqs.get("location"):
            update_data["location"] = reqs.get("location")

    await db.leads.update_one(
        {"lead_id": lead_id},
        {"$set": update_data}
    )

async def poll_bolna_execution(execution_id: str, lead_id: str, api_key: str):
    """
    Polls Bolna API for transcript updates in case webhooks fail.
    """
    db = mongodb.get_db()
    url = f"https://api.bolna.ai/executions/{execution_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    log_msg = f"Starting polling fallback for Execution {execution_id} (Lead: {lead_id})"
    print(log_msg)
    with open("bolna_polling.log", "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} - {log_msg}\n")
    
    # Poll for up to 10 minutes
    for i in range(300): 
        try:
            await asyncio.sleep(2)
            # Use run_in_threadpool for blocking requests.get
            response = await run_in_threadpool(requests.get, url, headers=headers, timeout=15)
            
            if response.ok:
                # Force UTF-8 decoding for Hindi/International characters
                response.encoding = 'utf-8'
                data = response.json()
                transcript = data.get("transcript") or ""
                status = data.get("status", "Active")
                
                with open("bolna_polling.log", "a") as f:
                    f.write(f"{datetime.utcnow().isoformat()} - Poll {i}: Status={status}, TranscriptLen={len(transcript)}\n")

                update_data = {
                    "last_poll_at": datetime.utcnow().isoformat() + "Z"
                }
                if transcript:
                    update_data["transcript"] = transcript
                    
                if status.lower() in ["completed", "finished", "ended"]:
                    print(f"Polling: Call {lead_id} completed. Triggering analysis...")
                    
                    # Fetch company_id and duration for billing
                    call_doc = await db.calls.find_one({"call_id": lead_id})
                    if call_doc and call_doc.get("company_id"):
                        duration = data.get("duration") or data.get("telephony_data", {}).get("duration") or 60
                        await billing_service.process_call_billing(
                            db, lead_id, call_doc["company_id"], call_doc.get("direction", "outbound"), duration
                        )
                    
                    analysis_result = await run_in_threadpool(analyze_transcript_text, transcript)
                    if analysis_result:
                        update_data.update({
                            "status": "Analyzed",
                            "summary": analysis_result.get("summary"),
                            "sentiment": analysis_result.get("sentiment"),
                            "duration_seconds": duration if 'duration' in locals() else 60,
                            "analysis": analysis_result
                        })
                        await sync_lead_status_from_call(db, lead_id, analysis_result)
                    else:
                        update_data["status"] = "Completed"
                    
                    await db.calls.update_one({"call_id": lead_id}, {"$set": update_data})
                    break # Stop polling
                elif status.lower() in ["failed", "canceled", "error", "no-answer", "busy", "timeout", "rejected"]:
                    update_data["status"] = "Failed"
                    await db.calls.update_one({"call_id": lead_id}, {"$set": update_data})
                    break # Stop polling
                else:
                    update_data["status"] = "Active"
                    await db.calls.update_one({"call_id": lead_id}, {"$set": update_data})
            else:
                with open("bolna_polling.log", "a") as f:
                    f.write(f"{datetime.utcnow().isoformat()} - Poll {i}: API Error {response.status_code}\n")
                    
        except Exception as e:
            err_msg = f"Polling error for {lead_id}: {str(e)}"
            print(err_msg)
            with open("bolna_polling.log", "a") as f:
                f.write(f"{datetime.utcnow().isoformat()} - {err_msg}\n")
    
    print(f"Finished polling fallback for {lead_id}")

@app.post("/webhooks/bolna")
async def bolna_webhook(data: dict = Body(...)):
    db = mongodb.get_db()
    
    # Save to log file
    with open("bolna_webhook.log", "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} - {json.dumps(data)}\n")
        
    print(f"WEBHOOK RECEIVED FROM BOLNA: {json.dumps(data)[:300]}...")
    
    user_data = data.get("user_data") or {}
    if isinstance(user_data, str):
        try: user_data = json.loads(user_data)
        except: user_data = {}
            
    lead_id = user_data.get("lead_id") or data.get("lead_id") or data.get("call_id")
    transcript = data.get("transcript") or data.get("conversation_history") or data.get("telephony_data", {}).get("transcript", "")
    status = data.get("status", "Active")
    
    if not lead_id:
        phone = data.get("recipient_phone_number") or data.get("telephony_data", {}).get("to_number")
        if phone:
            phone_clean = phone.replace('+', '').strip()
            potential_call = await db.calls.find_one({
                "customer_id": {"$regex": f"{phone_clean}$"}, 
                "status": {"$in": ["Initiating", "Active"]}
            })
            if potential_call:
                lead_id = potential_call["call_id"]
                
        # If STILL no lead_id, it's a completely new inbound call!
        if not lead_id:
            customer_phone = data.get("telephony_data", {}).get("from_number") or data.get("caller_phone_number") or "Unknown Inbound"
            lead_id = data.get("call_id") or data.get("execution_id") or f"inbound_{int(time.time()*1000)}"
            
            # Resolve company_id from the Bolna agent that handled the call.
            inbound_company_id = None
            agent_id = data.get("agent_id") or data.get("telephony_data", {}).get("agent_id")
            if agent_id:
                mapping = await db.language_mappings.find_one({"bolna_agent_id": agent_id})
                if mapping and mapping.get("company_id"):
                    inbound_company_id = mapping.get("company_id")
                if not inbound_company_id:
                    company = await db.companies.find_one({"bolna_agent_id": agent_id})
                    if company:
                        inbound_company_id = company.get("company_id")
            if not inbound_company_id:
                # Unattributable inbound call - keep it but flag it for an admin.
                inbound_company_id = os.environ.get("UNATTRIBUTED_INBOUND_COMPANY_ID") or "unassigned"
                print(f"WARNING: inbound call {lead_id} could not be attributed to a company (agent_id={agent_id})")

            await db.calls.insert_one({
                "call_id": lead_id,
                "customer_id": customer_phone,
                "customer_name": "Inbound Caller",
                "direction": "inbound",
                "transcript": "",
                "status": "Active",
                "created_at": datetime.utcnow(),
                "language": "Detecting...",
                "detected_language": "Unknown",
                "preferred_language": "Unknown",
                "transcript_language": "Unknown",
                "company_id": inbound_company_id
            })
            print(f"Created new INBOUND lead record: {lead_id} from {customer_phone}")

    if lead_id:
        update_data = {
            "transcript": transcript,
            "last_webhook_at": datetime.utcnow().isoformat() + "Z"
        }
        
        if status.lower() in ["completed", "finished", "ended"]:
            print(f"Call {lead_id} completed. Triggering AI Analysis...")
            
            # Fetch company_id and duration for billing
            call_doc = await db.calls.find_one({"call_id": lead_id})
            if call_doc and call_doc.get("company_id"):
                duration = data.get("telephony_data", {}).get("duration") or data.get("duration") or 60
                await billing_service.process_call_billing(
                    db, lead_id, call_doc["company_id"], call_doc.get("direction", "outbound"), duration
                )
                
            try:
                analysis_result = await run_in_threadpool(analyze_transcript_text, transcript)
                if analysis_result:
                    detected = analysis_result.get("detected_language") or analysis_result.get("language_detected") or "English"
                    update_data.update({
                        "status": "Analyzed",
                        "summary": analysis_result.get("summary"),
                        "sentiment": analysis_result.get("sentiment"),
                        "duration_seconds": duration if 'duration' in locals() else 60,
                        "language": detected,
                        "detected_language": detected,
                        "preferred_language": analysis_result.get("preferred_language") or detected,
                        "transcript_language": analysis_result.get("transcript_language") or detected,
                        "analysis": analysis_result
                    })
                    await sync_lead_status_from_call(db, lead_id, analysis_result)
                else:
                    update_data["status"] = "Completed"
            except Exception as e:
                print(f"Analysis failed for {lead_id}: {str(e)}")
                update_data["status"] = "Completed"
        elif status.lower() in ["failed", "canceled", "error", "no-answer", "busy", "timeout", "rejected"]:
            update_data["status"] = "Failed"
        else:
            update_data["status"] = "Active"

        await db.calls.update_one({"call_id": lead_id}, {"$set": update_data})
    return {"status": "success"}

@app.post("/api/v1/process-audio")
async def process_audio_api(
    file: UploadFile = File(...), 
    agent_name: str = Form("AI Agent"),
    employee_id: str = Form(None),
    employee_email: str = Form(None),
    current_user: dict = Depends(require_company_access)
):
    temp_path = None
    try:
        timestamp = int(time.time() * 1000)
        temp_path = f"temp_{timestamp}_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        result = await run_in_threadpool(process_uploaded_audio, temp_path)
        now = datetime.utcnow()
        unique_call_id = f"call_{timestamp}"
        doc = {
            "call_id": unique_call_id,
            "customer_id": result.get("analysis", {}).get("customer_name") or "Phone Lead",
            "customer_name": result.get("analysis", {}).get("customer_name") or "Phone Lead",
            "direction": "outbound",
            "agent_name": agent_name,
            "employee_id": employee_id,
            "employee_email": employee_email,
            "sentiment": str(result.get("sentiment", "neutral")).lower(),
            "summary": result.get("summary"),
            "transcript": result.get("transcript"),
            "analysis": result.get("analysis", {}),
            "created_at": now,
            "status": "Analyzed",
            "company_id": current_user["company_id"],
            "source": "voice_intelligence"
        }
        db = mongodb.get_db()
        await db.calls.insert_one(doc)
        doc["_id"] = None
        if temp_path and os.path.exists(temp_path): os.remove(temp_path)
        return doc
    except Exception as e:
        print(f"ERROR PROCESSING AUDIO: {str(e)}")
        if temp_path and os.path.exists(temp_path): os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/voice-intelligence/history")
async def get_voice_intelligence_history(limit: int = 20, skip: int = 0, current_user: dict = Depends(require_company_access)):
    db = mongodb.get_db()
    cursor = db.calls.find({
        "company_id": current_user["company_id"], 
        "$or": [
            {"source": "voice_intelligence"},
            {"status": "Analyzed", "duration_seconds": {"$exists": False}, "customer_name": "Phone Lead"}
        ]
    }).sort("created_at", -1).skip(skip).limit(limit)
    
    history = []
    async for d in cursor:
        d["_id"] = None
        history.append(d)
    return {"status": "success", "data": history}

@app.get("/download/{report_type}")
async def download_report(report_type: str):
    if report_type == "excel":
        from process_audio import get_weekly_excel_file
        file_path = get_weekly_excel_file()
        # Fallback to absolute path if needed
        full_path = os.path.join(BASE_DIR, file_path) if not os.path.isabs(file_path) else file_path
        if os.path.exists(full_path):
            return FileResponse(full_path, filename=os.path.basename(full_path))
        
        # Fallback to cumulative report if weekly doesn't exist
        fallback_path = os.path.join(BASE_DIR, "results", "analytics_results.xlsx")
        if os.path.exists(fallback_path):
            return FileResponse(fallback_path, filename="analytics_results.xlsx")
            
        return {"status": "error", "message": "Report not found"}
    # Mock download for demo
    return {"status": "success", "message": f"{report_type} report ready"}

# --- Phase 3 CRM & Follow-Up Endpoints ---

from services.crm_service import crm_service

async def _get_owned_call(db, call_id: str, current_user: dict):
    doc = await db.calls.find_one(tenant_filter(current_user, {"call_id": call_id}))
    if not doc:
        raise HTTPException(status_code=404, detail="Call not found")
    return doc


@app.post("/api/v1/calls/{call_id}/sync-crm")
async def sync_call_to_crm(call_id: str, current_user: dict = Depends(require_company_access)):
    try:
        db = mongodb.get_db()
        await _get_owned_call(db, call_id, current_user)
        await crm_service.sync_call_to_crm(db, call_id)
        return {"status": "success", "message": "Successfully synced to CRM."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/calls/{call_id}/send-followup")
async def send_followup_email(call_id: str, current_user: dict = Depends(require_company_access)):
    # Simulates sending an email
    try:
        db = mongodb.get_db()
        await _get_owned_call(db, call_id, current_user)
        import asyncio
        await asyncio.sleep(1) # Simulate network delay

        # Mark email as sent in DB (scoped to this company)
        await db.calls.update_one(
            tenant_filter(current_user, {"call_id": call_id}),
            {"$set": {
                "followup_sent": True,
                "followup_sent_at": datetime.utcnow().isoformat()
            }}
        )
        return {"status": "success", "message": "Email sent successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    # Using 'server:app' as a string is required for multi-worker setup or reload
    uvicorn.run("server:app", host="0.0.0.0", port=8002, reload=True)


