import discord
from discord.ext import commands
from core.cog import Cog
from core.bot import MyBot
import config
import time

class Events(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot


    @Cog.listener()
    async def on_ready(self):
        self.bot.logger.info(f"Bot is ready as {self.bot.user}")    
        await self.bot.change_presence(activity=discord.CustomActivity(name="Homie is online 🤗"))


    #event for deleteing prefix when bot is removed from the guild
    @Cog.listener()
    async def on_guild_remove(self, guild : discord.Guild):

        try:
            await self.bot.db["prefix"].delete_one({"guild_id": guild.id})
        except:
            pass

            
    # event for afk command
    @Cog.listener()
    async def on_message(self, message: discord.Message):

        #Ignore messages from the bot itself or other bots
        if message.author.bot:
            return

        #Ignoring the command message
        try:
            for prefix in self.bot.command_prefix:

                if f"{prefix}afk" in message.content or f"@<{self.bot.user.id}> afk" in message.content:
                    return
        except:
            pass


        # removing afk when the user is back
        afk_guild = await self.bot.db["afk"].find_one({"uid" : message.author.id})
        
        if afk_guild:
            afk_guild = afk_guild["guild_id"]
            if afk_guild == message.guild.id or afk_guild == 0:
                
                tm = dict(await self.bot.db["afk"].find_one({"uid": message.author.id}))["tm"]

                afk_time = round( time.time() - tm, 0)
                unit = "seconds"


                if afk_time > 24*3600:

                    afk_time = afk_time / (24*3600)
                    unit = "days"

                elif afk_time > 3600 :
                    afk_time = afk_time / 3600
                    unit = "hours"
                
                elif afk_time > 60:
                    afk_time = afk_time / 60
                    unit = "minutes"


                await message.channel.send(f"{message.author.mention} I have removed your afk. You were afk for {int(round(afk_time,0))} {unit} ")
                await self.bot.db["afk"].delete_one({"uid" : message.author.id})
                return

        if message.mentions:

            for user in message.mentions:

                
                afk_guild = await self.bot.db["afk"].find_one({"guild_id" : message.guild.id})

                if afk_guild:
                    afk_guild = afk_guild["guild_id"]

                    if afk_guild == message.guild.id or afk_guild == 0:

                        reason = await self.bot.db["afk"].find_one({"guild_id" : message.guild.id})["reason"]

                        tm = await dict(self.bot.db["afk"].find_one({"uid": user.id}))["tm"]
                        embed = discord.Embed() 
                        

                        embed.title = f"{user.display_name} went AFK <t:{int(tm)}:R>"


                        if reason != " ":
                            embed.description = f"<:r_arrow:1261000870590550176> **Reason:** {reason[:2500]}"
                        else:
                            pass

                        embed.color = config.color.no_color

                        await message.reply(embed=embed)
           
            
    #guild join logs
    @Cog.listener()
    async def on_guild_join(self, guild : discord.Guild):

        embed = discord.Embed()
        embed.title = guild.name
        embed.description = f"**ID:** {guild.id}\n**Name:** {guild.name}\n **Owner:** [`{guild.owner.name}`] [`{guild.owner.id}`]\n **Members:** `{guild.member_count}`"
        embed.color = discord.Colour.green()
        try:
            embed.set_thumbnail(url=guild.icon.url)
        except:
            pass

        channel = self.bot.get_channel(config.loging_channels.join)

        await channel.send(embed=embed)
        count_channel = self.bot.get_channel(config.loging_channels.count)
        await count_channel.send(f"# {len(self.bot.guilds)}")


    #guild leave logs
    
    @Cog.listener()
    async def on_guild_remove(self, guild : discord.Guild):

        embed = discord.Embed()
        embed.title = guild.name
        embed.description = f"**Name:** {guild.name}\n **Owner:** [`{guild.owner.name}`] [`{guild.owner.id}`]\n **Members:** `{guild.member_count}`"
        embed.color = discord.Colour.green()
        try:
            embed.set_thumbnail(url=guild.icon.url)
        except:
            pass

        channel = self.bot.get_channel(config.loging_channels.leave)

        await channel.send(embed=embed)
        count_channel = self.bot.get_channel(config.loging_channels.count)
        await count_channel.send(f"# {len(self.bot.guilds)}")