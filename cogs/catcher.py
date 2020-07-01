import discord
from discord.ext import commands

from config import CATCH_PENDING_ID

class Catcher(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # watches all channels for jelly catching
    @commands.Cog.listener("on_message")
    async def catcher_watch(self, message):
        for user in message.mentions:
            if user.id == self.bot.user.id and message.channel.id in CATCH_PENDING_ID:
                await message.channel.send(f"Congratulations <@{message.author.id}> caught a jelly")

def setup(bot):
    bot.add_cog(Catcher(bot))