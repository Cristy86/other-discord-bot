
from discord.ext import commands
from .cmds import bot_version
from utils.SimplePaginator import SimplePaginator
from utils.paginator import HelpPaginator, CannotPaginate
import discord

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
import pkg_resources

import json
from utils.constants import OTHER_ERROR_EMOJI, OTHER_SUCCESS_EMOJI, MAYBE_EMOJI, BOT_OWNER_ID, BLOCKED

class CodeBlock:
    missing_error = f'<{OTHER_ERROR_EMOJI}> **`Missing code block. Please use the following markdown`**\n\\`\\`\\`language\ncode here\n\\`\\`\\`'
    def __init__(self, argument):
        try:
            block, code = argument.split('\n', 1)
        except ValueError:
            raise commands.BadArgument(self.missing_error)

        if not block.startswith('```') and not code.endswith('```'):
            raise commands.BadArgument(self.missing_error)

        language = block[3:]
        self.command = self.get_command_from_language(language.lower())
        self.source = code.rstrip('`')

    def get_command_from_language(self, language):
        cmds = {
            'cpp': 'g++ -std=c++1z -O2 -Wall -Wextra -pedantic -pthread main.cpp -lstdc++fs && ./a.out',
            'c': 'mv main.cpp main.c && gcc -std=c11 -O2 -Wall -Wextra -pedantic main.c && ./a.out',
            'py': 'python main.cpp', # coliru has no python3
            'python': 'python main.cpp',
            'haskell': 'runhaskell main.cpp'
        }

        cpp = cmds['cpp']
        for alias in ('cc', 'h', 'c++', 'h++', 'hpp'):
            cmds[alias] = cpp
        try:
            return cmds[language]
        except KeyError as e:
            if language:
                fmt = f'Unknown language to compile for: {language}'
            else:
                fmt = 'Could not find a language to compile with.'
            raise commands.BadArgument(fmt) from e

class Information(commands.Cog):
    """Some commands that shows some information about something."""

    def __init__(self, bot):
        self.bot = bot
        self.bot.process = psutil.Process()
        self.x = ['+','-','*','/','**','%']

    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    @commands.guild_only()
    @commands.command()
    async def coliru(self, ctx, *, code: CodeBlock):
        """Compiles code via Coliru.

        You have to pass in a code block with the language syntax
        either set to one of these:
        - cpp
        - c
        - python
        - py
        - haskell

        Anything else isn't supported. The C++ compiler uses g++ -std=c++14.

        The python support is only python2.7 (unfortunately).

        Credits: R. Danny made by Danny#0007
        https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/lounge.py#L53-L97
        """
        if ctx.author.id in BLOCKED:
            return


        payload = {
            'cmd': code.command,
            'src': code.source
        }

        data = json.dumps(payload)

        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.post('http://coliru.stacked-crooked.com/compile', data=data) as resp:
                    if resp.status != 200:
                        await ctx.send(f'<{OTHER_ERROR_EMOJI}> **`Coliru did not respond in time.`**')
                        return

                    output = await resp.text(encoding='utf-8')

                    if len(output) < 1992:
                        await ctx.send(f'```\n{output}\n```')
                        return

                # output is too big so post it in gist
                    async with ctx.session.post('http://coliru.stacked-crooked.com/share', data=data) as r:
                        if r.status != 200:
                            await ctx.send(F'<{OTHER_ERROR_EMOJI}> **`Could not create coliru shared link.`**')
                        else:
                            shared_id = await r.text()
                            await ctx.send(f'<{MAYBE_EMOJI}> **`Output too big. Coliru link:`** <http://coliru.stacked-crooked.com/a/{shared_id}>')

    @coliru.error
    async def coliru_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(error)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(CodeBlock.missing_error)

    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(name="invite")
    async def _invite(self, ctx):
        """Gives you an invite."""
        if ctx.author.id in BLOCKED:
            return

        perms = discord.Permissions.none()
        perms.administrator = True
        await ctx.send(f'<{discord.utils.oauth_url(self.bot.user.id, perms)}>\n\n**`You can also uncheck the permissions but some commands are not gonna work without permissions.`**')

    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    @commands.command(name='help')
    async def _help(self, ctx, *, command: str = None):
        """Shows help about a command or the bot."""
        if ctx.author.id in BLOCKED:
            return

        if ctx.author.bot:
            return

        try:
            if command is None:
                p = await HelpPaginator.from_bot(ctx)
            else:
                entity = self.bot.get_cog(command) or self.bot.get_command(command)

                if entity is None:
                    clean = command.replace('@', '@\u200b')
                    return await ctx.send(f'<{OTHER_ERROR_EMOJI}> **`Command or category "{clean}" not found.`**')
                elif isinstance(entity, commands.Command):
                    p = await HelpPaginator.from_command(ctx, entity)
                else:
                    p = await HelpPaginator.from_cog(ctx, entity)

            await p.paginate()
        except Exception as e:
            await ctx.send(f"<{OTHER_ERROR_EMOJI}> **`{e}`**")

    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def userinfo(self, ctx, user: discord.Member = None):
        """Shows information about a user."""
        if ctx.author.id in BLOCKED:
            return

        try:
            user = user or ctx.author
            game = user.activity or None

            if game is None:
                game = game
                large_image_game = "https://cdn.discordapp.com/attachments/447662555993866243/464021387481317376/unknown.png"
                small_image_game = "https://cdn.discordapp.com/attachments/447662555993866243/464021387481317376/unknown.png"
                large_image_text_game = "None"
                small_image_text_game = "None"
            else:
                game = game
                large_image_game = game.large_image_url
                small_image_game = game.small_image_url
                large_image_text_game = game.large_image_text
                small_image_text_game = game.small_image_text

            perms = '\n'.join(perm for perm, value in user.guild_permissions if value)
            days = datetime.utcnow() - user.created_at

            days2 = datetime.utcnow() - user.joined_at

            embed = discord.Embed(color=user.color.value)
            embed.title = f"`- - {user} - -`"
            embed.description = f":white_small_square: **Joined at:** **{user.joined_at.strftime('%a %b %d %Y at %I:%M %p')} [`{days2.days} Days.`]**\n:white_small_square: **Status:** **`{user.status}`**\n:white_small_square: **Top Role:** **`{user.top_role.name}`**\n:white_small_square: **Roles:** {','.join([role.name for role in user.roles])}\n:white_small_square: **Playing:** **`{game}`**\n:white_small_square: **Is bot:** **`{user.bot if user.bot else 'False'}`**\n:white_small_square: **ID:** **`{user.id}`**\n:white_small_square: **Created at:** **{user.created_at.strftime('%a %b %d %Y at %I:%M %p')} [`{days.days} Days.`]**"
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_footer(text=f"{self.bot.user.name} - Page 1/3")
            embed.timestamp = datetime.utcnow()

            embed2 = discord.Embed(color=user.color.value)
            embed2.title = f"`- - {user}'s permissions - -`"
            embed2.description = f"`{perms}`"
            embed2.set_footer(text=f"{self.bot.user.name} - Page 2/3")

            embed3 = discord.Embed(color=user.color.value)
            embed3.title = f"`- - {user}'s game image - -`"
            embed3.description = f"`Using {small_image_text_game}`\n`{large_image_text_game}`"
            embed3.set_image(url=large_image_game)
            embed3.set_footer(text=f"{self.bot.user.name} - Page 3/3")
            embed3.set_thumbnail(url=small_image_game)

            await SimplePaginator(extras=[embed, embed2, embed3]).paginate(ctx)
        except:
            user = user or ctx.author
            game = user.activity

            perms = '\n'.join(perm for perm, value in user.guild_permissions if value)
            days = datetime.utcnow() - user.created_at

            days2 = datetime.utcnow() - user.joined_at

            embed = discord.Embed(color=user.color.value)
            embed.title = f"`- - {user} - -`"
            embed.description = f":white_small_square: **Joined at:** **{user.joined_at.strftime('%a %b %d %Y at %I:%M %p')} [`{days2.days} Days.`]**\n:white_small_square: **Status:** **`{user.status}`**\n:white_small_square: **Top Role:** **`{user.top_role.name}`**\n:white_small_square: **Roles:** {','.join([role.name for role in user.roles])}\n:white_small_square: **Playing:** **`{game}`**\n:white_small_square: **Is bot:** **`{user.bot if user.bot else 'False'}`**\n:white_small_square: **ID:** **`{user.id}`**\n:white_small_square: **Created at:** **{user.created_at.strftime('%a %b %d %Y at %I:%M %p')} [`{days.days} Days.`]**"
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_footer(text=f"{self.bot.user.name} - Page 1/2")
            embed.timestamp = datetime.utcnow()

            embed2 = discord.Embed(color=user.color.value)
            embed2.title = f"`- - {user}'s permissions - -`"
            embed2.description = f"`{perms}`"
            embed2.set_footer(text=f"{self.bot.user.name} - Page 2/2")

            await SimplePaginator(extras=[embed, embed2]).paginate(ctx)


    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def serverinfo(self, ctx):
        """Shows information about this server."""
        if ctx.author.id in BLOCKED:
            return

        embed = discord.Embed(color=0x000000)
        embed.title = "- - Server Information - -"
        embed.description = f":white_small_square: **Name:** **`{ctx.guild.name}`**\n:white_small_square: **ID:** **`{ctx.guild.id}`**\n:white_small_square: **Member count:** **`{len(ctx.guild.members)}`**\n:white_small_square: **Region:** **`{ctx.guild.region}`**\n:white_small_square: **Created at:** **{ctx.guild.created_at.strftime('%a %b %d %Y at %I:%M %p')}**"
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f"{self.bot.user.name}")
        embed.timestamp = datetime.utcnow()

        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def finduser(self, ctx, userID: int):
        """Finds a user with an ID."""
        if ctx.author.id in BLOCKED:
            return

        if ctx.author.bot:
            return

        if len(str(userID)) < 17:
            return await ctx.send("<:WrongMark:449572838915964928> **That's not a userID.**")

        user = await self.bot.get_user_info(userID)
        embed = discord.Embed(color=0x000000)
        embed.title = f"{user}"
        embed.description = f":white_small_square: **User ID:** **`{userID}`**\n\n:white_small_square:**Created at:** **`{user.created_at.strftime('%a %b %m %Y at %I:%M %p %Z')}`**"
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f"{self.bot.user.name}")
        embed.timestamp = datetime.utcnow()

        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def char(self, ctx, *, characters):
        """Shows information about an char."""
        if ctx.author.id in BLOCKED:
            return


        def to_string(c):
            name = unicodedata.name(c, 'Name not found.')
            return f'**`\\N{{{name}}}`**: - {c}'
        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send(f'<{OTHER_ERROR_EMOJI}> **Output too long to display.**')
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Information(bot))
