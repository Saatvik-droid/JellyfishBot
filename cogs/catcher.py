import discord
from discord.ext import commands

from config import CATCH_PENDING_ID
from .db import *

class Catcher(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # watches all channels for jelly catching
    @commands.Cog.listener("on_message")
    async def catcher_watch(self, message):
        for user in message.mentions:
            if user.id == self.bot.user.id and message.channel.id in CATCH_PENDING_ID:
                await DB.update_score(self, message.author.id)
                await message.channel.send(f"Congratulations <@{message.author.id}> caught a jelly")

    # get score of a particular user
    # if no user mentioned it assumes msg author
    # if user id provided as arg it works if there's no user mentions in the msg
    @commands.command(aliases=["score"])
    async def get_score(self, ctx, arg=None):
        if ctx.message.mentions:
            for user in ctx.message.mentions:
                if user is not None:
                    score = await DB.check_db_score(self, user.id)
                    await self.display_score(ctx, user.id, score)
        elif arg is not None:
            score = await DB.check_db_score(self, arg)
            await self.display_score(ctx, arg, score)
        else:
            score = await DB.check_db_score(self, ctx.author.id)
            await self.display_score(ctx, ctx.author.id, score)

    async def display_score(self, ctx, user_id: int, score):
        if score is not None:
            await ctx.send(f"<@{user_id}> has {score}")
        else:
            await ctx.send(f"<@{user_id}> Not listed")


def setup(bot):
    bot.add_cog(Catcher(bot))

