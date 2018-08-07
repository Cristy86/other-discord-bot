# basic dependencies
import discord
from discord.ext import commands
import random
from datetime import datetime

# aiohttp should be installed if discord.py is
import aiohttp

# PIL can be installed through
# `pip install -U Pillow`
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageFont

# partial lets us prepare a new function with args for run_in_executor
from functools import partial

# BytesIO allows us to convert bytes into a file-like byte stream.
from io import BytesIO

# this just allows for nice function annotation, and stops my IDE from complaining.
from typing import Union
from utils.constants import BLOCKED

class ImageCog:
    def __init__(self, bot: commands.Bot):

        # we need to include a reference to the bot here so we can access its loop later.
        self.bot = bot

        # create a ClientSession to be used for downloading avatars
        self.session = aiohttp.ClientSession(loop=bot.loop)


    async def get_avatar(self, user: Union[discord.User, discord.Member]) -> bytes:

        # generally an avatar will be 1024x1024, but we shouldn't rely on this
        avatar_url = user.avatar_url_as(format="png")

        async with self.session.get(avatar_url) as response:
            # this gives us our response object, and now we can read the bytes from it.
            avatar_bytes = await response.read()

        return avatar_bytes

    @staticmethod
    def make_jpeg(avatar_bytes: bytes) -> BytesIO:
        with Image.open(BytesIO(avatar_bytes)).convert('RGB') as im:
            jpeg_image = BytesIO()
            im.save(jpeg_image, format='jpeg', quality=1)
            jpeg_image.seek(0)

        return jpeg_image


    @staticmethod
    def make_edge(avatar_bytes: bytes) -> BytesIO:
        with Image.open(BytesIO(avatar_bytes)).convert('RGB') as im:
            horizontal = im.filter(ImageFilter.Kernel((3, 3), [-1, 0, 1, -1, 0, 1, -1, 0, 1], 1.0))
            vertical = im.filter(ImageFilter.Kernel((3, 3), [-1, -1, -1, 0, 0, 0, 1, 1, 1], 1.0))
            modified = Image.blend(horizontal, vertical, 0.5)

            edge_image = BytesIO()
            modified.save(edge_image, format='png')
            edge_image.seek(0)

        return edge_image

    @staticmethod
    def make_invert(avatar_bytes: bytes) -> BytesIO:
        with Image.open(BytesIO(avatar_bytes)).convert('RGB') as im:
            if im.mode == 'RGBA':
                r, g, b, a = im.split()
                r, g, b = map(lambda image: im.point(lambda p: 255 - p), (r, g, b))
                inverted_image = Image.merge(im.mode, (r, g, b, a))
            else:
                inverted_image = ImageOps.invert(im)

            invert_image = BytesIO()
            inverted_image.save(invert_image, format='png')
            invert_image.seek(0)

            return invert_image


    @staticmethod
    def processing(avatar_bytes: bytes, colour: tuple) -> BytesIO:

        # we must use BytesIO to load the image here as PIL expects a stream instead of
        # just raw bytes.
        with Image.open(BytesIO(avatar_bytes)) as im:

            # this creates a new image the same size as the user's avatar, with the
            # background colour being the user's colour.
            with Image.new("RGB", im.size, colour) as background:

                # this ensures that the user's avatar lacks an alpha channel, as we're
                # going to be substituting our own here.
                rgb_avatar = im.convert("RGB")

                # this is the mask image we will be using to create the circle cutout
                # effect on the avatar.
                with Image.new("L", im.size, 0) as mask:

                    # ImageDraw lets us draw on the image, in this instance, we will be
                    # using it to draw a white circle on the mask image.
                    mask_draw = ImageDraw.Draw(mask)

                    # draw the white circle from 0, 0 to the bottom right corner of the image
                    mask_draw.ellipse([(0, 0), im.size], fill=255)

                    # paste the alpha-less avatar on the background using the new circle mask
                    # we just created.
                    background.paste(rgb_avatar, (0, 0), mask=mask)

                # prepare the stream to save this image into
                final_buffer = BytesIO()

                # save into the stream, using png format.
                background.save(final_buffer, "png")

        # seek back to the start of the stream
        final_buffer.seek(0)

        return final_buffer

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def circle(self, ctx, *, member: discord.Member = None):
        """Display the user's avatar on their colour."""

        # this means that if the user does not supply a member, it will default to the
        # author of the message.
        if ctx.author.id in BLOCKED:
            return

        member = member or ctx.author

        async with ctx.typing():
            # this means the bot will type while it is processing and uploading the image

            if isinstance(member, discord.Member):
                # get the user's colour, pretty self explanatory
                member_colour = member.colour.to_rgb()
            else:
                # if this is in a DM or something went seriously wrong
                member_colour = (0, 0, 0)

            # grab the user's avatar as bytes
            avatar_bytes = await self.get_avatar(member)

            # create partial function so we don't have to stack the args in run_in_executor
            fn = partial(self.processing, avatar_bytes, member_colour)

            # this runs our processing in an executor, stopping it from blocking the thread loop.
            # as we already seeked back the buffer in the other thread, we're good to go
            final_buffer = await self.bot.loop.run_in_executor(None, fn)

            # prepare the file
            file = discord.File(filename="circle.png", fp=final_buffer)

            # send it
            await ctx.send(file=file)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def edge(self, ctx, *, member: discord.Member = None):
        """Display user's image like an edge image."""
        if ctx.author.id in BLOCKED:
            return

        member = member or ctx.author

        async with ctx.typing():
            avatar_bytes = await self.get_avatar(member)
            fn = partial(self.make_edge, avatar_bytes)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="edge.png", fp=final_buffer)

            await ctx.send(file=file)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def invert(self, ctx, *, member: discord.Member = None):
        """Inverts the colors from user's image."""
        if ctx.author.id in BLOCKED:
            return

        member = member or ctx.author

        async with ctx.typing():
            avatar_bytes = await self.get_avatar(member)
            fn = partial(self.make_invert, avatar_bytes)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="invert.png", fp=final_buffer)

            await ctx.send(file=file)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def jpeg(self, ctx, *, member: discord.Member = None):
        """Jpeg user's image."""
        if ctx.author.id in BLOCKED:
            return

        member = member or ctx.author

        async with ctx.typing():
            avatar_bytes = await self.get_avatar(member)
            fn = partial(self.make_jpeg, avatar_bytes)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)
            file = discord.File(filename="image.jpeg", fp=final_buffer)

            await ctx.send(file=file)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1.0, 20.0, commands.BucketType.user)
    async def shit(self, ctx, *, member: discord.Member = None):
        """Shits user's image."""
        if ctx.author.id in BLOCKED:
            return

        member = member or ctx.author

        async with ctx.typing():
            x = Image.open("app/cogs/images/meme1.png")
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png')) as r:
                    b = BytesIO(await r.read())
            im1 = Image.open(b).convert('RGBA')
            im4 = im1.resize((120, 200))
            im2 = im4.rotate(-45, expand=1)
            x.paste(im2, (200, 655), im2)
            x.save("image.png")
            await ctx.send(file=discord.File("image.png"))



# setup function so this can be loaded as an extension
def setup(bot: commands.Bot):
    bot.add_cog(ImageCog(bot))
