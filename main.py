import json
import discord, robloxpy, os, requests
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv(override=True)
TOKEN = os.getenv('DISCORD_TOKEN')
COOKIE = os.getenv('COOKIE')
print(robloxpy.User.Internal.SetCookie(COOKIE))
print(robloxpy.Utils.CheckCookie())

bot = commands.Bot()

bot.load_extension('commands.progression')

bot.run(TOKEN)
