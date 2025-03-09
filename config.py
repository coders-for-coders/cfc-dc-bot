from os import getenv
from dotenv import load_dotenv

load_dotenv()

class bot:
    token = getenv("DISCORD_TOKEN")
    default_prefix = "c."
    cogs = [
        "admin",
        "ai",
        "dev",
        "error",
        "events",
        "help",
        "tools"
    ]
    
    support_invite = "https://discord.gg/XxH8cSKfae"

class database:
    token = getenv("DB_CONFIG")
    db_name = "cfc-dc-bot"

class api:
    gif_api = getenv("TENOR_API")
    weather = getenv("WEATHER_API")
    gemini = getenv("GEMINI")
    groq = getenv("GROQ")
    remove_bg = getenv("REMOVE_BG")
    image = getenv("IMAGE")


class emoji:

    bot_ping = "<:bot_ping:1267199109027201147>"
    db_ping = "<:db_ping:1267199058913660929>"
    music_filter = "<:music:1270434659750117416>"
    arrow = "<:new_arrow:1276772471252586639>"
    developer = "<:developer:1288934616480219226>"

    cog_admin = "<:admin:1262364323666202714>"
    cog_ai = "<:ai:1262364370474897489>"
    cog_help = "<:help:1262364412497498164>"
    cog_tools = "<:tool:1254019437854588999>" 

class loging_channels:
    join = 1206246727116521504
    leave = 1206246727116521506
    mail = 1206246727116521505
    count = 1206246727116521507
    error_log = 1338082375761920053

class color:
    no_color = 0x2c2c34

class images:
    weather_thumbnail = ""
