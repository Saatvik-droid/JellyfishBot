import discord
from discord.ext import commands, tasks

import asyncio
import random

from ._jelly import Jelly
from config import SPAWN_CHANNELS

class JellySpawn(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.spawner_started = False
        self.jelly_obj = Jelly()

    # spawns a random jelly
    async def spawn_jelly(self, channel: discord.TextChannel = None):
        jelly = await self.jelly_obj.get_random_jelly()
        if channel is not None:
            await channel.send(file=discord.File(jelly))
        else:
            for channel in SPAWN_CHANNELS:
                await channel.send(file=discord.File(jelly))

    # spawns random jelly every 5-30 mins
    @tasks.loop(minutes=5)
    async def random_spawner(self):
        if not self.spawner_started:
            if not SPAWN_CHANNELS:
                self.spawner_started = True
                while True:
                    await self.spawn_jelly()

                    # sleep for 5-30 mins
                    await asyncio.sleep(random.randint(5, 30)*60)

        else:
            pass

    # set channel(s) to spawn the jellyfish
    @commands.command(aliases=["set", "setspawn", "setchannel", "sp"], hidden=True)
    @commands.has_permissions(manage_channels=True)
    async def set_spawn_channel(self, ctx):
        channels = ctx.message.raw_channel_mentions
        for channel in channels:
            channel = self.bot.get_channel(channel)
            if channel not in SPAWN_CHANNELS:
                SPAWN_CHANNELS.append(channel)
                await ctx.send(f"Added channel <#{channel.id}>")
            else:
                await ctx.send(f"<#{channel.id}> already in the list")

    @commands.command(aliases=["spawn", "force", "fs"], hidden=True)
    @commands.has_permissions(manage_channels=True)
    async def forcespawn(self, ctx):
        channels = ctx.message.raw_channel_mentions
        for channel in channels:
            channel = self.bot.get_channel(channel)
            await self.spawn_jelly(channel=channel)

def setup(bot):
    bot.add_cog(JellySpawn(bot))
