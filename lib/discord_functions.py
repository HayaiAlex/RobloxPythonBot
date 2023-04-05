import datetime
import discord, requests, os, robloxpy, json
from lib.sql.queries import DB
from lib.roblox.roblox_functions import get_role_in_group

with open('config.json', 'r') as file:
    config = json.load(file)
db = DB()

GROUP_ID = os.getenv('GROUP_ID')

async def update_roles(ctx, user):
    # next, update their roles
    current_rank = db.get_user_rank(user.get('id'))
    new_rank_role = discord.utils.get(ctx.guild.roles, name=current_rank['Rank_Name'])

    # user rover to get their discord id
    API = os.getenv('ROVERIFY_API')
    GUILD_ID = os.getenv('DISCORD_GUILD')
    url = f"http://registry.rover.link/api/guilds/{GUILD_ID}/roblox-to-discord/{user.get('id')}"
    request = requests.get(url,headers={'Authorization': f"Bearer {API}"})
    response = request.json()
    users_discord_id = response['discordUsers'][0]['user']['id']

    discord_user = await ctx.guild.fetch_member(users_discord_id)

    # remove all rank roles that may or may not be incorrect
    ranks = [rank['Rank_Name'] for rank in db.get_all_ranks()]
    rank_roles = [role for role in await ctx.guild.fetch_roles() if role.name in ranks]
    print(rank_roles)
    await discord_user.remove_roles(*rank_roles)
    await discord_user.add_roles(new_rank_role)

def get_profile_embed(user):
    try:
        user_data = db.get_data_from_id(user.get('id'))
        requirements = db.get_rank_requirements(int(db.get_user_rank(user['id'])['Rank_ID']) + 1)
    except:
        user_data = {'User_ID': user, 'Rank_ID': 0, 'Raids': 0, 'Defenses': 0, 'Defense Trainings': 0, 'Prism Trainings': 0}
        requirements = db.get_rank_requirements(1)
        
    roles = get_role_in_group(user['id'], GROUP_ID)

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
    return embed    

class ResetStatsView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    def __init__(self, user, event=None):
        super().__init__()
        self.user = user
        self.event = event

    @discord.ui.button(label="Reset Stats", style=discord.ButtonStyle.danger, emoji="🪖") # Create a button with the label "🪖 Reset Stats!" with color Blurple
    async def button_callback(self, button, interaction):
        db.reset_events(self.user.get('id'))
        if self.event:
            db.award(self.event, [self.user])
        await interaction.response.send_message(f"Reseting {self.user.get('username')}'s stats") # Send a message when the button is clicked

async def send_reset_stats_msg(guild, user, event=None):
    channel = await guild.fetch_channel(1091380436715970561)

    embed = get_profile_embed(user)
    await channel.send("A returning player joined the server. Reset their stats?", embed=embed, view=ResetStatsView(user, event)) # Send a message with our View class that contains the button