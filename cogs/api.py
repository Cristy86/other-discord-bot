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
from utils.constants import GREY_EMBED, OTHER_ERROR_EMOJI, BLOCKED, BLACK_EMBED
import praw

class API:
    """API Commands for the bot."""

    def __init__(self, bot):
        self.bot = bot
        self.reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),
                     client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                     user_agent=os.getenv('REDDIT_USER_AGENT'))

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def do_meme(self):
        memes_submissions = self.reddit.subreddit('memes').hot()
        post_to_pick = random.randint(1, 100)
        for i in range(0, post_to_pick):
            submission = next(x for x in memes_submissions if not x.stickied)
        return submission.url

    def do_softwaregore(self):
        softwaregore_submissions = self.reddit.subreddit('softwaregore').hot()
        post_to_pick = random.randint(1, 100)
        for i in range(0, post_to_pick):
            submission = next(x for x in softwaregore_submissions if not x.stickied)
        return submission.url

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 30.0, commands.BucketType.user)
    async def tinyurl(self, ctx, *, url: str):
        """Generates a tinyurl."""
        if ctx.author.id in BLOCKED:
            return

        if ctx.author.bot:
            return

        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://tinyurl.com/api-create.php', params={'url': f"{url}"}) as resp:
                    shorturl = await resp.text()
                    await ctx.send(f'<{shorturl}>')
        except:
            await ctx.send(f"<{OTHER_ERROR_EMOJI}> **`{url}` is invalid. Please enter a valid URL.**")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 30.0, commands.BucketType.user)
    async def osu(self, ctx, user: str, hex: int = None):
        """Generates an osu player."""
        if ctx.author.id in BLOCKED:
            return
        if hex is None:
		hex = "4b4c4f"

        embed = discord.Embed(color=0x000000)
        embed.set_image(url=f"http://lemmmy.pw/osusig/sig.php?colour=hex{hex}&uname={user}&pp=1&countryrank&removeavmargin&flagshadow&flagstroke&darktriangles&onlineindicator=undefined&xpbar&xpbarhex")
        embed.set_footer(text=f"{self.bot.user.name}")
        embed.timestamp = datetime.utcnow()

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def dadjoke(self, ctx):
        """Sends a dad joke."""
        if ctx.author.id in BLOCKED:
            return
        if ctx.author.bot:
            return

        try:

            headers = {"Accept": "application/json"}

            async with aiohttp.ClientSession() as session:
                async with session.get('https://icanhazdadjoke.com', headers=headers) as get:
                    resp = await get.json()
                    await ctx.send(f"**`{resp['joke']}`**")
        except Exception as e:
            await ctx.send(f"<{OTHER_ERROR_EMOJI}> **The API might be unavailable now.**\n\n```py\n{type(e).__name__}: {str(e)}\n```")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 30.0, commands.BucketType.user)
    async def ask(self, ctx, *, question: str):
        """Uses cleverbot.io to talk with you."""
        if ctx.author.id in BLOCKED:
            return

        params = {
			"user": os.getenv('API_USER'),
			"key": os.getenv('API_KEY'),
			"nick": os.getenv('API_NICK'),
			"text": question
		}
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.post("https://cleverbot.io/1.0/ask", data=params) as conversation:
                    data = await conversation.json()
                    result = data["response"]
                    await ctx.send(f"💬 | **`{result}`** | {ctx.author.mention}")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 30.0, commands.BucketType.user)
    async def dog(self, ctx):
        """Generates a random image dog."""
        if ctx.author.id in BLOCKED:
            return
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://random.dog/woof.json') as r:
                    res = await r.json()
                    embed = discord.Embed(color=0x000000)
                    embed.title = "Aww. I like dogs. :dog:"
                    embed.set_image(url=res['url'])
                    embed.set_footer(text=f"{self.bot.user.name}")
                    embed.timestamp = datetime.utcnow()
                    await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"<{OTHER_ERROR_EMOJI}> **The API might be unavailable now.**\n\n```py\n{type(e).__name__}: {str(e)}\n```")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 30.0, commands.BucketType.user)
    async def cat(self, ctx):
        """Generates a random image cat."""
        if ctx.author.id in BLOCKED:
            return
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('http://aws.random.cat/meow') as r:
                    res = await r.json()
                    embed = discord.Embed(color=0x000000)
                    embed.title = "Aww. I like cats. :cat:"
                    embed.set_image(url=res['file'])
                    embed.set_footer(text=f"{self.bot.user.name}")
                    embed.timestamp = datetime.utcnow()
                    await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"<{OTHER_ERROR_EMOJI}> **The API might be unavailable now.**\n\n```py\n{type(e).__name__}: {str(e)}\n```")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def bird(self, ctx):
        """Generates a random image bird."""
        if ctx.author.id in BLOCKED:
            return
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('http://random.birb.pw/tweet/') as resp:
                    _url = (await resp.read()).decode("utf-8")
                    url = f"http://random.birb.pw/img/{str(_url)}"
                    embed = discord.Embed(color=0x000000)
                    embed.title = "Aww. I like birds. :bird:"
                    embed.set_image(url=url)
                    embed.set_footer(text=f"{self.bot.user.name}")
                    embed.timestamp = datetime.utcnow()
                    await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"<{OTHER_ERROR_EMOJI}> **The API might be unavailable now.**\n\n```py\n{type(e).__name__}: {str(e)}\n```")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 30.0, commands.BucketType.user)
    async def shibe(self, ctx):
        """Generates a random image shibe."""
        if ctx.author.id in BLOCKED:
            return
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('http://shibe.online/api/shibes?count=[1]&urls=[true/false]&httpsUrls=[true/false]') as r:
                    res = await r.json()
                    embed = discord.Embed(color=0x000000)
                    embed.title = "Aww. I like shibes. :dog:"
                    embed.set_image(url=str(res).strip("[']"))
                    embed.set_footer(text=f"{self.bot.user.name}")
                    embed.timestamp = datetime.utcnow()
                    await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"<{OTHER_ERROR_EMOJI}> **The API might be unavailable now.**\n\n```py\n{type(e).__name__}: {str(e)}\n```")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 30.0, commands.BucketType.user)
    async def fox(self, ctx):
        """Generates a random image fox."""
        if ctx.author.id in BLOCKED:
            return
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://randomfox.ca/floof/') as r:
                    res = await r.json()
                    embed = discord.Embed(color=0x000000)
                    embed.title = "Aww. I like foxes. :fox:"
                    embed.set_image(url=res['image'])
                    embed.set_footer(text=f"{self.bot.user.name}")
                    embed.timestamp = datetime.utcnow()
                    await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"<{OTHER_ERROR_EMOJI}> **The API might be unavailable now.**\n\n```py\n{type(e).__name__}: {str(e)}\n```")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def hastebin(self, ctx, *, text:str):
        """Uploads text to Hastebin."""
        if ctx.author.id in BLOCKED:
            return
        text = self.cleanup_code(text)
        async with aiohttp.ClientSession() as session:
            async with session.post("https://hastebin.com/documents",data=text.encode('utf-8')) as post:
                post = await post.json()
                await ctx.send(f"<https://hastebin.com/{post['key']}>")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def mystbin(self, ctx, *, text:str):
        """Uploads text to mystb.in."""
        if ctx.author.id in BLOCKED:
            return
        text = self.cleanup_code(text)
        async with aiohttp.ClientSession() as session:
            async with session.post("http://mystb.in/documents",data=text.encode('utf-8')) as post:
                post = await post.json()
                await ctx.send(f"<http://mystb.in/{post['key']}>")

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 10.0, commands.BucketType.user)
    async def meme(self, ctx):
        """Generates a random r/memes from reddit."""
        if ctx.author.id in BLOCKED:
            return
        try:
            async with ctx.typing():
                b = await self.bot.loop.run_in_executor(None, self.do_meme)
                embed = discord.Embed(color=BLACK_EMBED)
                embed.set_image(url=b)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.message.add_reaction(OTHER_ERROR_EMOJI)
            await ctx.send(f'```py\n{type(e).__name__}: {str(e)}\n```')


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 10.0, commands.BucketType.user)
    async def softwaregore(self, ctx):
        """Generates a random r/softwaregore from reddit."""
        if ctx.author.id in BLOCKED:
            return
        try:
            async with ctx.typing():
                b = await self.bot.loop.run_in_executor(None, self.do_softwaregore)
                embed = discord.Embed(color=BLACK_EMBED)
                embed.set_image(url=b)
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.message.add_reaction(OTHER_ERROR_EMOJI)
            await ctx.send(f'```py\n{type(e).__name__}: {str(e)}\n```')

def setup(bot):
    bot.add_cog(API(bot))
