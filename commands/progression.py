import datetime
import robloxpy
import discord
from discord.ext import commands
from lib.sql.queries import award
from lib.roblox.roblox_functions import get_roblox_ids, check_for_promotions, get_role_in_group
from lib.sql.queries import get_data_from_id

events = ['Raid', 'Defense','Defense Training','Prism Training']
class Progression(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="award", description = "award an event to a group of users")
    async def award(self, ctx, event: discord.Option(str, choices=events), users: discord.Option(str)):
        print(users)
        user_ids = [user.get('id') for user in get_roblox_ids(users)]
        status = award(event,user_ids)
        if status == 'Success':
            await ctx.respond(f'Awarded {users} a {event} point!')
            check_for_promotions(user_ids)
        else:
            await ctx.respond(f'Something went wrong! ({status})')

    @discord.slash_command(name="profile", description = "shows a user's career profile")
    async def profile(self, ctx, user: discord.Option(str)):
        print(user)
        user = get_roblox_ids(user)[0]
        print(user)
        user_data = get_data_from_id(user.get('id'))
        roles = get_role_in_group(user['id'], 6870149)
        print(roles)
        print(f"user_data {user_data}")

        embed = discord.Embed(
            title=f"{user.get('username')}'s Profile",
            description=f"Rank: **{roles['name']}**",
            url=f"https://www.roblox.com/users/{user['id']}/profile",
            color=discord.Colour.from_rgb(255,255,255),
        )

        embed.add_field(name="Events", value=f"""
        **Raids:** {user_data['Raids']}
        **Defenses:** {user_data['Defenses']}
        **Defense Trainings:** {user_data['Defense Trainings']}
        **Prism Trainings:** {user_data['Prism Trainings']}

        """)

        avatar_image = robloxpy.User.External.GetBust(user['id'])
        print(avatar_image)
        embed.set_footer(text="Make your career great today!") # footers can have icons too
        embed.set_author(name="Ventis Group Datacenter", icon_url="https://i.imgur.com/YT9EJty.png")
        embed.set_thumbnail(url=avatar_image)
        embed.timestamp = datetime.datetime.now()
    
        await ctx.respond("Hello! Here's a cool embed.", embed=embed) # Send the embed with some text

def setup(bot):
    bot.add_cog(Progression(bot))