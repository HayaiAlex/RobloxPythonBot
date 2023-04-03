import datetime, os, robloxpy, discord, json
from discord.ext import commands
from lib.roblox.roblox_functions import get_roblox_ids, check_for_promotions, get_role_in_group
from lib.sql.queries import DB

with open('config.json', 'r') as file:
    config = json.load(file)
    
GROUP_ID = os.getenv('GROUP_ID')
db = DB()

events = ['Raid', 'Defense','Defense Training','Prism Training']
class Progression(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="award", description = "award an event to a group of users")
    async def award(self, ctx, event: discord.Option(str, choices=events), users: discord.Option(str, name="players")):
        users = [user for user in get_roblox_ids(users)]
       
        try:
            awarded = db.award(event,users)
            could_not_find = [user.get('username') for user in users if user.get('username').lower() not in [user.get('username').lower() for user in awarded]]
        except:
            awarded = []

        if len(awarded) > 0:
            award_msg = f"Awarded {', '.join([user.get('username') for user in awarded])} a {event.lower()} point!"
            could_not_find_msg = f"Could not find users {', '.join(could_not_find)}"

            if len(could_not_find) > 0:
                await ctx.respond(f"{award_msg}\n{could_not_find_msg}")
            else:
                await ctx.respond(f"{award_msg}")
          
            check_for_promotions([user.get('id') for user in awarded])
        else:
            await ctx.respond(f'No events awarded. Please check your player list.')


    @discord.slash_command(name="profile", description = "shows a user's career profile")
    async def profile(self, ctx, user: discord.Option(str,required=False)):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]
        try:
            user_data = db.get_data_from_id(user.get('id'))
            requirements = db.get_rank_requirements(db.get_user_rank(user['id']) + 1)
        except:
            user_data = {'User_ID': user, 'Rank_ID': 0, 'Raids': 0, 'Defenses': 0, 'Defense Trainings': 0, 'Prism Trainings': 0}
            requirements = db.get_rank_requirements(1)
         
        roles = get_role_in_group(user['id'], GROUP_ID)

        # Get events for next rank
        print(f'Requirements {requirements}')
        print(f'User data {user_data}')

        embed = discord.Embed(
            title=f"{user.get('username')}",
            url=f"https://www.roblox.com/users/{user['id']}/profile",
            color=discord.Colour.from_rgb(255,255,255),
        )

        # Set description
        description = f"""
            Rank: **{roles['name']}**
            """
        
        if 0 < user_data['Rank_ID'] < config['locked_ranks']:
            can_rank_up = True
        else:
            can_rank_up = False

        if can_rank_up:
            next_rank = db.get_rank(user_data['Rank_ID']+1)
            
            description += f"Next Rank: {next_rank['Rank_Name']}"

        if user_data['Rank_ID'] == 0:
            description += "Join the group to track your events and advance your Frostarian career."
        else:
            event_fields = ""
            for event in ['Raids','Defenses','Defense Trainings','Prism Trainings']:
                promotion_requirements = ""
                if can_rank_up:
                    promotion_requirements += f"**({requirements[event]})**"
                event_fields += f"**{event}:** {user_data[event]} {promotion_requirements}\n"

            event_field_name = "Events **(For Promotion)**" if can_rank_up else "Events"
            embed.add_field(name=event_field_name, value=event_fields)

        embed.description = description
        avatar_image = robloxpy.User.External.GetBust(user['id'])
        embed.set_footer(text="Make your career great today!")
        embed.set_author(name="Ventis Group Datacenter", icon_url="https://i.imgur.com/YT9EJty.png")
        embed.set_thumbnail(url=avatar_image)
        embed.timestamp = datetime.datetime.now()
    
        await ctx.respond("", embed=embed)

def setup(bot):
    bot.add_cog(Progression(bot))