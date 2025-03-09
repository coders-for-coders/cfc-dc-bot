import discord
from discord.ext import commands
import config
import asyncio
import time
from typing import Callable, Coroutine, List
import wavelink
from motor.motor_asyncio import AsyncIOMotorClient
import logging


startup_task: List[Callable[["MyBot"], Coroutine]] = []

class MyBot(commands.Bot):
    """Custom class inherited from commands.Bot"""

    def __init__(self, **kwargs):
        super().__init__(
            command_prefix = get_prefix,
            intents = discord.Intents.all(),
            **kwargs
            )
        
        self.uptime = None
        self.nodes: List[wavelink.Node] = []
        self.setup_logger()
        self.help_command = None

    def boot(self):

        try:
            self.logger.info("Bot is booting....")
            super().run(token=config.bot.token)

        except Exception as e:
            self.logger.error("Bot shutting down....")
            self.logger.error(f"An error occurred: {e}\n")

    def setup_logger(self):
        self.logger = logging.getLogger(" ")
        self.logger.setLevel(logging.INFO)
        
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "{asctime} {levelname:<8} {name} {message}", dt_fmt, style="{"
        )

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        for logger_name in ('asyncio', 'wavelink', 'discord.voice_state'):
            logging.getLogger(logger_name).setLevel(logging.CRITICAL)



    async def setup_hook(self):
        self.uptime = time.time()
        await asyncio.gather(*(task(self) for task in startup_task))

    global get_prefix
    async def get_prefix(self, message: discord.Message):

        prefixes = [config.bot.default_prefix]

        no_prefix = await self.db["np"].find_one({"uid" : message.author.id})
        guild_prefix = await self.db["prefix"].find_one({"guild_id" : message.guild.id})

        if guild_prefix:
            prefixes.append(guild_prefix["prefix"])

        if no_prefix:
            prefixes.append("")

        return commands.when_mentioned_or(*prefixes)(self, message)
    
    @startup_task.append
    async def setup_db(self):
        try:
            self.db = AsyncIOMotorClient(config.database.token)[config.database.db_name]
            self.logger.info("Connected to database")

        except Exception as e:
            self.logger.error("Failed to load database")
            self.logger.error(e)

    @startup_task.append
    async def setup_cogs(self):
        for cog in config.bot.cogs:
            try:
                await self.load_extension(f"cogs.{cog}")
                self.logger.info(f"Loaded {cog}")
            except Exception as e:
                self.logger.error(f"Failed to load: {cog}")
                self.logger.error(e)
        self.logger.info("Loaded all cogs")


    @startup_task.append
    async def setup_wavelink(self):
        # await asyncio.sleep(5)
        
        for i, node in enumerate(config.lavalink.nodes, start=1):
            uri = "ws://{}:{}".format(node.get("host"), node.get("port"))

            node_config = wavelink.Node(
                identifier= f"Node {i}",
                uri=uri,
                password=node.get("auth"),
                client=self,
                retries=3
            )
            
            try:
                await wavelink.Pool.connect(client=self, nodes=[node_config])
                self.nodes.append(node_config)
                self.logger.info(f"Connected to {node_config.identifier}")
            except Exception as e:
                self.logger.error(f"Failed to connect to node {i}: {e}")