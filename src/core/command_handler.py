from typing import Optional, Dict, Any
from .command import registry
from .discord import DiscordClient
import logging

logger = logging.getLogger(__name__)

class CommandHandler:
    def __init__(self, interaction_data: Dict[str, Any]):
        self.interaction_data = interaction_data
        self.command_data = interaction_data.get("data", {})
        self.command_name = self.command_data.get("name")
        self.options = self.command_data.get("options", [])
        self.discord = DiscordClient()

    async def execute(self) -> Optional[Dict[str, Any]]:
        """Execute the command and return the response"""
        if not self.command_name:
            logger.warning("No command name found in interaction data")
            return None
            
        command = registry.get_command(self.command_name)
        if command is None:
            logger.warning(f"Command not found: {self.command_name}")
            return None
            
        try:
            # Get the command response
            response = await command.respond(self.interaction_data)
            
            # For deferred responses, the command will handle its own response
            if command._deferred:
                return None
                
            # Send the initial response
            if not await self.discord.create_interaction_response(
                self.interaction_data["id"],
                self.interaction_data["token"],
                response
            ):
                logger.error("Failed to send interaction response")
                return None
                
            return None  # Return None since we've handled the response
            
        except Exception as e:
            logger.error(f"Error executing command {self.command_name}: {e}", exc_info=True)
            return None
        finally:
            await self.discord.close()
