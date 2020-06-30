import discord
from discord.ext import commands

import os
from datetime import datetime

from config import TOKEN

bot = commands.Bot(command_prefix=commands.when_mentioned_or("=="))

bot.start_time = datetime.now()

# sets activity to watching you catch jellies
@bot.event
async def on_ready():
    print(f"Username: {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you catch jellies"))

# gets uptime of the bot (time it has been up since the last restart)
@bot.command(aliases=["up"], hidden=True)
async def uptime(ctx):
    delta_uptime = datetime.now() - bot.start_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    embed = discord.Embed(title="Uptime", description=f"{days}d, {hours}h, {minutes}m, {seconds}s", color=0x00FF00)
    await ctx.send(embed=embed)

# reload cogs, for hot reloading without restarting the bot
@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, cog: str=None):
    await ctx.send("Trying to reload...")
    try:
        if cog is None:
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py") and not filename.startswith("_") and not filename.startswith("jellyspawn"):
                    bot.unload_extension(f"cogs.{filename[:-3]}")
                    bot.load_extension(f"cogs.{filename[:-3]}")
            cog = "all cogs"
        else:
            if not cog.startswith("jellyspawn"):
                cog = cog.lower()
                bot.unload_extension(f"cogs.{cog}")
                bot.load_extension(f"cogs.{cog}")
            else:
                ctx.send("**Please do not restart jellyspawn.py.\nIf you really want to please restart the bot.**")

    except Exception as error:
        await ctx.send(f"{cog} could'nt be reloaded")

    await ctx.send(f"Successfully reloaded {cog}")

# loading all cogs on start
for filename in os.listdir(r"./cogs"):
    if filename.endswith(".py") and not filename.startswith("_"):
        try:
            bot.load_extension(f"cogs.{filename[:-3]}")
        except Exception as error:
            print(f"{filename} could'nt be loaded")
            raise error

bot.run(TOKEN)




