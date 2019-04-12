import traceback
import sys
from discord.ext import commands
import discord
from datetime import datetime
from utils.constants import OTHER_ERROR_EMOJI

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        
        ignored = (commands.MissingRequiredArgument, commands.BadArgument, commands.NoPrivateMessage, commands.CheckFailure, commands.DisabledCommand, commands.CommandInvokeError, commands.TooManyArguments, commands.UserInputError, commands.NotOwner, commands.MissingPermissions, commands.BotMissingPermissions, AttributeError, KeyError, TypeError, ValueError, discord.Forbidden, discord.ConnectionClosed, discord.HTTPException, UnboundLocalError, NameError, FileNotFoundError, RuntimeError, RuntimeWarning, OSError, IndexError, ZeroDivisionError)   
        error = getattr(error, 'original', error)
        
        if isinstance(error, ignored):
            embed = discord.Embed(color=0x000000)
            embed.description = f"<{OTHER_ERROR_EMOJI}> **`{error}`**"
            embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
            embed.timestamp = datetime.utcnow()            
            await ctx.send(embed=embed)

        elif isinstance(error, commands.CommandOnCooldown):
            if await self.bot.is_owner(ctx.author):
                await ctx.reinvoke()
            else:
                embed = discord.Embed(color=0x000000)
                embed.description = f"<{OTHER_ERROR_EMOJI}> **`{error}`**"
                embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
                embed.timestamp = datetime.utcnow()
                await ctx.send(embed=embed)
        
        elif isinstance(error, commands.DisabledCommand):
            if await self.bot.is_owner(ctx.author):
                await ctx.reinvoke()
            else:
                embed = discord.Embed(color=0x000000)
                embed.description = f"<{OTHER_ERROR_EMOJI}> **`{error}`**"
                embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
                embed.timestamp = datetime.utcnow()    
                await ctx.send(embed=embed)
        
        elif isinstance(error, commands.CommandNotFound):
            return


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
