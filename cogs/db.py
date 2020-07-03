import discord
from discord.ext import commands

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, BIGINT

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
    async def update_score(self, user_id: int):
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

    # gets score for given user id from the db
    async def check_db_score(self, user_id: int):
        conn = engine.connect()
        query = scores.select().where(scores.c.user_id == user_id)
        result = conn.execute(query)
        row = result.fetchone()
        if row is not None:
            score = row.score
            return score
        return None

    # deletes user records from the db
    async def remove_user(self, ctx, user_id):
        try:
            conn = engine.connect()
            delete = scores.delete().where(scores.c.user_id == user_id)
            result = conn.execute(delete)
            await ctx.send(f"deleted <@{user_id}>")
        except Exception:
            await ctx.send("something went wrong")

    @commands.command(aliases=["lb", "top"])
    async def leaderboard(self, ctx):
        lbd = await self.get_lb()
        await ctx.send(lbd)

    async def get_lb(self):
        conn = engine.connect()
        query = scores.select().order_by(scores.c.score.desc()).limit(10)
        result = conn.execute(query)
        lbd = ""
        for row in result:
            user_nick = self.bot.get_user(row.user_id).display_name
            lbd += f"{user_nick} - {row.score}\n"
        return lbd

    # removes mentioned user(s) from the db
    # user id can be provided as arg if theres no user mentions in the message
    @commands.command(aliases=["ru"])
    @commands.has_permissions(manage_guild=True)
    async def remove_user_from_db(self, ctx, arg):
        if ctx.message.mentions:
            for user in ctx.message.mentions:
                await DB.remove_user(self, ctx, user.id)
        elif arg is not None:
            await DB.remove_user(self, ctx, arg)
        else:
            await ctx.send("no arg provided")

def setup(bot):
    bot.add_cog(DB(bot))