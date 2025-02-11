from core.command import command
from utils.constants import SlashCommand
from core.embed import EmbedBuilder
import psutil
import platform
import time
import datetime

from core.discord import DiscordClient  

async def get_self_info():
    """Get bot user information from Discord API"""
    client = DiscordClient()
    status, response = await client.get("users/@me")
    if status != 200:
        return None
    return response

@command(name="info", description="Get information about the bot")
class InfoCommand(SlashCommand):
    async def respond(self, interaction_data):
        await self.defer_response(interaction_data)

        # Get bot info from Discord
        bot_info = await get_self_info()
        bot_name = bot_info["username"] if bot_info else "Bot"

        # Get system stats
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_used = f"{memory.used / (1024 ** 3):.1f}"
        memory_total = f"{memory.total / (1024 ** 3):.1f}"
        memory_percent = memory.percent
        uptime = time.time() - psutil.boot_time()
        days = int(uptime // (24 * 3600))
        hours = int((uptime % (24 * 3600)) // 3600)
        minutes = int((uptime % 3600) // 60)

        # Get disk usage
        disk = psutil.disk_usage('/')
        disk_used = f"{disk.used / (1024 ** 3):.1f}"
        disk_total = f"{disk.total / (1024 ** 3):.1f}"

        embed = EmbedBuilder()
        embed.set_title(f"{bot_name} Information")
        embed.set_color(0x2b2d31)
        
        description = [
            "**🖥️ System Stats**",
            f"```",
            f"OS      : {platform.system()} {platform.release()}",
            f"CPU     : {cpu_usage}% utilized",
            f"Memory  : {memory_used}GB/{memory_total}GB ({memory_percent}%)",
            f"Storage : {disk_used}GB/{disk_total}GB ({disk.percent}%)",
            f"Uptime  : {days}d {hours}h {minutes}m",
            f"```",
            "",
            "**🔧 Bot Information**",
            f"```",
            f"Version    : v0.0.3",
            f"Started at : {datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}",
            f"Python     : {platform.python_version()}",
            f"```"
        ]
        
        embed.set_description("\n".join(description))
        embed.set_footer(text="⚡ Powered by FastAPI | 🚀 Deployed on Render")
        
        return await self.edit_response(
            interaction_data,
            embeds=[embed.to_dict()]
        )
