import discord
from discord.ext import commands

from datetime import datetime
import random

from config import CATCH_PENDING
from .db import *


class Catcher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # watches all channels for jelly catching
    @commands.Cog.listener("on_message")
    async def catcher_watch(self, message):
        current_time = datetime.now()
        for user in message.mentions:
            if message.author.id != self.bot.user.id and user.id == self.bot.user.id:
                for jelly in CATCH_PENDING:
                    if message.channel.id == jelly.channel_id:
                        if not await self.sting_check(jelly, current_time):
                            await DB.update_score(message.author.id)
                            CATCH_PENDING.remove(jelly)
                        else:
                            embed = discord.Embed(title="STING", description="HAHAHAHA you got stung", color=0xffff1a)
                            await message.channel.send(embed=embed)

    @staticmethod
    async def sting_check(jelly, current_time):
        diff_time = current_time - jelly.spawn_time
        sting_factor = (diff_time.seconds * jelly.score) + 50
        if sting_factor < jelly.score * random.randint(1, 10) +10:
            print(f"sting score {diff_time.seconds}")
            return True
        elif random.randint(1, 10) > 8:
            print("sting rand")
            return True
        print("not sting")
        return False


    # get score of a particular user
    # if no user mentioned it assumes msg author
    # if user id provided as arg it works if there's no user mentions in the msg
    @commands.command(aliases=["score"])
    async def get_score(self, ctx, arg=None):
        if ctx.message.mentions:
            for user in ctx.message.mentions:
                if user is not None:
                    score = await DB.check_db_score(user.id)
                    await self.display_score(ctx, user.id, score)
        elif arg is not None:
            score = await DB.check_db_score(arg)
            await self.display_score(ctx, arg, score)
        else:
            score = await DB.check_db_score(ctx.author.id)
            await self.display_score(ctx, ctx.author.id, score)

    @commands.command()
    async def helpscore(self, ctx):
        embed = discord.Embed(title="Help - Score",
                              description="Returns score of mentioned user. Can parse only one user at a time.",
                              color=0xffff1a)
        await ctx.send(embed=embed)

    @staticmethod
    async def display_score(ctx, user_id: int, score):
        try:
            if score is not None:
                embed = discord.Embed(title="Score", description=f"<@{user_id}> has {score} points", color=0x00FF00)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Score", description=f"<@{user_id}> Not listed", color=0xff3434)
                await ctx.send(embed=embed)
        except commands.BotMissingPermissions:
            await ctx.send("Bot missing permissions")


def setup(bot):
    bot.add_cog(Catcher(bot))
