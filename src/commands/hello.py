from utils import (
    SlashCommand,
    Option,
    ApplicationCommandOptionType,
)
from core.command import command
from core.embed import EmbedBuilder
import aiohttp
import random
import os

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

        await self.defer_response(interaction_data, ephemeral=False)
        
        user_id = interaction_data["data"]["options"][0]["value"]
        
        async with aiohttp.ClientSession() as session:
            search_term = "hello wave"
    
            tenor_key = os.getenv("TENOR_API_KEY")
            url = f"https://tenor.googleapis.com/v2/search?q={search_term}&key={tenor_key}&limit=10"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get("results", [])
                    if results:
                        gif = random.choice(results)
                        gif_url = gif["media_formats"]["gif"]["url"]
                        
                        embed = EmbedBuilder()
                        embed.set_title(f"Hello <@!{user_id}>! 👋")
                        embed.set_image(url=gif_url)
                        embed.set_color(0x2b2d31)
                        
                        return await self.edit_response(
                            interaction_data,
                            embeds=[embed.to_dict()]
                        )

        return await self.edit_response(
            interaction_data,
            content=f"Hello <@!{user_id}> 👋"
        )