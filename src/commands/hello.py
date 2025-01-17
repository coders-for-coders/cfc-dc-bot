from utils import (
    SlashCommand,
    Option,
    InteractionResponseFlags,
    InteractionResponseType,
    ApplicationCommandOptionType,
)
from core.command import command, create_response

@command(
    name="hello",
    description="Say hello to someone",
    options=[
        Option(
            name="user",
            type=ApplicationCommandOptionType.USER,
            description="The user to say hello",
            required=True,
        ),
    ],
)
class HelloCommand(SlashCommand):
    async def respond(self, interaction_data: dict):
        # Defer the response first
        await self.defer_response(interaction_data, ephemeral=True)
        
        user_id = interaction_data["data"]["options"][0]["value"]
        
        # Edit the deferred response
        return await self.edit_response(
            interaction_data,
            content=f"Hello <@!{user_id}>"
        )
