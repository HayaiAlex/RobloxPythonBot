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

    async def get_progress_embed(self, user, top_rank):
        roles = get_role_in_group(user['id'], GROUP_ID)

        try:
            user_data = db.get_data_from_id(user.get('id'))
        except:
            user_data = {'User_ID': user, 'Rank_ID': 0, 'Raids': 0, 'Defenses': 0, 'Defense_Trainings': 0, 'Prism_Trainings': 0, 'Spar_Gun_Wins': 0, 'Spar_Gun_Kills': 0, 'Spar_Sword_Wins': 0, 'Spar_Sword_Kills': 0, 'Solo_Aim_Trainer_Kills': 0, 'Passed_Exam': 0, 'Passed_MR_Vote': 0}
            
 

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

        # Set rank header
        if can_rank_up:
            next_rank = roles['rank']+1
            next_rank_name = robloxpy.Group.External.GetRoles(GROUP_ID)[0][robloxpy.Group.External.GetRoles(GROUP_ID)[1].index(next_rank)]
            description += f"Next Rank: {next_rank_name}"
        else:
            description += "You have progressed far in your career. Refer to the progression handbook for more information on how to rank up."

        if roles['rank'] == 0:
            description += "Join the group to track your events and advance your Frostarian career."

        # Set rank progress description
        if can_rank_up:
            description += "\n\n**Rank Progress**"

        print(f'Top Rank: {top_rank}')
        if top_rank == 1:
            description += f"""
            [{user_data['Defense_Trainings']}/1] Defense Training
            [{user_data['Prism_Trainings']}/1] Prism Training
            [{'X' if db.has_user_passed_entrance_exam(user.get('id')) else '_'}] Entrance Test Completed
            """
        elif top_rank == 2:
            description += f"""
            [{user_data['Defense_Trainings']}/4] Defense Training
            [{user_data['Prism_Trainings']}/4] Prism Training
            [{'X' if has_uniform(user) else '_'}] Have Uniform
            """

        elif top_rank == 3:
            description += f"""
            [{user_data['Raids'] + user_data['Defenses']}/2] Raids or Defenses
            [{user_data['Defense_Trainings'] + user_data['Prism_Trainings']}/13] Defense Trainings or Prism Trainings
            [{user['Solo_Aim_Trainer_Kills']}/60] High score on Prism solo aim trainer
            """

        elif top_rank == 4:
            description += f"""
            [{user_data['Raids'] + user_data['Defenses']}/8] Raids or Defenses of which [{user_data['Raids']}/3] must be Raids
            [{user_data['Defense_Trainings'] + user_data['Prism_Trainings']}/18] Defense Trainings or Prism Trainings
            [{user_data['Spar_Gun_Wins'] + user_data['Spar_Sword_Wins']}/25] Total Prism Spar Wins
            """

        elif top_rank == 5:
            description += f"""
            [{user_data['Raids'] + user_data['Defenses']}/16] Raids or Defenses of which [{user_data['Raids']}/7] must be Raids
            [{user_data['Defense_Trainings'] + user_data['Prism_Trainings']}/26] Defense Trainings or Prism Trainings

            [{'X' if db.has_user_passed_mr_vote(user.get('id')) else '_'}] Passed MR Vote 
            """

        embed.description = description
        embed.set_footer(text="Make your career great today!")
        embed.set_author(name="Ventis Group Datacenter", icon_url="https://i.imgur.com/YT9EJty.png")
        avatar_image = await get_avatar_thumbnail(user)
        embed.set_thumbnail(url=avatar_image)
        embed.timestamp = datetime.datetime.now()
        return embed


    async def get_profile_embed(self, user):
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
            next_rank = roles['rank']+1
            next_rank_name = robloxpy.Group.External.GetRoles(GROUP_ID)[0][robloxpy.Group.External.GetRoles(GROUP_ID)[1].index(next_rank)]
            description += f"Next Rank: {next_rank_name}"

        if roles['rank'] == 0:
            description += "Join the group to track your events and advance your Frostarian career."
        else:
            event_fields = ""
            for event in ['Raids','Defenses','Defense Trainings','Prism Trainings']:
                user_data = {key.replace("_"," "):value for key,value in user_data.items()}
                event_fields += f"**{event}:** {user_data[event]}\n"

            event_field_name = "Events"
            embed.add_field(name=event_field_name, value=event_fields)

        medals = db.get_user_medals(user.get('id'))
        
        if medals:
            formatted_medals = "\n".join([f"{medal['Emote']} {medal['Name']}" for medal in medals])
        else:
            formatted_medals = "No medals yet!"

        embed.add_field(name="Medals", value=formatted_medals)

        embed.description = description
        embed.set_footer(text="Make your career great today!")
        embed.set_author(name="Ventis Group Datacenter", icon_url="https://i.imgur.com/YT9EJty.png")
        avatar_image = await get_avatar_thumbnail(user)
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
                db.set_user_stat(self.user.get('id'), event, self.previous_stats[event])
            if self.event:
                db.award(self.event, [self.user])
                check_for_promotions([self.user])
            await interaction.response.send_message(f"Restoring {self.user.get('username')}'s stats")

    async def send_restore_stats_msg(self, user, event=None):
        channel = await self.bot.fetch_channel(1091380436715970561)

        embed = self.get_profile_embed(user)
        await channel.send("A returning player joined the server. The bot reset their stats. Restore stats?", embed=embed, view=self.RestoreStatsView(user, event))