import discord
from discord.ext import commands
from lib.roblox.roblox_functions import get_role_in_group, get_usernames_from_ids
from lib.sql.queries import DB

db = DB()


def setup(bot):
    bot.add_cog(Provinces(bot))


class Provinces(commands.Cog):
    def __init__(self, bot:discord.Bot):
        self.bot = bot

    @discord.slash_command(name="province", description = "Get information about a province")
    async def province_info(self, ctx: discord.ApplicationContext, province: discord.Option(str, name='province', description='Province name')):
        province = db.get_province(province)

        if province is None:
            await ctx.respond(embed=discord.Embed(title="Province not found", description="The province you are looking for does not exist", color=discord.Color.from_rgb(255, 255, 255)))
            return
        
        embed = discord.Embed(
            title=province['Name'], 
            description=province['Description'], 
            color=discord.Color.from_rgb(255, 255, 255)
            )
        try:
            embed.set_image(url=province['Image Url'])
        except:
            pass
        embed.add_field(name="Prestige", value=province['Prestige'], inline=True)
        
        try:
            
            leader = f"{get_role_in_group(province['Leader ID'])['name']} {get_usernames_from_ids([province['Leader ID']])[0]['username'].capitalize()}"
            print(leader)
            embed.add_field(name="Governor", value=leader, inline=True)
        except:
            embed.add_field(name="Governor", value="This area has no Admiral governing it.", inline=True)

        embed.add_field(name="Population", value="", inline=True)
        embed.add_field(name="Capital", value="", inline=True)
        embed.add_field(name="Area", value="", inline=True)
        embed.add_field(name="Major Cities", value="", inline=True)

        await ctx.respond(embed=embed)