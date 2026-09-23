import os
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("talkly.bolna")


def _strict_bolna_enabled() -> bool:
    return str(os.environ.get("STRICT_BOLNA_AGENT", "")).strip().lower() in ("1", "true", "yes", "on")


async def resolve_bolna_agent_id(db, company_id: str, language: str = "English") -> str:
    """Resolve the Bolna agent id to use for a company's call.

    Resolution order (strict tenant isolation):
      1. company-specific language mapping (``language_mappings`` with company_id)
      2. ``companies.bolna_agent_id`` (the company's dedicated agent)
      3. env ``BOLNA_AGENT_ID`` fallback - ONLY when ``STRICT_BOLNA_AGENT`` is not
         enabled, and always with a loud warning. Never silently shared in strict mode.
    """
    if not company_id:
        raise ValueError("company_id is required to resolve a Bolna agent")

    mapping = await db.language_mappings.find_one({
        "company_id": company_id,
        "language": {"$regex": f"^{re.escape(language)}$", "$options": "i"},
    })
    if mapping and mapping.get("bolna_agent_id"):
        return mapping["bolna_agent_id"]

    mapping_en = await db.language_mappings.find_one({"company_id": company_id, "language": "English"})
    if mapping_en and mapping_en.get("bolna_agent_id"):
        return mapping_en["bolna_agent_id"]

    company = await db.companies.find_one({"company_id": company_id})
    if company and company.get("bolna_agent_id"):
        return company["bolna_agent_id"]

    if _strict_bolna_enabled():
        raise ValueError(
            f"No Bolna agent configured for company {company_id}. "
            "Set companies.bolna_agent_id or a company language mapping."
        )

    fallback = os.environ.get("BOLNA_AGENT_ID", "").strip()
    logger.warning(
        "Bolna FALLBACK agent used for company %s (no company-specific agent configured)",
        company_id,
    )
    return fallback

class LanguageService:
    """
    Handles language detection, switching logic, and analytics aggregation
    for TalklyAI (Indian Languages).
    """
    
    SUPPORTED_LANGUAGES = [
        "English", "Hindi", "Tamil", "Telugu", "Kannada", 
        "Malayalam", "Bengali", "Marathi", "Gujarati", 
        "Punjabi", "Bhojpuri", "Odia", "Assamese", "Urdu"
    ]

    def detect_language_from_text(self, transcript: str, current_language: str = "English") -> str:
        """
        Uses heuristics or delegates to an LLM (in process_audio.py) to detect language.
        For now, this provides a lightweight fallback mechanism.
        """
        if not transcript:
            return current_language
            
        transcript_lower = transcript.lower()
        
        # Simple heuristic mapping (in reality, relies on OpenRouter/GPT-4o)
        if re.search(r'[\u0900-\u097F]', transcript):
            return "Hindi"  # Devanagari block
        if re.search(r'[\u0B80-\u0BFF]', transcript):
            return "Tamil"
        if re.search(r'[\u0C00-\u0C7F]', transcript):
            return "Telugu"
        if re.search(r'[\u0C80-\u0CFF]', transcript):
            return "Kannada"
        if re.search(r'[\u0D00-\u0D7F]', transcript):
            return "Malayalam"
        if re.search(r'[\u0980-\u09FF]', transcript):
            return "Bengali"
            
        return current_language

    def should_switch_language(self, transcript: str, current_language: str) -> Optional[str]:
        """
        Determines if the customer requested a language switch or if the spoken
        language heavily deviated from the current language.
        """
        detected = self.detect_language_from_text(transcript, current_language)
        if detected != current_language and detected in self.SUPPORTED_LANGUAGES:
            # We detected a switch
            return detected
        return None

    async def get_agent_id_for_language(self, db, language: str, company_id: str = None) -> str:
        """Resolve the Bolna agent id for a company + language.

        Delegates to :func:`resolve_bolna_agent_id` which enforces per-company
        isolation (no shared global agent unless STRICT_BOLNA_AGENT is off).
        """
        return await resolve_bolna_agent_id(db, company_id, language or "English")
