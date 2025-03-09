from os import getenv
from dotenv import load_dotenv

load_dotenv()

class bot:
    token = getenv("TEST")
    default_prefix = "s."
    cogs = [
        "admin",
        "ai",
        "autoresponder",
        "dev",
        "events",
        "gif_commands",
        "fun_tools",
        "help",
        "image_tools",
        "lovecalc",
        "minecraft",
        "music",
        "text_tools",
        "tools"
    ]
    
    support_invite = "YOUR_DISCORD_INVITE_LINK"

class database:
    token = getenv("DB_CONFIG")
    db_name = "homie"

class api:
    gif_api = getenv("TENOR_API")
    weather = getenv("WEATHER_API")
    gemini = getenv("GEMINI")
    groq = getenv("GROQ")
    remove_bg = getenv("REMOVE_BG")
    image = getenv("IMAGE")

class lavalink:
    nodes = [
        {
            "host" : getenv("LAVALINK_HOST"),
            "port" :  getenv("LAVALINK_PORT"),
            "auth" : getenv("LAVALINK_AUTH"),
        }
    ]

class emoji:

    bot_ping = "<:bot_ping:1267199109027201147>"
    db_ping = "<:db_ping:1267199058913660929>"
    lavalink_ping = "<:lava_ping:1270432997069291561>"
    music_filter = "<:music:1270434659750117416>"
    arrow = "<:new_arrow:1276772471252586639>"
    developer = "<:developer:1288934616480219226>"

    play = "<:play:1271214161187180635>"
    skip = "<:skip:1271214157127225397>"
    stop = "<:stop:1271214153473855559>"
    lyrics = "<:lyrics:1287530305472696414>"
    filters = "<:filters:1290029915873349706>"
    like = "<:filters:1290029915873349706>"

    cog_admin = "<:admin:1262364323666202714>"
    cog_ai = "<:ai:1262364370474897489>"
    cog_autoresponder = "<:ai:1262364370474897489>"
    cog_fun_tools = "<:fun_tools:1255550320478781471>"
    cog_gif_commands = "<:gif:1254019441503633408>"
    cog_help = "<:help:1262364412497498164>"
    cog_image_tools = "<:image_tool:1254019503659028581>"
    cog_lovecalc = "<:love_calc:1254019519878402080>"
    cog_minecraft = "<:Minecraft:1277279364316139601>"
    cog_music = "<:music:1270434659750117416>"
    cog_text_tools = "<:text_tool:1254019510533623850>"
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
