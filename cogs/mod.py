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
from utils.constants import OTHER_ERROR_EMOJI, OTHER_SUCCESS_EMOJI, BLOCKED

async def is_blocked():
    def predicate(ctx):
        return ctx.author.id not in BLOCKED
        # a function that takes ctx as it's only arg, that returns a truethy or falsey value, or raises an exception
    return commands.check(predicate)   

class Moderation:
    """Mod-only commands for the bot."""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def clear(self, ctx, num: int, target:discord.Member = None):
        """Clears X messages."""
        if ctx.author.id in BLOCKED:
            return        
        if ctx.author.bot:
            return
        if num>500 or num<0:
            await ctx.send (f"<{OTHER_ERROR_EMOJI}> **Invalid amount. Maximum is `500`.**")
            return
        def msgcheck(amsg):
            if target:
                return amsg.author.id==target.id
            return True
        await ctx.channel.purge(limit=num, check=msgcheck)
        await ctx.send(f'<{OTHER_SUCCESS_EMOJI}> Deleted **{num}** messages for you.', delete_after=10)

    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def kick(self, ctx, user: discord.Member = None, *, reason: str = None):
        """Kicks a member with an reason."""
        if ctx.author.id in BLOCKED:
            return        
        if user is None:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **That's not a user. [example: @User#1111]**")
        if ctx.author.bot:
            return
        if self.bot.owner_id == user.id:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Can't kick the owner of this bot.**")
        if user == ctx.guild.owner:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Can't kick guild owner.**")
        if ctx.me.top_role <= user.top_role:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **My top role is lower or equal to member's top role, can't kick `{user}`.**")
        if ctx.author.top_role <= user.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Your top role is lower or equal to member's/Can't kick `{user}`.**")
        if reason is None:
            reason = 'No reason.'
        
        await ctx.guild.kick(user, reason=reason)
        await ctx.send(f'<{OTHER_SUCCESS_EMOJI}> **Done.**')
        try:
            embed = discord.Embed(color=0x000000)
            embed.title = "Alert System"
            embed.description = f"**`Looks like you got kicked from {ctx.guild.name}`** :boot:"
            embed.add_field(name="`Moderator`", value=f"**`{ctx.author}`**")
            embed.add_field(name="`Reason`", value=f"**`{reason}`**")
            await user.send(embed=embed)
        except discord.Forbidden as e:
            error = await ctx.send(f"<{OTHER_ERROR_EMOJI}> **`Looks like the user blocked me. DM message failed. Deleting this message in 5 seconds.`** ```py\n{type(e).__name__}: {e}\n```")
            await asyncio.sleep(5)
            await error.delete()
            pass
    
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def softban(self, ctx, user: discord.Member = None, *, reason: str = None):
        """Bans a user and then unbans the user.."""
        if ctx.author.id in BLOCKED:
            return
        if user is None:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **That's not a user. [example: @User#1111]**")
        if ctx.author.bot:
            return
        if self.bot.owner_id == user.id:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Can't softban the owner of this bot.**")
        if user == ctx.guild.owner:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Can't softban guild owner.**")
        if ctx.me.top_role <= user.top_role:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **My top role is lower or equal to member's top role, can't softban `{user}`.**")
        if ctx.author.top_role <= user.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Your top role is lower or equal to member's/Can't softban `{user}`.**")
        if reason is None:
            reason = 'No reason.'
        
        await ctx.guild.ban(user, reason=reason)
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f'<{OTHER_SUCCESS_EMOJI}> **Done.**')
        try:
            embed = discord.Embed(color=0x000000)
            embed.title = "Alert System"
            embed.description = f"**`Looks like you got softbanned from {ctx.guild.name}`** <a:BlobBan:466662201835388949>"
            embed.add_field(name="`Moderator`", value=f"**`{ctx.author}`**")
            embed.add_field(name="`Reason`", value=f"**`{reason}`**")
            embed.add_field(name="`What softban means?`", value="**`If you don't know, softban means that bans an user and then unbans the user.`**")
            await user.send(embed=embed)
        except discord.Forbidden as e:
            error = await ctx.send(f"<{OTHER_ERROR_EMOJI}> **`Looks like the user blocked me. DM message failed. Deleting this message in 5 seconds.`** ```py\n{type(e).__name__}: {e}\n```")
            await asyncio.sleep(5)
            await error.delete()
            pass

    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def ban(self, ctx, user: discord.Member = None, *, reason: str = None):
        """Bans an user.."""
        if ctx.author.id in BLOCKED:
            return        
        if user is None:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **That's not a user. [example: @User#1111]**")
        if ctx.author.bot:
            return
        if self.bot.owner_id == user.id:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Can't ban the owner of this bot.**")
        if user == ctx.guild.owner:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Can't ban guild owner.**")
        if ctx.me.top_role <= user.top_role:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **My top role is lower or equal to member's top role, can't ban `{user}`.**")
        if ctx.author.top_role <= user.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Your top role is lower or equal to member's/Can't ban `{user}`.**")
        if reason is None:
            reason = 'No reason.'
        
        await ctx.guild.ban(user, reason=reason)
        await ctx.send(f'<{OTHER_SUCCESS_EMOJI}> **Done.**')
        try:
            embed = discord.Embed(color=0x000000)
            embed.title = "Alert System"
            embed.description = f"**`Looks like you got banned from {ctx.guild.name}`** <a:BlobBan:466662201835388949>"
            embed.add_field(name="`Moderator`", value=f"**`{ctx.author}`**")
            embed.add_field(name="`Reason`", value=f"**`{reason}`**")
            await user.send(embed=embed)
        except discord.Forbidden as e:
            error = await ctx.send(f"<{OTHER_ERROR_EMOJI}> **`Looks like the user blocked me. DM message failed. Deleting this message in 5 seconds.`** ```py\n{type(e).__name__}: {e}\n```")
            await asyncio.sleep(5)
            await error.delete()
            pass

    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def poll(self, ctx, *, text: str):
        """Starts a poll with text."""
        if ctx.author.id in BLOCKED:
            return
        
        if ctx.author.bot:
            return
        
        embed = discord.Embed(color=0x000000)
        embed.description = f"{text}"
        embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url)
        embed.timestamp = datetime.utcnow()
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('\N{THUMBS UP SIGN}')
        await msg.add_reaction('\N{SHRUG}')
        await msg.add_reaction('\N{THUMBS DOWN SIGN}')

    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.command(pass_context=True)
    async def warn(self, ctx, logChannel: discord.TextChannel = None, user: discord.Member = None, *, reason: str = None):
        """Warns an user."""
        if ctx.author.id in BLOCKED:
            return
        if user is None:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **That's not a user. [example: @User#1111]**")
        if ctx.author.bot:
            return
        if self.bot.owner_id == user.id:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Can't warn the owner of this bot.**")
        if user == ctx.guild.owner:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Can't warn guild owner.**")
        if ctx.me.top_role <= user.top_role:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **My top role is lower or equal to member's top role, can't warn `{user}`.**")
        if ctx.author.top_role <= user.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Your top role is lower or equal to member's/Can't warn `{user}`.**")
        if reason is None:
            reason = 'No reason.'
        if logChannel is None:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **I need a logChannel. [example: #general]**")
        
        embed = discord.Embed(color=0x000000)
        embed.title = "Alert System"
        embed.description = f"**`{user} warned.`** \N{DOUBLE EXCLAMATION MARK}"
        embed.add_field(name="`Moderator`", value=f"**`{ctx.author}`**")
        embed.add_field(name="`Reason`", value=f"**`{reason}`**")
        await logChannel.send(embed=embed)

        await ctx.send(f'<{OTHER_SUCCESS_EMOJI}> **Done.**')
        try:
            embed = discord.Embed(color=0x000000)
            embed.title = "Alert System"
            embed.description = f"**`Looks like you got warned from {ctx.guild.name}`** \N{DOUBLE EXCLAMATION MARK}"
            embed.add_field(name="`Moderator`", value=f"**`{ctx.author}`**")
            embed.add_field(name="`Reason`", value=f"**`{reason}`**")
            await user.send(embed=embed)
        except discord.Forbidden as e:
            error = await ctx.send(f"<{OTHER_ERROR_EMOJI}> **`Looks like the user blocked me. DM message failed. Deleting this message in 5 seconds.`** ```py\n{type(e).__name__}: {e}\n```")
            await asyncio.sleep(5)
            await error.delete()
            pass

    @commands.group()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def mute(self, ctx):
        """Displays you some mute commands."""
        if ctx.invoked_subcommand is None:
                await ctx.send(f'<{OTHER_ERROR_EMOJI}> **`Incorrect random subcommand passed. Try {ctx.prefix}help mute`**')
    
    @mute.command()
    @commands.has_permissions(manage_channels=True)
    async def add(self, ctx, user: discord.Member, *, reason: str = None):
        """Mutes an user."""
        if ctx.author.bot:
            return
        if self.bot.owner_id == user.id:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Can't mute the owner of this bot.**")
        if user == ctx.guild.owner:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Can't mute guild owner.**")
        if ctx.me.top_role <= user.top_role:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **My top role is lower or equal to member's top role, can't mute `{user}`.**")
        if ctx.author.top_role <= user.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Your top role is lower or equal to member's/Can't mute `{user}`.**")
        if reason is None:
            reason = 'No reason.'
        await ctx.channel.set_permissions(user,         read_messages=True,
                                                        send_messages=False, reason=reason)
        await ctx.send(f'<{OTHER_SUCCESS_EMOJI}> **`Done.`**')
        try:
            embed = discord.Embed(color=0x000000)
            embed.title = "Alert System"
            embed.description = f"**`Looks like you got muted from {ctx.guild.name}`** \N{FACE WITHOUT MOUTH}"
            embed.add_field(name="`Moderator`", value=f"**`{ctx.author}`**")
            embed.add_field(name="`Reason`", value=f"**`{reason}`**")
            await user.send(embed=embed)
        except discord.Forbidden as e:
            error = await ctx.send(f"<{OTHER_ERROR_EMOJI}> **`Looks like the user blocked me. DM message failed. Deleting this message in 5 seconds.`** ```py\n{type(e).__name__}: {e}\n```")
            await asyncio.sleep(5)
            await error.delete()
            pass
    
    
    @mute.command()
    @commands.has_permissions(manage_channels=True)
    async def remove(self, ctx, user: discord.Member, *, reason: str = None):
        """Unmutes an user."""
        if ctx.author.bot:
            return
        if self.bot.owner_id == user.id:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Can't unmute the owner of this bot.**")
        if user == ctx.guild.owner:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Can't unmute guild owner.**")
        if ctx.me.top_role <= user.top_role:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **My top role is lower or equal to member's top role, can't unmute `{user}`.**")
        if ctx.author.top_role <= user.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send(f"<{OTHER_ERROR_EMOJI}> **Your top role is lower or equal to member's/Can't unmute `{user}`.**")
        if reason is None:
            reason = 'No reason.'
        await ctx.channel.set_permissions(user,         read_messages=True,
                                                        send_messages=True, reason=reason)
        await ctx.send(f'<{OTHER_SUCCESS_EMOJI}> **`Done.`**')
        try:
            embed = discord.Embed(color=0x000000)
            embed.title = "Alert System"
            embed.description = f"**`Looks like you got unmuted from {ctx.guild.name}`** \N{FACE WITHOUT MOUTH}"
            embed.add_field(name="`Moderator`", value=f"**`{ctx.author}`**")
            embed.add_field(name="`Reason`", value=f"**`{reason}`**")
            await user.send(embed=embed)
        except discord.Forbidden as e:
            error = await ctx.send(f"<{OTHER_ERROR_EMOJI}> **`Looks like the user blocked me. DM message failed. Deleting this message in 5 seconds.`** ```py\n{type(e).__name__}: {e}\n```")
            await asyncio.sleep(5)
            await error.delete()
            pass
        
def setup(bot):
    bot.add_cog(Moderation(bot))
