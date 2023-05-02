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
    bot.add_cog(Medals(bot))


class Medals(commands.Cog):
    medal_commands = discord.SlashCommandGroup("medal", "Medal Commands")
    role_commands = medal_commands.create_subgroup("role", "Role Commands")

    def __init__(self, bot:discord.Bot):
        self.bot = bot

    @medal_commands.command(name="create", description = "Create a new medal")
    async def create(self, ctx: discord.ApplicationContext, title: discord.Option(str,required=True, description='The title of the medal'), emote: discord.Option(str,required=False, description='The emoji symbol for this medal'), description: discord.Option(str,required=False, description='The medal description')):
        db.create_medal(title,description,emote)
        await ctx.respond(f"Created medal: {title}")

    class DeleteMedalView(discord.ui.View):
        def __init__(self, id, medal, embed: discord.Embed):
            super().__init__()
            self.id = id
            self.medal = medal
            self.embed = embed

        @discord.ui.button(label="Really Delete", style=discord.ButtonStyle.danger) 
        async def button_callback(self, button, interaction):
            db.delete_medal(self.id)
            self.clear_items()

            self.embed.title = "Deleted Medal"
            await interaction.response.edit_message(view=self, embed=self.embed)

        @discord.ui.button(label="Keep Medal", style=discord.ButtonStyle.blurple) 
        async def second_button_callback(self, button, interaction):
            self.clear_items()

            self.embed.title = "Kept Medal"
            await interaction.response.edit_message(view=self, embed=self.embed)
    
    @medal_commands.command(name="delete", description = "Delete a medal from the database")
    async def delete(self, ctx: discord.ApplicationContext, id: discord.Option(int, required=True, description='Medal ID')):
        medal = db.get_medal_info(id)

        embed = discord.Embed(
            title=f"Delete Medal",
            color=discord.Colour.from_rgb(255,0,0)
        )
        embed.add_field(name="Name",value=f"{medal['Emote']} {medal['Name']}")
        embed.add_field(name="Description",value=f"{medal['Description']}")
        await ctx.respond(embed=embed, view=self.DeleteMedalView(id, medal, embed))
    
    @medal_commands.command(name="award", description = "Award a medal to player(s)")
    async def awardMedal(self, ctx: discord.ApplicationContext, title: discord.Option(str,required=True, description='The title of the medal'), emote: discord.Option(str,required=False, description='The emoji symbol for this medal'), description: discord.Option(str,required=False, description='The medal description')):
        pass

    @medal_commands.command(name="unaward", description = "Unaward a medal from player(s)")
    async def unawardMedal(self, ctx: discord.ApplicationContext, title: discord.Option(str,required=True, description='The title of the medal'), emote: discord.Option(str,required=False, description='The emoji symbol for this medal'), description: discord.Option(str,required=False, description='The medal description')):
        pass

    @role_commands.command(name="assign", description = "Assign a role that will automatically be given to anyone who has this medal")
    async def assignRoleToMedal(self, ctx: discord.ApplicationContext, id: discord.Option(int, required=True, description='Medal ID'), role: discord.Option(str,required=True, description='The role ID')):
        pass

    @role_commands.command(name="remove", description = "Remove the link between a role and a medal")
    async def removeRoleFromMedal(self, ctx: discord.ApplicationContext, id: discord.Option(int, required=True, description='Medal ID')):
        pass