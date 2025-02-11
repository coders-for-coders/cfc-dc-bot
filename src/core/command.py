from typing import List, Optional, Type, Dict, Any
from utils.constants import SlashCommand, InteractionResponseType, InteractionResponseFlags

class CommandRegistry:
    def __init__(self):
        self._commands = {}

    def register(self, command: SlashCommand) -> SlashCommand:
        """Register a command with the registry"""
        self._commands[command.name] = command
        return command

    def get_command(self, name: str) -> Optional[SlashCommand]:
        """Get a command by name"""
        return self._commands.get(name)

    def all_commands(self) -> List[SlashCommand]:
        """Get all registered commands"""
        return list(self._commands.values())

    def clear(self):
        """Clear all registered commands"""
        self._commands.clear()

# Global registry instance
registry = CommandRegistry()

def command(name: str, description: str = "...", options: list = None):
    """Decorator to register a command with the command registry
    
    Args:
        name: The name of the command
        description: The description of the command
        options: List of command options
    """
    def decorator(cls: Type[SlashCommand]) -> Type[SlashCommand]:
        if not issubclass(cls, SlashCommand):
            raise TypeError(f"Command class must inherit from SlashCommand, got {cls}")
            
        cmd = cls()
        cmd.name = name
        cmd.description = description
        cmd.options = options or []
        registry.register(cmd)
        return cls
    return decorator

def create_response(
    type: int,
    content: Optional[str] = None,
    embeds: Optional[list] = None,
    ephemeral: bool = False,
    components: Optional[list] = None,
) -> Dict[str, Any]:
    """Create a standardized interaction response
    
    Args:
        type: InteractionResponseType
        content: Message content
        embeds: List of embeds
        ephemeral: Whether the message should be ephemeral
        components: Message components (buttons, selects, etc)
    """
    data = {}
    
    if content is not None:
        data["content"] = content
        
    if embeds is not None:
        data["embeds"] = embeds
        
    if components is not None:
        data["components"] = components
        
    if ephemeral:
        data["flags"] = InteractionResponseFlags.EPHEMERAL
        
    return {
        "type": type,
        "data": data
    }

async def send_deferred_response(ephemeral: bool = False):
    """Create a deferred response (shows loading state)"""
    data = {}
    if ephemeral:
        data["flags"] = InteractionResponseFlags.EPHEMERAL
        
    return {
        "type": InteractionResponseType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE,
        "data": data
    }