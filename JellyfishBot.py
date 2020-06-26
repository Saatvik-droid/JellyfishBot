import discord
from discord.ext import commands

import datetime

bot = commands.Bot(command_prefix="==")

bot.start_time = datetime.datetime.now()

@bot.event
async def on_ready():
    print(f"Username: {bot.user} \n User id: {bot.user.id}")
    print(f"Latency: {round(bot.latency * 1000, 3)}ms")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you catch jellies"))

@bot.command(aliases=['up'], hidden=True)
@commands.is_owner()
async def uptime(ctx):
    delta_uptime = datetime.datetime.now() - bot.start_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    embed = discord.Embed(title="Uptime", description=f"{days}d, {hours}h, {minutes}m, {seconds}s", color=0x00FF00)
    await ctx.send(embed=embed)





