import os
import mongodb
from .session_manager import create_inbound_session

async def handle_incoming_call(form_data: dict) -> str:
    """
    Handles the raw incoming webhook from a telephony provider (e.g., Twilio).
    Logs the session and returns TwiML to forward the call to the Bolna agent.
    """
    call_sid = form_data.get("CallSid")
    from_number = form_data.get("From", "Unknown")
    
    # Create the session in the DB
    await create_inbound_session(from_number, call_sid)
    
    # Extract company_id based on To number (webhook routing logic)
    to_number = form_data.get("To", "")
    
    # Normalize phone number (strip spaces, ensure + prefix)
    to_number_normalized = to_number.strip().replace(" ", "")
    if to_number_normalized and not to_number_normalized.startswith("+"):
        to_number_normalized = "+" + to_number_normalized
        
    db = mongodb.get_db()
    
    # Example mapping: find company by the Twilio phone number
    agent_sip_uri = os.getenv("BOLNA_SIP_URI", "sip:agent@bolna.ai")
    
    if to_number_normalized:
        phone_doc = await db.phone_numbers.find_one({"phone_number": to_number_normalized})
        if phone_doc:
            if phone_doc.get("inbound_mode") == "forward_human" and phone_doc.get("fallback_number"):
                fallback = phone_doc["fallback_number"]
                return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Dial>{fallback}</Dial>
</Response>"""
            if phone_doc.get("bolna_sip_uri"):
                agent_sip_uri = phone_doc["bolna_sip_uri"]
            
    # Generate TwiML forwarding to the officially configured Bolna Agent
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Dial>
        <Sip>{agent_sip_uri}</Sip>
    </Dial>
</Response>"""
    return twiml

async def transfer_call(call_id: str, destination_number: str) -> dict:
    """
    Initiates a call transfer using the telephony provider's API.
    """
    # Placeholder for actual Twilio REST API transfer logic
    # client.calls(call_id).update(twiml=f'<Response><Dial>{destination_number}</Dial></Response>')
    
    return {"status": "success", "message": f"Transferred to {destination_number}"}

async def hangup_call(call_id: str) -> dict:
    """
    Hangs up the live call using the telephony provider's API.
    """
    # Placeholder for Twilio REST API hangup
    # client.calls(call_id).update(status='completed')
    
    return {"status": "success", "message": "Call terminated"}
