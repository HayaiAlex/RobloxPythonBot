import datetime
import os, discord, json, robloxpy
from discord.ext import commands
from lib.roblox.roblox_functions import get_avatar_thumbnail, get_roblox_ids, get_role_in_group
from lib.discord_functions import send_could_not_find_user_msg
from lib.sql.queries import DB

with open('config.json', 'r') as file:
    config = json.load(file)
    
GROUP_ID = os.getenv('GROUP_ID')
db = DB()

def setup(bot):
    bot.add_cog(Profile(bot))

class Profile(commands.Cog):
    def __init__(self, bot:discord.Bot):
        self.bot = bot

    @discord.slash_command(name="profile", description = "shows a player's career profile")
    async def profile(self, ctx: discord.ApplicationContext, 
                      user: discord.Option(str,required=False, description='View your own or another player\'s profile')):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]

        if user.get('id') == None:
            send_could_not_find_user_msg(ctx, user)
            return
        
        embed = await self.get_profile_embed(user)
        await ctx.respond("", embed=embed)

    @classmethod                    
    async def get_profile_embed(cls, user):
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
            event_user_data = user_data.copy()
            for event in ['Raids','Defenses','Defense Trainings','Prism Trainings']:
                event_user_data = {key.replace("_"," "):value for key,value in event_user_data.items()}
                event_fields += f"**{event}:** {event_user_data[event]}\n"

            event_field_name = "Events"
            embed.add_field(name=event_field_name, value=event_fields)
    
        aim_trainer_kills = user_data.get('Solo_Aim_Trainer_Kills')
        embed.add_field(name="Aim Trainer", value=f"Solo: {aim_trainer_kills}")

        # Spar Stats
        spar_stat_fields = ""
        spar_stats = {'Spar_Gun_Kills':'Guns Kills', 'Spar_Gun_Wins':'Guns Wins', 'Spar_Sword_Kills':'Sword Kills', 'Spar_Sword_Wins':'Sword Wins'}
        for stat, label in spar_stats.items():
            value = user_data.get(stat)
            if value is None:
                value = 0
            spar_stat_fields += f"**{label}:** {value}\n"
        embed.add_field(name="Spar Stats", value=spar_stat_fields)

        commendations = db.get_user_commendations(user.get('id'))
        
        def get_commendation_field(commendation_type):
            if [commendation for commendation in commendations if commendation['Type'] == commendation_type]:
                result = ''
                for commendation in commendations:
                    if commendation['Type'] == commendation_type:
                        result += f"{commendation['Emote']} {commendation['Name']}"
                        if commendation['Quantity'] > 1:
                            result += f" **x{commendation['Quantity']}**"
                        result += "\n"
                return result            
            else:
                return f"No {commendation_type.lower()}s yet!"

        embed.add_field(name="Medals", value=get_commendation_field("Medal"))
        embed.add_field(name="Ribbons", value=get_commendation_field("Ribbon"))

        embed.description = description
        embed.set_footer(text="Make your career great today!")
        embed.set_author(name="Ventis Group Datacenter", icon_url="https://i.imgur.com/YT9EJty.png")
        avatar_image = await get_avatar_thumbnail(user.get('id'))
        embed.set_thumbnail(url=avatar_image)
        embed.timestamp = datetime.datetime.now()
        return embed    