import datetime
import discord, requests, os, robloxpy, json
from lib.progression import check_for_promotions
from lib.sql.queries import DB
from lib.roblox.roblox_functions import get_avatar_thumbnail, get_role_in_group, has_uniform

with open('config.json', 'r') as file:
    config = json.load(file)
db = DB()

GROUP_ID = os.getenv('GROUP_ID')
GUILD_ID = os.getenv('DISCORD_GUILD')

def get_rover_data_from_roblox_id(user_id):
    API = os.getenv('ROVERIFY_API')
    url = f"http://registry.rover.link/api/guilds/{GUILD_ID}/roblox-to-discord/{user_id}"
    request = requests.get(url,headers={'Authorization': f"Bearer {API}"})
    response = request.json()
    if request.status_code == 200:
        return response['discordUsers'][0]
    return {}

async def send_could_not_find_user_msg(self, ctx, user):
    await ctx.respond(embed=discord.Embed(title=f"Could not find player {user}", color=discord.Colour.from_rgb(255,255,255)))
    
async def get_discord_user(guild, user_id):
    print('getting discord user')
    # user rover to get their discord id
    API = os.getenv('ROVERIFY_API')
    url = f"http://registry.rover.link/api/guilds/{GUILD_ID}/roblox-to-discord/{user_id}"
    request = requests.get(url,headers={'Authorization': f"Bearer {API}"})
    print(request)
    response = request.json()
    print(response)
    users_discord_id = response['discordUsers'][0]['user']['id']
    print(users_discord_id)
    return await guild.fetch_member(users_discord_id)

class DiscordManager():
    def __init__(self, bot:discord.Bot):
        self.bot = bot

    async def update_roles(self, user):
        current_rank = db.get_user_rank(user.get('id'))
        print(f"Current rank: {current_rank}")
        guild:discord.Guild = await self.bot.fetch_guild(GUILD_ID)

        # get the rank name using robloxpy and the rank id
        ranks = robloxpy.Group.External.GetRoles(GROUP_ID)
        # (['Guest','Member','2nd Rank','3rd','Admin','Owner'],[0,1,2,3,254,255])
        rank_name = ranks[0][ranks[1].index(current_rank)]   
        print(f"Rank name: {rank_name}")
        
        new_rank_role = discord.utils.get(guild.roles, name=rank_name)
    
        discord_user = await get_discord_user(guild, user.get('id'))

        # remove all rank roles that may or may not be incorrect
        rank_roles = [role for role in await guild.fetch_roles() if role.name in ranks[0]]
        await discord_user.remove_roles(*rank_roles)
        await discord_user.add_roles(new_rank_role)

        # update commendation roles
        # get all commendation roles
        commendation_role_ids = [comm['Role ID'] for comm in db.get_all_commendations() if comm['Role ID'] != None]
        # get all commendations the user has that have a role
        user_commendation_ids = [comm['Role ID'] for comm in db.get_user_commendations(user.get('id')) if comm['Role ID'] != None]

        # remove all commendation roles that may or may not be incorrect
        guild_roles = await guild.fetch_roles()
        commendation_roles = [role for role in guild_roles if role.id in commendation_role_ids]
        await discord_user.remove_roles(*commendation_roles)
        # add the commendation roles the user has
        commendation_roles = [role for role in guild_roles if role.id in user_commendation_ids]
        await discord_user.add_roles(*commendation_roles)

    class ResetStatsView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
        def __init__(self, user, event=None):
            super().__init__()
            self.user = user
            self.event = event

        @discord.ui.button(label="Reset Stats", style=discord.ButtonStyle.danger, emoji="🪖") #
        async def button_callback(self, button, interaction):
            db.reset_events(self.user.get('id'))
            if self.event:
                db.award(self.event, [self.user])
            await interaction.response.send_message(f"Reseting {self.user.get('username')}'s stats")

    async def send_reset_stats_msg(self, user, event=None):
        channel = await self.bot.fetch_channel(1091380436715970561)

        embed = self.get_profile_embed(user)
        await channel.send("A returning player joined the server. Reset their stats?", embed=embed, view=self.ResetStatsView(user, event)) 

    class RestoreStatsView(discord.ui.View):
        def __init__(self, user, event=None):
            super().__init__()
            self.previous_stats = db.get_data_from_id(user.get('id'))
            self.user = user
            self.event = event
            db.reset_events(self.user.get('id'))
            if event:
                db.award(self.event, [self.user])

        @discord.ui.button(label="Restore Stats", style=discord.ButtonStyle.blurple, emoji="🪖") 
        async def button_callback(self, button, interaction):
            for event in ['Raids','Defenses','Defense_Trainings','Prism_Trainings']:
                db.set_user_stat(self.user.get('id'), event, self.previous_stats[event])
            if self.event:
                db.award(self.event, [self.user])
                check_for_promotions([self.user])
            await interaction.response.send_message(f"Restoring {self.user.get('username')}'s stats")

    async def send_restore_stats_msg(self, user, event=None):
        channel = await self.bot.fetch_channel(1091380436715970561)

        embed = self.get_profile_embed(user)
        alert_embed = discord.Embed(title=f"Restore {user.get('username')} stats?",
                                    description= f"It looks like {user.get('username')} is a returning player. The bot has reset their stats. Do you wish to keep their previous progress?", 
                                    color=discord.Colour.from_rgb(255,255,255))
        await channel.send(embeds=[alert_embed,embed], view=self.RestoreStatsView(user, event))
