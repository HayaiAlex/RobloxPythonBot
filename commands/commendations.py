import os, discord, json
from discord.ext import commands
from lib.roblox.roblox_functions import get_roblox_ids
from lib.discord_functions import DiscordManager
from lib.sql.queries import DB

GROUP_ID = os.getenv('GROUP_ID')
db = DB()
discordManager = None

def setup(bot):
    global discordManager
    discordManager = DiscordManager(bot)
    bot.add_cog(Commendations(bot))


class Commendations(commands.Cog):
    commendation_commands = discord.SlashCommandGroup("commendation", "Medal Commands")
    role_commands = commendation_commands.create_subgroup("role", "Role Commands")

    def __init__(self, bot:discord.Bot):
        self.bot = bot

    @commendation_commands.command(name="create", description = "Create a new commendation")
    async def create(self, ctx: discord.ApplicationContext, 
                     title: discord.Option(str,required=True, description='The title of the commendation'), 
                     emote: discord.Option(str,required=False, description='The emoji symbol for this commendation'), 
                     description: discord.Option(str,required=False, description='The commendation description')):
        
        db.create_commendation(title,description,emote)
        await ctx.respond(f"Created commendation: {title}")

    class DeleteMedalView(discord.ui.View):
        def __init__(self, id, commendation, embed: discord.Embed):
            super().__init__()
            self.id = id
            self.commendation = commendation
            self.embed = embed

        @discord.ui.button(label="Really Delete", style=discord.ButtonStyle.danger) 
        async def button_callback(self, button, interaction):
            db.delete_commendation(self.id)
            self.clear_items()

            self.embed.title = "Deleted Medal"
            await interaction.response.edit_message(view=self, embed=self.embed)

        @discord.ui.button(label="Keep Medal", style=discord.ButtonStyle.blurple) 
        async def second_button_callback(self, button, interaction):
            self.clear_items()

            self.embed.title = "Kept Medal"
            await interaction.response.edit_message(view=self, embed=self.embed)
    
    @commendation_commands.command(name="delete", description = "Delete a commendation from the database")
    async def delete(self, ctx: discord.ApplicationContext, 
                     id: discord.Option(int, required=True, description='Medal ID')):

        commendation = db.get_commendation_info(id)

        embed = discord.Embed(
            title=f"Delete Medal",
            color=discord.Colour.from_rgb(255,0,0)
        )
        embed.add_field(name="Name",value=f"{commendation['Emote']} {commendation['Name']}")
        embed.add_field(name="Description",value=f"{commendation['Description']}")

        await ctx.respond(embed=embed, view=self.DeleteMedalView(id, commendation, embed))
    
    @commendation_commands.command(name="award", description = "Award a commendation to player(s)")
    async def awardMedal(self, ctx: discord.ApplicationContext, 
                         title: discord.Option(str,required=True, description='The title of the commendation'), 
                         emote: discord.Option(str,required=False, description='The emoji symbol for this commendation'), 
                         description: discord.Option(str,required=False, description='The commendation description')):
        pass

    @commendation_commands.command(name="unaward", description = "Unaward a commendation from player(s)")
    async def unawardMedal(self, ctx: discord.ApplicationContext, 
                           title: discord.Option(str,required=True, description='The title of the commendation'), 
                           emote: discord.Option(str,required=False, description='The emoji symbol for this commendation'), description: discord.Option(str,required=False, description='The commendation description')):
        pass

    @role_commands.command(name="assign", description = "Assign a role that will automatically be given to anyone who has this commendation")
    async def assignRoleToMedal(self, ctx: discord.ApplicationContext, 
                                id: discord.Option(int, required=True, description='Medal ID'), 
                                role: discord.Option(str,required=True, description='The role ID')):
        pass

    @role_commands.command(name="remove", description = "Remove the link between a role and a commendation")
    async def removeRoleFromMedal(self, ctx: discord.ApplicationContext, 
                                  id: discord.Option(int, required=True, description='Medal ID')):
        pass