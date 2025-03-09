import discord
from discord.ext import commands
from core.cog import Cog
from core.bot import MyBot
import config
import time
import psutil
import os
import sys
import speedtest

class Dev(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
     

    #dev command for command sync
    @commands.command(hidden=True)
    @commands.is_owner()
    async def sync(self, ctx:commands.Context):
        
        await self.bot.tree.sync()
        await ctx.send("Synced Globally")
        
    
    #dev command for stats
    @commands.command(hidden=True)
    @commands.is_owner()
    async def stats(self, ctx:commands.Context):
        
        #stats
        total_memory = psutil.virtual_memory().total >> 20
        used_memory = psutil.virtual_memory().used >> 20
        cpu_used = str(psutil.cpu_percent())
        total_members = sum(i.member_count for i in self.bot.guilds)
        cached_members = len(self.bot.users)
        
        
        #embed properties
        embed = discord.Embed(description=None)
        embed.title = F"**__{self.bot.user.display_name}__**"
        embed.colour = discord.Color.red()
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        
        arrow=config.emoji.arrow
        
        guild_value = len(self.bot.guilds)
        embed.add_field(name="Servers", value=f"**[Total** {arrow} {guild_value}**]**")
        embed.add_field(name="Members", value=f"**[Total** {arrow} {total_members}**]** \n **[Cached** {arrow} {cached_members}**]** ")
        embed.add_field(
            name="Stats",
            value=f"**[Ping** {arrow} {round(self.bot.latency * 1000, 2)}ms]",
        )
        embed.add_field(name="System", value=f"**[RAM** {arrow} {used_memory} / {total_memory} MB**]** \n **[CPU used** {arrow} {cpu_used}%**]**"),
        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar.url)        
        await ctx.send(embed=embed) 


    @commands.command()
    @commands.is_owner()
    async def invite(self, ctx: commands.Context, guild_id: int):

        try:
            guild = self.bot.get_guild(guild_id)

            invite = await guild.text_channels[0].create_invite(max_uses=1)
            
            await ctx.send(invite)
            
        except Exception as e:
            await ctx.send(e)


    @commands.command(aliases=["np"])
    @commands.is_owner()
    #@commands.cooldown(1, 5, commands.BucketType.user)
    async def noprefix(self, ctx: commands.Context, user: discord.User):

        np_user = await self.bot.db["np"].find_one({"uid" : user.id})

        embed = discord.Embed()
        embed.color=config.color.no_color

        if np_user:
            embed.description = f"🔴 {user.mention} is already in No prefix"
            return await ctx.send(embed=embed)

        await self.bot.db["np"].insert_one(document={
            "user" : "user",
              "uid": user.id
              })
        
        embed.description = f"🟢 {user.mention} has been added to the No prefix list"
        
        await ctx.send(embed=embed)


    @commands.command(aliases = ["nplist"])
    @commands.is_owner()
    async def np_list(self, ctx: commands.Context):

        np_list = await self.bot.db["np"].find({}).to_list()
 
        users = []
        n = 1
        for uid in np_list:
            try:
                user = self.bot.get_user(uid['uid'])
                users.append(f"{n}. {user.mention}")
            except:
                users.append(f"{n}. `{uid['uid']}`")

            n = n+1

        embed = discord.Embed()
        embed.color=config.color.no_color
        embed.description = "\n".join(users)

        await ctx.send(embed=embed)


    @commands.command(aliases = ["npdel"])
    @commands.is_owner()
    async def npdelete(self, ctx: commands.Context, user: discord.User):

        np_user = await self.bot.db["np"].find_one({"uid" : user.id})

        embed = discord.Embed()
        embed.color=config.color.no_color

        if not np_user:
            embed.description = f"🔴 {user.mention} is not in No prefix list"
            return await ctx.send(embed=embed)
        
        await self.bot.db["np"].delete_one({"uid" : user.id})
        embed.description = f"🟢 {user.mention} has been removed from No prefix"
        await ctx.send(embed=embed)
        

    
    @commands.command(name="vps_speed")
    @commands.is_owner()
    async def vps_speed(self, ctx: commands.Context):

        embed = discord.Embed(color=config.color.no_color)
        embed.description = "⌛ Please wait...."

        msg: discord.Message = await ctx.send(embed=embed)
        test = speedtest.Speedtest()

        download = test.download()
        upload = test.upload()

        download = round(download / 10**6, 1)
        upload = round(upload / 10**6, 1)

        if download >= 1024:
            dl_speed = f"{(download / 1024)} GBPS"

        else:
            dl_speed = f"{download} MBPS"

        if upload >= 1024:
            ul_speed = f"{(upload / 1024)} GBPS"

        else:
            ul_speed = f"{upload} MBPS"

        new_embed = discord.Embed(color=config.color.no_color)

        new_embed.description = f"> **Download:** {dl_speed}\n> **Upload:** {ul_speed}"

        await msg.edit(embed=new_embed)