import os, discord, json
from discord.ext import commands
from lib.roblox.roblox_functions import get_roblox_ids, check_for_promotions
from lib.discord_functions import update_roles, send_reset_stats_msg
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
    async def award(self, ctx: discord.ApplicationContext, event: discord.Option(str, choices=events, description='Type of event hosted'), users: discord.Option(str, name="players", description='Those who attended the event')):
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
          
            promoted, skipped_ranks = check_for_promotions(ctx, [user.get('id') for user in awarded])

            for user in skipped_ranks:
                send_reset_stats_msg(ctx.guild, user, event)

            for user in promoted:
                update_roles(ctx, user)
        else:
            await ctx.respond(f'No events awarded. Please check your player list.')

    @discord.slash_command(name="profile", description = "shows a player's career profile")
    async def profile(self, ctx: discord.ApplicationContext, user: discord.Option(str,required=False, description='View your own or another player\'s profile')):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]
        
        embed = self.get_profile_embed(user)
        await ctx.respond("", embed=embed)

    @discord.slash_command(name="update", description = "updates a user's roles")
    async def update_roles(self, ctx: discord.ApplicationContext, user: discord.Option(str,required=False)):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]
        
        # update their rank
        check_for_promotions(ctx, [user.get('id')])
        # update their roles
        update_roles(ctx, user)

        await ctx.respond(f"Updated {user.get('username')}'s roles.")

    @discord.slash_command(name="setevent", description="manually set a player's events stats")
    async def set_events(self, ctx: discord.ApplicationContext, user: discord.Option(str, name="player", description="The person you would like to change event stats of"), event: discord.Option(str, choices=events, name="event", description="Type of event to set"), num: discord.Option(int, name="value", description="The new value for the event stat")):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]

        db.set_event(user.get('id'),event,num)

        await ctx.respond(f"Set {user.get('username')}'s {event} score to {num}.")


    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        # check if a member has pre-existing event scores and reset them
        guild = member.guild
        user = get_roblox_ids(member.mention)[0]
        try:
            profile = db.get_data_from_id(user.get('id'))
            has_events = [True for event in ['Raids','Defenses','Defense Trainings','Prism Trainings'] if profile[event] > 0]
            if not has_events:
                return
        except:
            return
        send_reset_stats_msg(guild, user)

def setup(bot):
    bot.add_cog(Progression(bot))