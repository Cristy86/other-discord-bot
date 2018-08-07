import discord
from discord.ext import commands
import random

import unicodedata
import time
import asyncio
import aiohttp
import io
import platform
import os

from datetime import datetime
from cogs.cmds import bot_version
from utils.constants import BLOCKED


description = '''PythonBot but in rewrite.'''
bot = commands.Bot(command_prefix=commands.when_mentioned_or('e-'), description=description)
bot.remove_command('help')
bot.launch_time = datetime.utcnow()
startup_extensions = ['cogs.admin','cogs.music','cogs.eh','cogs.cmds','cogs.mod','cogs.info','cogs.image','cogs.events','jishaku','cogs.api']
nl4 = "------"


@bot.event
async def on_ready():
    print('Logged in as:')
    print(f'{nl4}')
    print(f'Username: {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print(f'Bot Version: {bot_version}')
    print(f'Active on: {len(bot.guilds)} Servers.')
    print(f'{nl4}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"e-help | {len(bot.users)} users."))

@bot.command()
async def uptime(ctx):
    if ctx.author.id in BLOCKED:
        return

    delta_uptime = datetime.utcnow() - bot.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    await ctx.send(f"**`{days}d, {hours}h, {minutes}m, {seconds}s`**")

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

bot.run(os.getenv('BOT_TOKEN'))
