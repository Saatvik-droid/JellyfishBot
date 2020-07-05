import discord
from discord.ext import commands

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, BIGINT
from sqlalchemy.exc import SQLAlchemyError

from config import DATABASE_URI

engine = create_engine(DATABASE_URI)
meta = MetaData()

scores = Table(
                "scores", meta,
                Column("id", Integer, primary_key=True),
                Column("user_id", BIGINT, unique=True, nullable=False),
                Column("score", Integer, default=0),
)


class DB(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # increases score by 1
    @staticmethod
    async def update_score(user_id: int):
        try:
            conn = engine.connect()
            query = scores.select().where(scores.c.user_id == user_id)
            result = conn.execute(query)
            row = result.fetchone()
            if row is not None:
                score = row.score
                update = scores.update().where(scores.c.user_id == user_id).values(score=score + 1)
                conn.execute(update)
            else:
                insert = scores.insert().values(user_id=user_id, score=1)
                conn.execute(insert)
        except SQLAlchemyError:
            print("DB error raise the alarms!")

    # gets score for given user id from the db
    @staticmethod
    async def check_db_score(user_id: int):
        try:
            conn = engine.connect()
            query = scores.select().where(scores.c.user_id == user_id)
            result = conn.execute(query)
            row = result.fetchone()
            if row is not None:
                score = row.score
                return score
            return None
        except SQLAlchemyError:
            print("DB error raise the alarms!")

    # deletes user records from the db
    @staticmethod
    async def remove_user(ctx, user_id):
        try:
            conn = engine.connect()
            delete = scores.delete().where(scores.c.user_id == user_id)
            conn.execute(delete)
            await ctx.send(f"deleted <@{user_id}>")
        except commands.BotMissingPermissions:
            pass
        except SQLAlchemyError:
            print("DB error raise the alarms!")

    @commands.command(aliases=["lb", "top"])
    async def leaderboard(self, ctx):
        lbd = await self.get_lb()
        embed = discord.Embed(title="Database - leaderboard", description=lbd, color=0xffff1a)
        await ctx.send(embed=embed)

    async def get_lb(self):
        try:
            conn = engine.connect()
            query = scores.select().order_by(scores.c.score.desc()).limit(10)
            result = conn.execute(query)
            lbd = ""
            for row in result:
                user_nick = self.bot.get_user(row.user_id).display_name
                user_dis = self.bot.get_user(row.user_id).discriminator
                lbd += f"{user_nick}#{user_dis} - {row.score}\n"
            return lbd
        except SQLAlchemyError:
            print("DB error raise the alarms!")

    # removes mentioned user(s) from the db
    # user id can be provided as arg if theres no user mentions in the message
    @commands.command(aliases=["ru"])
    @commands.has_permissions(manage_guild=True)
    async def remove_user_from_db(self, ctx, arg):
        if ctx.message.mentions:
            for user in ctx.message.mentions:
                await DB.remove_user(ctx, user.id)
        elif arg is not None:
            await DB.remove_user(ctx, arg)
        else:
            embed = discord.Embed(title="Database - users", description=f"No argument provided!", color=0xff3434)
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DB(bot))
