import discord
from discord.ext import commands
from lib.sql.queries import award
from lib.roblox.roblox_functions import get_roblox_ids

events = ['Raid', 'Defense','Defense Training','Prism Training']

# takes a discord input of users and outputs a list of clean ids
# def parse_users_to_ids(users):
#     # remove special characters
#     users = ''.join(c for c in users if c not in '<>@!,')
#     # create a list of users
#     users = users.split()
#     ids = [await get_id(user) for user in users]
#     return ids

class Progression(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="award", description = "award an event to a group of users")
    async def award(self, ctx, event: discord.Option(str, choices=events), users: discord.Option(str)):
        print(users)
        user_ids = get_roblox_ids(users)
        status = award(event,user_ids)
        if status == 'Success':
            await ctx.respond(f'Awarded {users} a {event} point!')
        else:
            await ctx.respond(f'Something went wrong! ({status})')

def setup(bot):
    bot.add_cog(Progression(bot))