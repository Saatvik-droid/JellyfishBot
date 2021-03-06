import discord
from discord.ext import commands, tasks

import asyncio
import random

from ._jelly import Jelly
from config import SPAWN_CHANNELS_ID, CATCH_PENDING


class Jellyspawn(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.spawner_started = False
        self.jelly_obj = Jelly()
        self.random_spawner.start()

    # spawns a random jelly
    # currently doesnt stack but remove inner if cases to stack
    async def spawn_jelly(self, channel_id: int = None):
        if channel_id is not None:
            await self.send_image(channel_id)
        else:
            for channel_id in SPAWN_CHANNELS_ID:
                await self.send_image(channel_id)

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
            try:
                if channel_id not in SPAWN_CHANNELS_ID:
                    SPAWN_CHANNELS_ID.append(channel_id)
                    embed = discord.Embed(title="Spawn channel", description=f"<#{channel_id}> SUCCESSFULY ADDED!", color=0x00FF00)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="Spawn channel", description=f"<#{channel_id}> FAILED!\n\n (already in the list)", color=0xff3434)
                    await ctx.send(embed=embed)
            except commands.MissingPermissions:
                await ctx.send("You do not have adequate permissions")
            except commands.BotMissingPermissions:
                await ctx.send("Bot missing permissions")

    @commands.command(aliases=["helpsetspawn", "helpsetchannel", "helpss", "helpsc"])
    async def helpset(self, ctx):
        embed = discord.Embed(title="Help - Set Spawn",
                              description="Sets channel for jelly to spawn. You have to #mention every channel. It can parse multiple mentions (User needs manage channels permission to execute this command)\nAlternate names-> setspawn, setchannel, sc, ss",
                              color=0xffff1a)
        await ctx.send(embed=embed)

    @commands.command(aliases=["spawn", "force", "fs"], hidden=True)
    @commands.has_permissions(manage_channels=True)
    async def forcespawn(self, ctx):
        try:
            channels = ctx.message.raw_channel_mentions
            for channel in channels:
                channel_id = self.bot.get_channel(channel).id
                await self.spawn_jelly(channel_id=channel_id)
        except commands.MissingPermissions:
            await ctx.send("You do not have adequate permissions")

    @commands.command(aliases=["helpspawn", "helpforce", "helpfs"])
    async def helpforcespawn(self, ctx):
        embed = discord.Embed(title="Help - Force Spawn",
                              description="Forces the bot to spawn a jelly. You have to #mention every channel. It can parse multiple mentions (User needs manage channels permissions to execute this command)\nAlternate names-> force, spawn, fs",
                              color=0xffff1a)
        await ctx.send(embed=embed)

    # get channels it currently spawns in
    @commands.command(aliases=["get", "getspawn", "getchannel", "gc", "gs"])
    async def get_spawn_channel(self, ctx):
        channels = ""
        try:
            if not SPAWN_CHANNELS_ID:
                embed = discord.Embed(title="Spawn channel", description=f"No channels selected", color=0xffff1a)
                await ctx.send(embed=embed)
            else:
                for channel_id in SPAWN_CHANNELS_ID:
                    channels += f"<#{channel_id}>"
            if channels != "":
                embed = discord.Embed(title="Spawn channel", description=f"Currently spawns in {channels}", color=0xffff1a)
                await ctx.send(embed=embed)
        except commands.BotMissingPermissions:
            await ctx.send("Bot missing permissions")

    @commands.command(aliases=["helpgetspawn", "helpgetchannel", "helpgc", "helpgs"])
    async def helpget(self, ctx):
        embed = discord.Embed(title="Help - Get Spawn",
                              description="Get channels the bot spawns jellies in.\nAlternate names-> getspawn, getchannel, gc, gs",
                              color=0xffff1a)
        await ctx.send(embed=embed)

    # remove channel from list
    @commands.command(aliases=["remove", "removespawn", "removechannel", "rc", "rs"])
    @commands.has_permissions(manage_channels=True)
    async def remove_spawn_channel(self, ctx):
        channels = ctx.message.raw_channel_mentions
        channels_in = ""
        channels_not = ""
        try:
            for channel in channels:
                channel_id = self.bot.get_channel(channel).id
                if channel_id in SPAWN_CHANNELS_ID:
                    SPAWN_CHANNELS_ID.remove(channel_id)
                    channels_in = ""
                    channels_in += f"<#{channel_id}>"
                else:
                    channels_not = f"<#{channel_id}>"
            if channels_in != "":
                embed = discord.Embed(title="Spawn channel", description=f"{channels_in} SUCCESSFULY REMOVED!", color=0x00FF00)
                await ctx.send(embed=embed)
            if channels_not != "":
                embed = discord.Embed(title="Spawn channel", description=f"{channels_not} FAILED!\n\n (not in the queue)", color=0xff3434)
                await ctx.send(embed=embed)
        except commands.MissingPermissions:
            await ctx.send("You do not have adequate permissions")
        except commands.BotMissingPermissions:
            await ctx.send("Bot missing permissions")

    @commands.command(aliases=["helpremovespawn", "helpremovechannel", "helprc", "helprs"])
    async def helpremove(self, ctx):
        embed = discord.Embed(title="Help - Remove Spawn",
                              description="Removes #mentioned channels from the queue. It can parse multiple channles (User needs manage channels permission to execute this command)\nAlternate names-> removechannel, removespawn, rs , rc",
                              color=0xffff1a)
        await ctx.send(embed=embed)

    async def send_image(self, channel_id):
        jelly = Jelly()
        channel = self.bot.get_channel(channel_id)
        try:
            await channel.send(file=discord.File(jelly.image))
        except commands.BotMissingPermissions:
            await channel.send("Bot missing permissions")
        remove_dupli(channel_id)
        jelly.channel_id = channel_id
        CATCH_PENDING.append(jelly)


def remove_dupli(curr_channel):
    for jelly in CATCH_PENDING:
        if curr_channel == jelly.channel_id:
            CATCH_PENDING.remove(jelly)


def setup(bot):
    bot.add_cog(Jellyspawn(bot))
