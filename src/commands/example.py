import asyncio
from core.command import command, create_response
from utils.constants import SlashCommand, InteractionResponseType
from core.embed import EmbedBuilder

@command(name="long", description="A command that takes a while")
class LongCommand(SlashCommand):
    async def respond(self, interaction_data):
        # Show loading state
        await self.defer_response(interaction_data, ephemeral=True)
        
        # Do some long operation...
        await asyncio.sleep(5)
        
        # Create an embed for the response
        embed = EmbedBuilder()
        embed.set_title("Long Operation Complete!")
        embed.set_description("Thanks for waiting!")
        
        # Edit the deferred response
        return await self.edit_response(
            interaction_data,
            content="Operation completed!",
            embeds=[embed.to_dict()]
        ) 