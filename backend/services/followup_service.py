import os
import requests
import json

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENAI_MODEL = "gpt-4o"
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")

FOLLOWUP_PROMPT = """
You are an expert sales representative. Based on the following call summary, action items, and key objections, write a highly professional, personalized follow-up email to the customer.

Return your response ONLY as a JSON object with two keys: "subject" and "body".

Call Data:
{data}
"""

class FollowUpService:
    def generate_followup_draft(self, call_data: dict) -> dict:
        """
        Generates a follow-up email draft based on call analysis.
        Returns {"subject": "...", "body": "..."}
        """
        # Prepare context for the prompt
        analysis = call_data.get("analysis", {})
        context = {
            "summary": call_data.get("summary", ""),
            "action_items": analysis.get("action_items", []),
            "objections": analysis.get("key_objections", []),
            "customer_name": call_data.get("customer_name", "Customer")
        }
        
        prompt = FOLLOWUP_PROMPT.format(data=json.dumps(context, indent=2))

        # Try OpenAI first
        if OPENAI_API_KEY:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": OPENAI_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                }
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                if response.ok:
                    content = response.json()["choices"][0]["message"]["content"]
                    return json.loads(content)
            except Exception as e:
                print(f"FollowUp Generation OpenAI Error: {e}")

        # Fallback to OpenRouter
        if OPENROUTER_API_KEY:
            try:
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
                payload = {
                    "model": OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                }
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                if response.ok:
                    content = response.json()["choices"][0]["message"]["content"]
                    return json.loads(content)
            except Exception as e:
                print(f"FollowUp Generation OpenRouter Error: {e}")

        # Ultimate fallback
        offering_text = context.get("offering") or "our discussion"
        return {
            "subject": "Following up on our conversation",
            "body": f"Hi {context['customer_name']},\n\nThank you for taking the time to speak with me today. I wanted to follow up on our discussion regarding {offering_text}.\n\nPlease let me know if you have any further questions.\n\nBest regards,\nAgent"
        }

followup_service = FollowUpService()
