from enum import Enum
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class InteractionType:
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class InteractionResponseType:
    PONG = 1  # ACK a Ping
    CHANNEL_MESSAGE_WITH_SOURCE = 4  # respond with a message
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5  # ACK and show loading state
    DEFERRED_UPDATE_MESSAGE = 6  # ACK and edit response later
    UPDATE_MESSAGE = 7  # edit the message
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8  # respond with autocomplete choices
    MODAL = 9  # respond with a modal
    PREMIUM_REQUIRED = 10  # respond indicating premium is required


class InteractionResponseFlags:
    EPHEMERAL = 1 << 6


class ApplicationCommandOptionType(Enum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8


class Option:
    def __init__(
        self,
        name: str,
        type: ApplicationCommandOptionType,
        description: str = "...",
        required: bool = False,
        options: list = None,
    ):
        self.name = name
        self.description = description
        self.type = type
        self.required = required
        self.options = options or []

    def to_dict(self):
        result = {
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "required": self.required,
        }
        if self.options:
            result["options"] = [option.to_dict() for option in self.options]
        return result


class SlashCommand:
    name: str
    description: str
    options: list

    def __init__(self):
        self.options = []
        self._deferred = False
        self._discord = None

    async def _get_discord(self):
        """Get or create Discord client"""
        if not self._discord:
            from core.discord import DiscordClient
            self._discord = DiscordClient()
        return self._discord

    async def _cleanup(self):
        """Cleanup Discord client"""
        if self._discord:
            await self._discord.close()
            self._discord = None

    async def defer_response(self, interaction_data: dict, ephemeral: bool = False) -> bool:
        """Defer the response to show a loading state"""
        try:
            discord = await self._get_discord()
            
            success = await discord.create_interaction_response(
                interaction_data["id"],
                interaction_data["token"],
                {
                    "type": InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"flags": InteractionResponseFlags.EPHEMERAL} if ephemeral else {}
                }
            )
            
            if success:
                self._deferred = True
            return success
            
        except Exception as e:
            logger.error(f"Failed to defer response: {e}")
            return False

    async def edit_response(self, interaction_data: dict, **kwargs) -> Optional[Dict[str, Any]]:
        """Edit the original response"""
        if not self._deferred:
            return None
            
        try:
            discord = await self._get_discord()
            
            # Convert kwargs to a proper payload
            payload = {}
            if "content" in kwargs:
                payload["content"] = kwargs["content"]
            if "embeds" in kwargs:
                payload["embeds"] = kwargs["embeds"]
            if "components" in kwargs:
                payload["components"] = kwargs["components"]
            if "flags" in kwargs:
                payload["flags"] = kwargs["flags"]
            if "allowed_mentions" in kwargs:
                payload["allowed_mentions"] = kwargs["allowed_mentions"]
                
            return await discord.edit_original_response(
                interaction_data["application_id"],
                interaction_data["token"],
                payload
            )
        except Exception as e:
            logger.error(f"Failed to edit response: {e}")
            return None
        finally:
            await self._cleanup()

    async def respond(self, interaction_data: dict):
        """Override this method to handle the command response"""
        return create_response(
            type=InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            content="Command not implemented",
            ephemeral=True
        )

    def to_dict(self):
        return {
            "type": 1,  # Slash command
            "name": self.name,
            "description": self.description,
            "options": [option.to_dict() for option in self.options],
        }
