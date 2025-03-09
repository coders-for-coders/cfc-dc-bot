import discord
from discord.ext import commands
from core.cog import Cog
from core.bot import MyBot
import config
from discord.ui import Select, View
from typing import Optional
import os
import sys
import time

class Help(Cog):
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.emoji = config.emoji.cog_help


class HelpSelect(Select):
    def __init__(self, bot:commands.Bot):
        super().__init__(
            placeholder= "Choose a category",
            options=[
                discord.SelectOption(
                    label=cog_name, description= cog.description, emoji= cog.emoji
                    
                ) for cog_name, cog in bot.cogs.items() if cog.__cog_commands__ and cog_name not in ["Dev"]
                
            ]
        )      
        
        self.bot=bot
        
    global get_emoji
    
    def get_emoji (cog: commands.Cog): 
    
        input= cog.emoji.split(":")
        list = []
        for i in input:
            list.append(i)

        
        input = str(list[2])
        list=[]
        for char in input :
            if char.isdigit():
                list.append(char)
                
                
        output = int("".join(list))
        
        link = f"https://cdn.discordapp.com/emojis/{output}.png?=1"
        return link

    async def callback(self, interaction: discord.Interaction) -> None:
        cog = self.bot.get_cog(self.values[0])
        
        
        #this is for getting the emoji url for embed thumbnail

        try: 
            link = get_emoji(cog)
        except:
            link = self.bot.user.avatar.url
                
        assert cog 
        #global commands_mixer
        commands_mixer = []
        for i in cog.walk_commands():
            commands_mixer.append(i)
            
        for i in cog.walk_app_commands():
            commands_mixer.append(i)
            

        global prefix
        prefix = await self.bot.db["prefix"].find_one({"guild_id": interaction.guild.id})
        prefix = prefix["prefix"]
        
        if prefix == None:
            prefix = config.bot.default_prefix
         
        embed= discord.Embed(color=config.color.no_color)

        embed.title= f"{cog.__cog_name__} commands"


        embed.description= "\n".join(
            f"**{prefix}{command.name}**: `{command.description}`\n" for command in commands_mixer
            
        )
                
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user.name}", icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=link)
        await interaction.response.edit_message(embed=embed)
            
            

class Help(commands.Cog):
    def __init__(self, bot:MyBot):
        self.bot = bot
        self.emoji = config.emoji.cog_help
        
        
    @commands.hybrid_command(name= "help", description="Shows the command list")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def help(self, ctx: commands.Context, command : Optional[str]):
        
        #global prefix
        prefix = await self.bot.db["prefix"].find_one({"guild_id": ctx.guild.id})
        prefix = prefix["prefix"]
        if prefix == None:
            prefix = config.bot.default_prefix
        if not command:
            embed= discord.Embed(
                title= f"**{self.bot.user.name}'s help desk**",
                description= f"**Prefix:** `{prefix}` \n Hello, thanks for using Homie bot.\n Please select the category to see the available commands\n",
                color= config.color.no_color
            )
            
            embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url)
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
            embed.set_thumbnail(url=self.bot.user.avatar.url)

            view = View().add_item(HelpSelect(self.bot))
            await ctx.send (embed=embed, view= view)
            
            return        
            
        try:
            cmd = self.bot.get_command(command)
            cog = cmd.cog
        except:
            return await ctx.send(embed=discord.Embed(title="Error", description=f"`{{{command}}}` doesn't exist", colour=discord.Color.random()))
            
 
        embed = discord.Embed()
        embed.title = cmd.name
        embed.colour = discord.Colour.random()
        try:
            embed.set_thumbnail(url= get_emoji(cog))
        except:
            pass
        
        if cmd.aliases:
            alias = f"Aliases: {cmd.aliases}\n"
        else:
            alias = ""

        param = str(cmd.params)
        
        param = param.split("'")
        
        args = []
        for i in param:
            
            args.append(i)

        for i in args:
            
            if "{" or "<" in i:
                args.pop(args.index(i))

        args_str = "} {".join(args)
        

        embed.description = f"**{cmd.description}**\n {alias} \n**Example:**\n `{prefix}{cmd.name} {{{args_str}}}`"
        await ctx.send(embed=embed)


    @commands.hybrid_command(name= "mail", description = "Send us a message")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def mail(self, ctx:commands.Context,*, message: str):

        msg_log_channel = self.bot.get_channel(config.loging_channels.mail)

        embed = discord.Embed()
        embed.title = ctx.author.display_name
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.color=config.color.no_color
        embed.add_field(name="User Mention:", value = ctx.author.mention, inline= False)
        embed.add_field(name="User Name:", value = ctx.author.name, inline= False)
        embed.add_field(name="ID:", value = ctx.author.id, inline= False)


        if not isinstance(ctx.channel, discord.channel.DMChannel):
            
            embed.add_field(name="Guild Name:", value = ctx.guild.name, inline = False)
            embed.add_field(name="Guild ID:", value = ctx.guild.id, inline= False)
        
        embed.description = f"**Message:** {message}"

        await msg_log_channel.send(embed=embed)


        resp_embed = discord.Embed()
        resp_embed.color=config.color.no_color
        resp_embed.title = "Your message has been recieved"
        resp_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        resp_embed.description = f"{config.emoji.arrow} **We will reply you shortly**\n{config.emoji.arrow} **MSG:** {message} "
        await ctx.reply(embed=resp_embed)



    @commands.command(name="botinfo", aliases = [ "developer", "bot_info", "info"])
    async def botinfo(self, ctx: commands.Context):

        embed = discord.Embed(color=config.color.no_color)
        embed.set_author(icon_url=self.bot.user.avatar.url, name="Bot Info")

        bot_info = f"> **Bot Tag:** {self.bot.user.name}\n> **Bot Mention:** {self.bot.user.mention}\n"
        uptime = f"> **Uptime:** <t:{int(self.bot.uptime)}:R>\n"
        stats = f"> **Servers:** {len(self.bot.guilds)}\n> **Users:** {len(self.bot.users)}\n"
        os_info = f"> **Operating System:** {os.name}\n> **Code Language:** Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]} \n> **Discord.py:** {discord.__version__}\n"
        dev_info = f"{config.emoji.developer} Created by: [Mainak](https://discord.com/users/510002835140771842)\n\n{config.emoji.arrow} Use `mail` command if you want to send us a message"

        embed.description = bot_info + uptime + stats + os_info + dev_info
        await ctx.send(embed=embed)
