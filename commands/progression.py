import os, discord, json, robloxpy
from discord.ext import commands
from lib.roblox.roblox_functions import get_roblox_ids, get_role_in_group
from lib.progression import check_for_promotions, get_top_rank
from lib.discord_functions import DiscordManager
from lib.sql.queries import DB

with open('config.json', 'r') as file:
    config = json.load(file)
    
events = ['Raid', 'Defense','Defense Training','Prism Training']
GROUP_ID = os.getenv('GROUP_ID')
db = DB()
discordManager = None

def setup(bot):
    global discordManager
    discordManager = DiscordManager(bot)
    bot.add_cog(Progression(bot))

class Progression(commands.Cog):
    def __init__(self, bot:discord.Bot):
        self.bot = bot

    @discord.slash_command(name="award", description = "award an event to a group of users")
    async def award(self, ctx: discord.ApplicationContext, 
                    event: discord.Option(str, choices=events, description='Type of event hosted'), 
                    users: discord.Option(str, name="players", description='Those who attended the event')):
        users = [user for user in get_roblox_ids(users)]

        try:
            awarded = db.award(event,users)
            could_not_find = [user.get('username') for user in users if user.get('username').lower() not in [user.get('username').lower() for user in awarded]]
        except:
            print('something happened')
            awarded = []

        if len(awarded) > 0:
            award_msg = f"Awarded {', '.join([user.get('username') for user in awarded])} a {event.lower()} point!"
            could_not_find_msg = f"Could not find users {', '.join(could_not_find)}"

            if len(could_not_find) > 0:
                await ctx.respond(f"{award_msg}\n{could_not_find_msg}")
            else:
                await ctx.respond(f"{award_msg}")
          
            promoted, skipped_ranks = check_for_promotions([user.get('id') for user in awarded])

            for user in skipped_ranks:
                await discordManager.send_restore_stats_msg(user, event)

            for user in promoted:
                discordManager.update_roles(user)
        else:
            await ctx.respond(f'No events awarded. Please check your player list.')

    @discord.slash_command(name="profile", description = "shows a player's career profile")
    async def profile(self, ctx: discord.ApplicationContext, 
                      user: discord.Option(str,required=False, description='View your own or another player\'s profile')):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]
        
        embed = await discordManager.get_profile_embed(user)
        await ctx.respond("", embed=embed)

    @discord.slash_command(name="progress", description = "shows what you need next to progress in your career")
    async def progress(self, ctx: discord.ApplicationContext,
                          user: discord.Option(str,required=False, description='View your own or another player\'s progress')):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]
        id = user.get('id')
        profile = db.get_data_from_id(id)
        embed = await discordManager.get_progress_embed(user, top_rank=get_top_rank(profile))
        await ctx.respond("", embed=embed)

    @discord.slash_command(name="update", description = "updates a user's roles")
    async def update_roles(self, ctx: discord.ApplicationContext, 
                           user: discord.Option(str,required=False)):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]
        await ctx.respond(f"Checking {user.get('username')}...")
        
        # update their rank
        check_for_promotions([user.get('id')])
        # update their roles
        await discordManager.update_roles(user)
        
        # edit preious sent message
        await ctx.interaction.edit_original_response(content=f"Updated {user.get('username')}'s roles.")
        

    @discord.slash_command(name="setevent", description="manually set a player's events stats")
    async def set_events(self, ctx: discord.ApplicationContext, 
                         user: discord.Option(str, name="player", description="The person you would like to change event stats of"), 
                         event: discord.Option(str, choices=events, name="event", description="Type of event to set"), 
                         num: discord.Option(int, name="value", description="The new value for the event stat")):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]

        db.set_user_stat(user.get('id'),event,num)

        await ctx.respond(f"Set {user.get('username')}'s {event} score to {num}.")


    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        # check if a member has pre-existing event scores and reset them
        user = get_roblox_ids(member.mention)[0]
        try:
            profile = db.get_data_from_id(user.get('id'))
            has_events = [True for event in ['Raids','Defenses','Defense_Trainings','Prism_Trainings'] if profile[event] > 0]
            if not has_events:
                return
        except:
            return
        await discordManager.send_restore_stats_msg(user)
