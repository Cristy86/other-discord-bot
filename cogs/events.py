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
from discord import Embed
from utils.constants import BOT_GUILD_ID, BANNED_LOG_CHANNEL_ID, ADDED_REMOVED_CHANNEL_ID

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    def guild_info(self, guild):
        count = sum(1 for m in guild.members if m.bot)
        ratio = round(count / guild.member_count * 100)
        embed = Embed(color=0x000000)
        embed.add_field(name="Guild 🆔", value=f"**`{guild.id}`**", inline=False)
        embed.add_field(name="Members count 👥", value=f"**`{guild.member_count - count}`** and **`{count}`** bots.", inline=False)
        embed.add_field(name="Owner 🆔", value=f"**`{guild.owner.id}`**", inline=False)
        embed.add_field(name="Bot ratio 📈", value=f"**`{ratio}%`**", inline=False)
        embed.add_field(name="Now active on servers <:Servers:453459326791843841>", value=f"**`{len(self.bot.guilds)}`**", inline=False)
        embed.set_thumbnail(url=guild.icon_url or guild.owner.avatar_url)
        embed.set_footer(text=f'The owner of this server: {guild.owner}', icon_url=guild.owner.avatar_url)

        return embed
   
    async def on_member_ban(self, guild, member):
        if guild.id != BOT_GUILD_ID:
            return

        await self.bot.get_channel(BANNED_LOG_CHANNEL_ID).send(f"<:trashcan_empty:447669800660107264> **`{member} banned from {guild.name}!`** <a:BlobBanHammer:465503815479590922>")

    async def on_member_unban(self, guild, member):
        if guild.id != BOT_GUILD_ID:
            return

        await self.bot.get_channel(BANNED_LOG_CHANNEL_ID).send(f"<:trashcan_empty:447669800660107264> **`{member} unbanned from {guild.name}!`** <a:BlobBanHammer:465503815479590922>")

    async def on_guild_join(self, guild):
        embed = self.guild_info(guild)
        embed.title = f'Added to a new server: {guild}'
        await self.bot.get_channel(ADDED_REMOVED_CHANNEL_ID).send(embed=embed)
    
    async def on_guild_remove(self, guild):
        embed = self.guild_info(guild)
        embed.title = f'Removed from a server: {guild}'
        await self.bot.get_channel(ADDED_REMOVED_CHANNEL_ID).send(embed=embed)
    

def setup(bot):
    bot.add_cog(Events(bot))
