import discord, requests, os
from lib.sql.queries import DB
db = DB()

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
