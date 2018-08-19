import discord
from discord.ext import commands

import asyncio
import os

from datetime import datetime
from cogs.cmds import bot_version
from utils.constants import BLOCKED, BOT_OWNER_ID
import pkg_resources, platform, psutil

bot = commands.Bot(command_prefix=commands.when_mentioned_or(os.getenv('BOT_PREFIX')))
bot.remove_command('help')
bot.launch_time = datetime.utcnow()
bot.process = psutil.Process()
bot.launch_time = datetime.utcnow()
startup_extensions = ['cogs.admin','cogs.music','cogs.eh','cogs.cmds','cogs.mod','cogs.info','cogs.image','cogs.events','jishaku','cogs.api']


@bot.event
async def on_ready():
    print('Logged in as:')
    print('------')
    print(f'Username: {bot.user.name}')
    print(f'ID: {bot.user.id}')
    print(f'Bot Version: {bot_version}')
    print(f'Active on: {len(bot.guilds)} Servers.')
    print('------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{os.getenv('BOT_PREFIX')}help | {len(bot.users)} users."))

@bot.command(name='stats')
async def _stats(ctx):
    """Shows the stats of the bot."""
    if ctx.author.bot:
        return
    if ctx.author.id in BLOCKED:
        return

    delta_uptime = datetime.utcnow() - bot.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    embed = discord.Embed(color=0x000000)
    embed.title = f"{bot.user.name}'s stats "
    embed.description = f"`{bot.user} is created by {bot.get_user(BOT_OWNER_ID)}.`\n`{len(bot.guilds)} servers, {len(bot.emojis)} emojis, {len(bot.cogs)} cogs and {len(bot.users)} users.`\n\n\N{WHITE SMALL SQUARE} **Python Version:** **`{platform.python_version()}`** <:python_image:448428643543416832>\n\N{WHITE SMALL SQUARE} **discord.py Version:** **`{pkg_resources.get_distribution('discord.py').version}`** <:discord:453469273344442370>\n\N{WHITE SMALL SQUARE} **RAM Usage:** **`{psutil.virtual_memory().percent} MB`** <:computer_ram:463269182209785866>\n\N{WHITE SMALL SQUARE} **CPU Usage:** **`{psutil.cpu_percent()}%`** <:cpu:453497845501394945>\n\N{WHITE SMALL SQUARE} **Process Memory: `{round(bot.process.memory_info().rss / 1024 / 1024)} MB`** :question:\n\N{WHITE SMALL SQUARE} **Websocket latency: `{round(bot.latency * 1000)}ms.`** \N{TABLE TENNIS PADDLE AND BALL}\n\N{WHITE SMALL SQUARE} **Uptime: `{days}d, {hours}h, {minutes}m, {seconds}s`** \N{TIMER CLOCK}"
    embed.set_footer(text=f"{bot.user.name}")
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.timestamp = datetime.utcnow()
    await ctx.send(embed=embed)

if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

bot.run(os.getenv('BOT_TOKEN'))
