import os, discord, json, robloxpy
from discord.ext import commands
from lib.roblox.roblox_functions import get_avatar_thumbnail, get_roblox_ids, get_role_in_group
from lib.progression import check_for_promotions, get_top_rank
from lib.discord_functions import DiscordManager, send_could_not_find_user_msg
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

            await ctx.respond(embed=discord.Embed(
                title = f"Awarded {event} points",
                color = discord.Color.from_rgb(10,10,10)
            ))
            for user in awarded:
                awarded_embed = discord.Embed(
                    title = f"{user.get('username')}",
                    description = f"**{event}**\n{user.get('points')} points",
                    color = discord.Color.from_rgb(10,10,10)
                )
                awarded_embed.set_thumbnail(url=await get_avatar_thumbnail(user.get('id')))
                await ctx.respond(embed=awarded_embed)

            if len(could_not_find) > 0:
                could_not_find_embed = discord.Embed(
                    title = "Could not find users",
                    description = f"{', '.join(could_not_find)}",
                    color = discord.Color.red()
                )
                await ctx.respond(embed=could_not_find_embed)
          
            promoted, skipped_ranks = check_for_promotions([user.get('id') for user in awarded])

            for user in skipped_ranks:
                await discordManager.send_restore_stats_msg(user, event)

            for user in promoted:
                discordManager.update_roles(user)

            # check rank 5s have completed everything ready for a vote
            voting_channel = ctx.guild.get_channel(config['voting_channel'])
            for user in awarded:
                user_profile = db.get_data_from_id(user.get('id'))
                # rank 5.5 has completed all events and is now ready for/or currently doing their vote
                # rank 6 has completed all events and passed their vote
                if get_top_rank(user_profile) == 5.5:
                    # check if vote is already in progress
                    message_history = await voting_channel.history(limit=100).flatten() 
                    votum_motion = [message for message in message_history if message.content.startswith(f'!motion # Accept {user.get("username")} into the Frostarian Military')]
                        
                    # if not, give the command to start a votum motion
                    if not votum_motion:
                        need_vote_embed = discord.Embed(
                            title=f"{user.get('username')} is ready for a vote",
                            description=f"{ctx.guild.get_role(config['admiral_role']).mention} please copy and paste the below command to add the next MR vote\n!motion # Accept {user.get('username')} into the Frostarian Military",
                            color=discord.Color.from_rgb(255,255,255))
                        await voting_channel.send(embed=need_vote_embed)

        else:
            none_awarded_embed = discord.Embed(title=f"No events awarded. Please check your player list.", color=discord.Color.from_rgb(255,255,255))
            await ctx.respond(embed=none_awarded_embed)
            
    @discord.slash_command(name="test-vote", description="test the votum motion")
    async def test_vote(self, ctx: discord.ApplicationContext):
        voting_channel = ctx.guild.get_channel(config['voting_channel'])
        user = {'username': 'test_username', 'id': 1}
        # check if vote is already in progress
        message_history = await voting_channel.history(limit=100).flatten() 
        votum_motion = [message for message in message_history if message.content.startswith(f'!motion # Accept {user.get("username")} into the Frostarian Military')]
            
        # if not, give the command to start a votum motion
        if not votum_motion:
            need_vote_embed = discord.Embed(
                title=f"{user.get('username')} is ready for a vote",
                description=f"{ctx.guild.get_role(config['admiral_role']).mention} please copy and paste the below command to add the next MR vote\n!motion # Accept {user.get('username')} into the Frostarian Military",
                color=discord.Color.from_rgb(255,255,255))
            await ctx.respond(embed=need_vote_embed)
        else:
            await ctx.respond(embed=discord.Embed(title="Vote already in progress", color=discord.Color.from_rgb(255,255,255)))


    @discord.slash_command(name="set-event", description="manually set a player's events stats")
    async def set_events(self, ctx: discord.ApplicationContext, 
                         user: discord.Option(str, name="player", description="The person you would like to change event stats of"), 
                         event: discord.Option(str, choices=events, name="event", description="Type of event to set"), 
                         num: discord.Option(int, name="value", description="The new value for the event stat")):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]

        if user.get('id') == None:
            send_could_not_find_user_msg(ctx, user)
            return

        event_mapping = {'Raid': 'Raids', 'Defense': 'Defenses', 'Defense Training': 'Defense_Trainings', 'Prism Training': 'Prism_Trainings'}
        db.set_user_stat(user.get('id'),event_mapping[event],num)

        embed = discord.Embed(title=f"Set {user.get('username')}'s {event.lower()}s to {num}.", color=discord.Color.from_rgb(255,255,255))

        await ctx.respond(embed=embed)


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
