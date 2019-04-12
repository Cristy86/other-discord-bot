import discord
from discord.ext import commands

import asyncio
import traceback
from discord.ext.commands.cooldowns import BucketType

import aiohttp
import platform

import os
import unicodedata

import time
import random

from datetime import datetime
import psutil
from pyfiglet import figlet_format
from utils.constants import OTHER_ERROR_EMOJI, BLOCKED, LOADING_EMOJI

bot_version = "0.3.5"

async def is_blocked():
    def predicate(ctx):
        return ctx.author.id not in BLOCKED
        # a function that takes ctx as it's only arg, that returns a truethy or falsey value, or raises an exception
    return commands.check(predicate)   

class Fun(commands.Cog):
    """Fun commands for the bot."""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def cookie(self, ctx, user: discord.Member):
        """Gives a cookie to a user."""
        if ctx.author.id in BLOCKED:
            return
        if ctx.author.bot:
            return
        
        if user == ctx.author:
            return await ctx.send("<a:TickRed:466641000782364692> **`You can't give a cookie yourself.`**")

        await ctx.trigger_typing()

        await ctx.send(f"**`{user.display_name}, you've been given a cookie by {ctx.author.display_name}.`** :cookie:")


    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def ping(self, ctx):
        """Returns with pong."""
        if ctx.author.id in BLOCKED:
            return
        if ctx.author.bot:
            return
        
        t_1 = time.perf_counter()
        await ctx.trigger_typing() 

        t_2 = time.perf_counter()
        time_delta = round((t_2-t_1)*1000)  

        await ctx.send(f"**`Pong.`** :ping_pong:\n\n:white_small_square: **`Time: {time_delta}ms.`**\n\n:white_small_square: **`Websocket latency: {round(self.bot.latency * 1000)}ms.`**")
    
    
    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def roulette(self, ctx, *, text: str):
        """Chooses a user at roulette."""
        if ctx.author.id in BLOCKED:
            return
        if ctx.author.bot:
            return
        
        random_user = random.choice(ctx.guild.members)

        embed = discord.Embed(color=random_user.color.value)
        embed.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
        embed.description = f"The winner of **{text}** is: **{random_user.name}**!\n**`{random_user.id} BOT: {random_user.bot}`**"
        embed.set_image(url=random_user.avatar_url)
        embed.set_footer(text=f"{self.bot.user.name}")
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)

    @commands.command(pass_context=True, aliases=['lc'])
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def lovecalc(self, ctx, user: discord.Member, user2: discord.Member):
        '''Calculates the love of a user and other user.'''
        if ctx.author.id in BLOCKED:
            return
        if ctx.author.bot:
            return
        
        if user == ctx.author and user2 == ctx.author:
            return await ctx.send(f'<{OTHER_ERROR_EMOJI}> **Find a user for you, not yourself.**')
        
        if user == user and user2 == user:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Please don't even try this.**")

        random.seed((user.id, user2.id))
        percent = random.randint(0, 100)
        result = ""

        if percent > 75:
            result = "**`They are perfect.`** :heartpulse: :heart_exclamation:"
        
        if percent <= 75:
            result = "**`They might become a thing.`** :heart_decoration:"
        
        if percent == 50:
            result = "**`Best friends.`** :four_leaf_clover: :innocent:"
        
        if percent < 50:
            result = "**`Friendzone.`** :four_leaf_clover: :pray:"

        embed = discord.Embed(color=0x000000)
        embed.title = "- - Love calculator - -"
        embed.description = f"**`{user.display_name} + {user2.display_name}`**"
        embed.add_field(name=":white_small_square: Percent", value=f"**`{percent}%`**", inline=False)
        embed.add_field(name=":white_small_square: Result", value=result, inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text=f"{self.bot.user.name}")
        embed.timestamp = datetime.utcnow()

        await ctx.send(embed=embed)

    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def webhook(self, ctx, user:discord.Member=None, *, text: str):
        """Makes an webhook and sends text as an user."""
        if ctx.author.id in BLOCKED:
            return
        if user is None:
            user = ctx.author



        await ctx.message.add_reaction(LOADING_EMOJI)
        content = text
        webhook = await ctx.channel.create_webhook(name=f"{user.name}#{user.discriminator}")
        
        await ctx.message.remove_reaction(LOADING_EMOJI, member=ctx.me)
        await webhook.send(content, avatar_url=user.avatar_url_as(format='png'))
        await webhook.delete()

    @commands.command(name="8ball")
    @commands.guild_only()
    @commands.cooldown(1.0, 30.0, commands.BucketType.user)
    async def _ball(self, ctx, *, question:str):
        """A usual 8ball..."""
        if ctx.author.id in BLOCKED:
            return

        if ctx.author.bot:
            return
        
        results = ["It is certain"," It is decidedly so","Without a doubt","Yes, definitely","You may rely on it","As I see it, yes"," Most likely","Outlook good","Yes","Signs point to yes"," Reply hazy try again","Ask again later","Better not tell you now","Cannot predict now","Concentrate and ask again","Don't count on it","My reply is no","My sources say no","Outlook not so good","Very doubtful"]
        await ctx.send(f"The 🎱 says: **`{random.choice(results)}.`**")



def setup(bot):
    bot.add_cog(Fun(bot))
