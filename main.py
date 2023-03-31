# bot.py
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot()

@bot.slash_command(name="hello", description = "Say hello to the bot")
async def hello(ctx): 
    await ctx.respond("Hi there :)")
    
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')




bot.load_extension('commands.progression')

bot.run(TOKEN)