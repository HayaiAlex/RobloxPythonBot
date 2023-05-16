import datetime
import discord, requests, os, robloxpy, json
from lib.sql.queries import DB
from lib.roblox.roblox_functions import get_role_in_group, check_for_promotions

with open('config.json', 'r') as file:
    config = json.load(file)
db = DB()

GROUP_ID = os.getenv('GROUP_ID')
GUILD_ID = os.getenv('DISCORD_GUILD')

class DiscordManager():
    def __init__(self, bot:discord.Bot):
        self.bot = bot

    async def update_roles(self, user):
        # next, update their roles
        current_rank = db.get_user_rank(user.get('id'))
        print(f"Current rank: {current_rank}")
        guild:discord.Guild = await self.bot.fetch_guild(GUILD_ID)

        # get the rank name using robloxpy and the rank id
        ranks = robloxpy.Group.External.GetRoles(GROUP_ID)
        # (['Guest','Member','2nd Rank','3rd','Admin','Owner'],[0,1,2,3,254,255])
        rank_name = ranks[0][ranks[1].index(current_rank)]   
        print(f"Rank name: {rank_name}")
        
        print(guild)
        new_rank_role = discord.utils.get(guild.roles, name=rank_name)

        # user rover to get their discord id
        API = os.getenv('ROVERIFY_API')
        url = f"http://registry.rover.link/api/guilds/{GUILD_ID}/roblox-to-discord/{user.get('id')}"
        request = requests.get(url,headers={'Authorization': f"Bearer {API}"})
        response = request.json()
        users_discord_id = response['discordUsers'][0]['user']['id']

        discord_user = await guild.fetch_member(users_discord_id)

        # remove all rank roles that may or may not be incorrect
        rank_roles = [role for role in await guild.fetch_roles() if role.name in ranks[0]]
        print(rank_roles)
        await discord_user.remove_roles(*rank_roles)
        await discord_user.add_roles(new_rank_role)

    def get_profile_embed(self, user):
        roles = get_role_in_group(user['id'], GROUP_ID)

        try:
            user_data = db.get_data_from_id(user.get('id'))
        except:
            user_data = {'User_ID': user, 'Rank_ID': 0, 'Raids': 0, 'Defenses': 0, 'Defense_Trainings': 0, 'Prism_Trainings': 0}
            
            

        embed = discord.Embed(
            title=f"{user.get('username')}",
            url=f"https://www.roblox.com/users/{user['id']}/profile",
            color=discord.Colour.from_rgb(255,255,255),
        )

        # Set description
        description = f"""
            Rank: **{roles['name']}**
            """
        
        if 0 < roles['rank'] < config['locked_ranks']:
            can_rank_up = True
        else:
            can_rank_up = False

        if can_rank_up:
            next_rank = db.get_rank(roles['rank']+1)
            
            description += f"Next Rank: {next_rank['Rank_Name']}"

        if roles['rank'] == 0:
            description += "Join the group to track your events and advance your Frostarian career."
        else:
            event_fields = ""
            for event in ['Raids','Defenses','Defense Trainings','Prism Trainings']:
                promotion_requirements = ""
                if can_rank_up:
                    requirements = db.get_rank_requirements(roles['rank'] + 1)
                    promotion_requirements += f"**({requirements[event]})**"
                user_data = {key.replace("_"," "):value for key,value in user_data.items()}
                event_fields += f"**{event}:** {user_data[event]} {promotion_requirements}\n"

            event_field_name = "Events **(For Promotion)**" if can_rank_up else "Events"
            embed.add_field(name=event_field_name, value=event_fields)

        medals = db.get_user_medals(user.get('id'))
        print(medals)
        formatted_medals = "\n".join([f"{medal['Emote']} {medal['Name']}" for medal in medals])

        embed.add_field(name="Medals", value=formatted_medals)

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
                db.set_event(self.user.get('id'), event, self.previous_stats[event])
            if self.event:
                db.award(self.event, [self.user])
                check_for_promotions([self.user])
            await interaction.response.send_message(f"Restoring {self.user.get('username')}'s stats")

    async def send_restore_stats_msg(self, user, event=None):
        channel = await self.bot.fetch_channel(1091380436715970561)

        embed = self.get_profile_embed(user)
        await channel.send("A returning player joined the server. The bot reset their stats. Restore stats?", embed=embed, view=self.RestoreStatsView(user, event))