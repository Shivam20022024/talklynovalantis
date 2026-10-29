import os
import uuid
import datetime
from typing import Optional, Dict, Any
from livekit import api

class LiveKitService:
    """
    Manages LiveKit room tokens and real-time voice sessions for TalklyAI.
    """

    @staticmethod
    def get_credentials(company_doc: Optional[dict] = None) -> Dict[str, str]:
        """
        Retrieves LiveKit credentials, prioritizing company-level config,
        then falling back to server environment variables.
        """
        livekit_cfg = (company_doc or {}).get("livekit_config") or {}

        url = (
            livekit_cfg.get("url")
            or os.environ.get("LIVEKIT_URL", "")
        ).strip()

        api_key = (
            livekit_cfg.get("api_key")
            or os.environ.get("LIVEKIT_API_KEY", "")
        ).strip()

        api_secret = (
            livekit_cfg.get("api_secret")
            or os.environ.get("LIVEKIT_API_SECRET", "")
        ).strip()

        return {
            "url": url,
            "api_key": api_key,
            "api_secret": api_secret
        }

    @staticmethod
    def generate_token(
        room_name: str,
        participant_identity: str,
        participant_name: str,
        api_key: str,
        api_secret: str,
        ttl_minutes: int = 60
    ) -> str:
        """
        Generates a secure WebRTC JWT token for joining a LiveKit audio room.
        """
        token = (
            api.AccessToken(api_key, api_secret)
            .with_identity(participant_identity)
            .with_name(participant_name)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True
                )
            )
            .with_ttl(datetime.timedelta(minutes=ttl_minutes))
        )
        return token.to_jwt()

livekit_service = LiveKitService()
