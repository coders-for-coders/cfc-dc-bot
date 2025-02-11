from core.command import command
from utils.constants import SlashCommand
from core.embed import EmbedBuilder
import time

@command(name="ping", description="Check bot latency and response time")
class PingCommand(SlashCommand):
    async def respond(self, interaction_data):
        # Measure initial response time
        start_time = time.time()
        await self.defer_response(interaction_data, ephemeral=False)
        latency = round((time.time() - start_time) * 1000)

        # Measure websocket heartbeat latency
        ws_latency = round(self.client.latency * 1000) if hasattr(self, 'client') else None
        
        embed = EmbedBuilder()
        embed.set_title("Pong! 🏓")
        embed.set_description(
            f"**API Latency:** `{latency}ms`\n"
        )
        embed.set_color(0x2ecc71 if latency < 200 else 0xe74c3c)  # Green if fast, red if slow
        embed.set_footer(text="Lower latency = faster response times")
        
        return await self.edit_response(
            interaction_data,
            embeds=[embed.to_dict()]
        )