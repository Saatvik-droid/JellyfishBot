import discord
from discord.ext import commands

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, BIGINT

from config import CATCH_PENDING_ID, DATABASE_URI

engine = create_engine(DATABASE_URI)
meta = MetaData()

scores = Table(
                "scores", meta,
                Column("id", Integer, primary_key=True),
                Column("user_id", BIGINT, unique=True, nullable=False),
                Column("score", Integer, default=0),
)

class Catcher(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # watches all channels for jelly catching
    @commands.Cog.listener("on_message")
    async def catcher_watch(self, message):
        for user in message.mentions:
            if user.id == self.bot.user.id and message.channel.id in CATCH_PENDING_ID:
                await message.channel.send(f"Congratulations <@{message.author.id}> caught a jelly")
                conn = engine.connect()
                query = scores.select().where(scores.c.user_id == message.author.id)
                result = conn.execute(query)
                row = result.fetchone()
                if row is not None:
                    score = row.score
                    update = scores.update().where(scores.c.user_id == message.author.id).values(score=score + 1)
                    conn.execute(update)
                else:
                    insert = scores.insert().values(user_id=message.author.id, score=1)
                    conn.execute(insert)

def setup(bot):
    bot.add_cog(Catcher(bot))