import discord
from discord.ext import commands, tasks

import asyncio
import random

from ._jelly import Jelly
from config import SPAWN_CHANNELS_ID, CATCH_PENDING_ID

class JellySpawn(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.spawner_started = False
        self.jelly_obj = Jelly()
        self.random_spawner.start()

    # spawns a random jelly
    async def spawn_jelly(self, channel_id: int = None):
        jelly = await self.jelly_obj.get_random_jelly()
        if channel_id is not None:
            channel = self.bot.get_channel(channel_id)
            await channel.send(file=discord.File(jelly))
            CATCH_PENDING_ID.append(channel_id)
        else:
            for channel_id in SPAWN_CHANNELS_ID:
                channel = self.bot.get_channel(channel_id)
                await channel.send(file=discord.File(jelly))
                CATCH_PENDING_ID.append(channel_id)

    # spawns random jelly every 5-30 mins
    @tasks.loop(seconds=5.0)
    async def random_spawner(self):
        await self.bot.wait_until_ready()
        if SPAWN_CHANNELS_ID and not self.spawner_started:
            self.spawner_started = True
            while True:
                await self.spawn_jelly()

                # sleep for 5-30 mins
                # changed to secs for testing
                await asyncio.sleep(random.randint(1, 5))
        else:
            pass

    # set channel(s) to spawn the jellyfish
    @commands.command(aliases=["set", "setspawn", "setchannel", "sc", "ss"], hidden=True)
    @commands.has_permissions(manage_channels=True)
    async def set_spawn_channel(self, ctx):
        channels = ctx.message.raw_channel_mentions
        for channel in channels:
            channel_id = self.bot.get_channel(channel).id
            if channel_id not in SPAWN_CHANNELS_ID:
                SPAWN_CHANNELS_ID.append(channel_id)
                await ctx.send(f"Added channel <#{channel_id}>")
            else:
                await ctx.send(f"<#{channel_id}> already in the list")

    @commands.command(aliases=["spawn", "force", "fs"], hidden=True)
    @commands.has_permissions(manage_channels=True)
    async def forcespawn(self, ctx):
        channels = ctx.message.raw_channel_mentions
        for channel in channels:
            channel_id = self.bot.get_channel(channel).id
            await self.spawn_jelly(channel_id=channel_id)

    # get channels it currently spawns in
    @commands.command(aliases=["get", "getspawn", "getchannel", "gc", "gs"])
    async def get_spawn_channel(self, ctx):
        if not SPAWN_CHANNELS_ID:
            await ctx.send("No channels selected")
        else:
            for channel_id in SPAWN_CHANNELS_ID:
                await ctx.send(f"currently spawns in <#{channel_id}>")

    # remove channel from list
    @commands.command(aliases=["remove", "removespawn", "removechannel", "rc", "rs"])
    @commands.has_permissions(manage_guild=True)
    async def remove_spawn_channel(self, ctx):
        channels = ctx.message.raw_channel_mentions
        for channel in channels:
            channel_id = self.bot.get_channel(channel).id
            if channel_id in SPAWN_CHANNELS_ID:
                SPAWN_CHANNELS_ID.remove(channel_id)
                await ctx.send(f"<#{channel_id}> was removed.")
            else:
                await ctx.send(f"<#{channel_id}> wasnt in the queue.")

def setup(bot):
    bot.add_cog(JellySpawn(bot))
