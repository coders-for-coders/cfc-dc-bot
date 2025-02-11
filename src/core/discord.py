from typing import Dict, Any, Optional
from core.http import HTTPClient
import os
import logging

logger = logging.getLogger(__name__)

class DiscordClient(HTTPClient):
    def __init__(self):
        super().__init__(
            base_url="https://discord.com/api/v10/",
            headers={
                "Authorization": f"Bot {os.getenv('DISCORD_TOKEN')}",
                "Content-Type": "application/json",
            }
        )

    async def create_interaction_response(
        self,
        interaction_id: str,
        interaction_token: str,
        payload: Dict[str, Any]
    ) -> bool:
        """Send an initial response to an interaction
        
        Must be sent within 3 seconds of receiving the interaction.
        Returns True if successful (204 status), False otherwise.
        """
        try:
            status, _ = await self.post(
                f"interactions/{interaction_id}/{interaction_token}/callback",
                json=payload,
                expected_type="text/html"  # Discord returns 204 with empty response
            )
            return status == 204
        except Exception as e:
            logger.error(f"Failed to send interaction response: {e}")
            return False

    async def get_original_response(
        self,
        application_id: str,
        interaction_token: str
    ) -> Optional[Dict[str, Any]]:
        """Get the initial interaction response"""
        try:
            status, response = await self.get(
                f"webhooks/{application_id}/{interaction_token}/messages/@original"
            )
            return response if status == 200 else None
        except Exception as e:
            logger.error(f"Failed to get original response: {e}")
            return None

    async def edit_original_response(
        self,
        application_id: str,
        interaction_token: str,
        payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Edit the original interaction response
        
        Can only be used after sending an initial response.
        Token is valid for 15 minutes.
        """
        try:
            status, response = await self.patch(
                f"webhooks/{application_id}/{interaction_token}/messages/@original",
                json=payload
            )
            if status != 200:
                logger.error(f"Failed to edit response: status {status}")
                return None
            return response
        except Exception as e:
            logger.error(f"Failed to edit response: {e}")
            return None

    async def delete_original_response(
        self,
        application_id: str,
        interaction_token: str
    ) -> bool:
        """Delete the initial interaction response"""
        try:
            status, _ = await self.delete(
                f"webhooks/{application_id}/{interaction_token}/messages/@original"
            )
            return status == 204
        except Exception as e:
            logger.error(f"Failed to delete original response: {e}")
            return False

    async def create_followup_message(
        self,
        application_id: str,
        interaction_token: str,
        payload: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Send a followup message to an interaction
        
        Limited to 5 followup messages per interaction for user-installed apps not in server.
        The thread_id, avatar_url, and username parameters are not supported.
        """
        try:
            status, response = await self.post(
                f"webhooks/{application_id}/{interaction_token}",
                json=payload
            )
            return response if status == 200 else None
        except Exception as e:
            logger.error(f"Failed to send followup message: {e}")
            return None