import discord
from discord.ext import commands

import asyncio
import random

from ._jelly import Jelly

spawn_timer = 5

class JellySpawn(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.spawn_channels = []
        self.jelly_obj = Jelly()

    # spawns a random jelly
    async def spawn_jelly(self, channel: discord.TextChannel = None):
        jelly = await self.jelly_obj.get_random_jelly()
        if channel is not None:
            await channel.send(file=discord.File(jelly))
        else:
            for channel in self.spawn_channels:
                await channel.send(file=discord.File(jelly))

    # spawns random jelly every 5-30 mins
    async def random_spawner(self):
        while True:
            await self.spawn_jelly()

            asyncio.sleep(random.randint(5, 30)*60)

    # set channel(s) to spawn the jellyfish
    @commands.command(aliases=["set", "setspawn", "setchannel"], hidden=True)
    @commands.has_permissions(manage_channels=True)
    async def set_spawn_channel(self, ctx):
        added_tracker = ""
        channels = ctx.message.raw_channel_mentions
        for channel in channels:
            channel = self.bot.get_channel(channel)
            self.spawn_channels.append(channel)
            added_tracker += f"<#{channel.id}> "

        await ctx.send(f"Added channel(s) {added_tracker}")
        await self.spawn_jelly()


    @commands.command(aliases=["spawn", "force"], hidden=True)
    @commands.has_permissions(manage_channels=True)
    async def forcespawn(self, ctx):
        channels = ctx.message.raw_channel_mentions
        for channel in channels:
            channel = self.bot.get_channel(channel)
            await self.spawn_jelly(channel=channel)

def setup(bot):
    bot.add_cog(JellySpawn(bot))
