import datetime
import os, discord, json
from discord.ext import commands
from lib.discord_functions import DiscordManager, send_could_not_find_user_msg
from lib.sql.queries import DB
from lib.roblox.roblox_functions import get_ordered_datastore_stat, get_roblox_ids
from lib.progression import check_for_promotions
from commands.progression.profile import Profile

with open('config.json', 'r') as file:
    config = json.load(file)
    
GROUP_ID = os.getenv('GROUP_ID')
db = DB()

def setup(bot):
    bot.add_cog(Update(bot))
    print("setup update commands")

class Update(commands.Cog):
    def __init__(self, bot:discord.Bot):
        self.bot = bot
        self.discord_manager = DiscordManager(bot)

    @discord.slash_command(name="update-player", description = "Updates a user's rank and roles")
    async def update_player(self, ctx: discord.ApplicationContext, 
                           user: discord.Option(str,required=False)):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]

        if user.get('id') == None:
            send_could_not_find_user_msg(ctx, user)
            return

        checking_embed = discord.Embed(
            title=f"Checking {user.get('username')}'s roles...",
            color=discord.Colour.from_rgb(255,255,255),
        )
        await ctx.respond(embed=checking_embed)
        
        # update their rank
        check_for_promotions([user.get('id')])
        # update their roles
        await self.discord_manager.update_roles(user)
        
        # edit preious sent message
        finished_embed = discord.Embed(
            title=f"Finished updating {user.get('username')}'s roles!",
            color=discord.Colour.from_rgb(255,255,255),
        )
        await ctx.interaction.edit_original_response(embed=finished_embed)
        

    @discord.slash_command(name="update-stats", description = "Updates all users' stats")
    async def update_roles(self, ctx: discord.ApplicationContext, 
                           user: discord.Option(str,required=False)):
        if user == None:
            user = ctx.user.mention
        user = get_roblox_ids(user)[0]
        
        if user.get('id') == None:
            send_could_not_find_user_msg(ctx, user)
            return

        checking_embed = discord.Embed(
            title=f"Updating {user.get('username')}'s stats...",
            color=discord.Colour.from_rgb(255,255,255),
        )
        await ctx.respond(embed=checking_embed)

        # update their stats
        prism_id = 4371347484

        stats = {'Solo_Aim_Trainer_Kills':'Solos', 'Spar_Sword_Kills':'SwordsKills', 'Spar_Sword_Wins':'SwordsWins', 'Spar_Gun_Kills':'GunsKills', 'Spar_Gun_Wins':'GunsWins'}
        for db_ref, stat in stats.items():
            value = get_ordered_datastore_stat(user.get('id'), prism_id, stat)
            try:
                if value is None:
                    value = 0
                db.set_user_stat(user.get('id'), db_ref, value)
            except Exception as e:
                print(e)


        # edit preious sent message on complete
        finished_embed = discord.Embed(
            title=f"Finished updating {user.get('username')}'s stats!",
            color=discord.Colour.from_rgb(255,255,255),
        )
        profile_embed = await Profile.get_profile_embed(user)
        await ctx.interaction.edit_original_response(embeds=[finished_embed, profile_embed])