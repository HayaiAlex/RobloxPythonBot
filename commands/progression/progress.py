import datetime
import os, discord, json, robloxpy
from discord.ext import commands
from lib.roblox.roblox_functions import get_avatar_thumbnail, get_roblox_ids, get_role_in_group, has_uniform
from lib.progression import get_top_rank
from lib.sql.queries import DB

with open('config.json', 'r') as file:
    config = json.load(file)
    
GROUP_ID = os.getenv('GROUP_ID')
db = DB()

def setup(bot):
    bot.add_cog(Progress(bot))

class Progress(commands.Cog):
    def __init__(self, bot:discord.Bot):
        self.bot = bot

    @discord.slash_command(name="progress", description = "shows what you need next to progress in your career")
    async def progress(self, ctx: discord.ApplicationContext,
                          user: discord.Option(str,required=False, description='View your own or another player\'s progress')):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]
        id = user.get('id')
        profile = db.get_data_from_id(id)
        embed = await self.get_progress_embed(user, top_rank=get_top_rank(profile))
        await ctx.respond("", embed=embed)
        
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
        avatar_image = await get_avatar_thumbnail(user.get('id'))
        embed.set_thumbnail(url=avatar_image)
        embed.timestamp = datetime.datetime.now()
        return embed
