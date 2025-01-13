import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime
from itertools import cycle

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

intents = discord.Intents.all()
intents.members = True
intents.guilds = True
intents.presences = True
bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

# Define status messages
status_messages = cycle([
    "We are working on a fix for modding.",
    "We are trying our best bare with us.",
    "Modding has been disabled, were working hard"
])

@tasks.loop(seconds=10)  # Change status every 10 seconds
async def change_status():
    await bot.change_presence(activity=discord.CustomActivity(
        name=next(status_messages)
    ))

# Load cogs
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await load_extensions()
    await bot.tree.sync()
    change_status.start()  # Start the status rotation

@bot.command()
@commands.is_owner()  # Only bot owner can use this
async def reload(ctx, extension):
    try:
        await bot.reload_extension(f'cogs.{extension}')
        await ctx.send(f'✅ Reloaded {extension}')
    except Exception as e:
        await ctx.send(f'❌ Error reloading {extension}: {str(e)}')

@bot.command()
@commands.is_owner()  # Only bot owner can use this
async def reloadall(ctx):
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.reload_extension(f'cogs.{filename[:-3]}')
                await ctx.send(f'✅ Reloaded {filename[:-3]}')
            except Exception as e:
                await ctx.send(f'❌ Error reloading {filename[:-3]}: {str(e)}')

bot.run(config['token']) 