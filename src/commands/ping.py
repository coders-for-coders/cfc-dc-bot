from core.command import command, create_response
from utils.constants import SlashCommand, InteractionResponseType
from core.embed import EmbedBuilder

@command(name="ping", description="Check if the bot is alive")
class PingCommand(SlashCommand):
    async def respond(self, interaction_data):
        embed = EmbedBuilder()
        embed.set_title("Pong! 🏓")
        
        return create_response(
            type=InteractionResponseType.CHANNEL_MESSAGE_WITH_SOURCE,
            embeds=[embed.to_dict()]
        ) 