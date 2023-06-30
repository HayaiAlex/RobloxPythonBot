import discord,robloxpy, os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv(override=True)
TOKEN = os.getenv('DISCORD_TOKEN')
COOKIE = os.getenv('COOKIE')
robloxpy.User.Internal.SetCookie(COOKIE)
print(robloxpy.Utils.CheckCookie())

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(intents=intents)

bot.load_extension('commands.progression')
bot.load_extension('commands.join_manager')
bot.load_extension('commands.commendations')
bot.load_extension('commands.provinces')
bot.load_extension('commands.role_manager')
bot.load_extension('api.webserver')

bot.run(TOKEN)
