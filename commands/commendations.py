import os, discord
from discord.ext import commands
from discord.ext.pages import Paginator, Page
from lib.roblox.roblox_functions import get_roblox_ids, get_avatar_thumbnail
from lib.discord_functions import DiscordManager, get_discord_user
from lib.sql.queries import DB

GROUP_ID = os.getenv('GROUP_ID')
db = DB()
discordManager = None

def setup(bot):
    global discordManager
    discordManager = DiscordManager(bot)
    bot.add_cog(Commendations(bot))


class Commendations(commands.Cog):
    commendation_commands = discord.SlashCommandGroup("commendation", "Commendation Commands")
    role_commands = commendation_commands.create_subgroup("role", "Role Commands")

    def __init__(self, bot:discord.Bot):
        self.bot = bot

    @commendation_commands.command(name="list", description = "List all commendations")
    async def list(self, ctx: discord.ApplicationContext):
        commendations = db.get_all_commendations()
        commendations_per_page = 8
        commendation_by_page = []
        commendations.reverse()
        for (index, commendation) in enumerate(commendations):
            page = int(index/commendations_per_page)
            content = f"[{commendation['ID']}] **{commendation['Emote']} {commendation['Name']}**\n{commendation['Description']}"
            try:
                commendation_by_page[page].append(content)
            except:
                commendation_by_page.append([content])

        pages = []
        for (index, commendation_page) in enumerate(commendation_by_page):
            header = discord.Embed(
                color=discord.Colour.from_rgb(255,255,255)
            )
            header.set_image(url="https://i.imgur.com/qcAeijr.png")
            body = discord.Embed(
                description= "\n\n".join(commendation_page),
                color=discord.Colour.from_rgb(10,10,10)
            )
            pages.append(Page(embeds=[header, body]))

        paginator = Paginator(pages=pages)

        await paginator.respond(ctx.interaction)

    @commendation_commands.command(name="info", description = "Get info about a commendation")
    async def info(self, ctx: discord.ApplicationContext,
                     desired_commendation: discord.Option(str, name='commendation', description='The name or ID of the commendation')):
        
        commendation = self.get_commendation(desired_commendation)
        if commendation == None:
            await ctx.respond(f"Could not find commendation: {desired_commendation}")
            return
        commendation = db.get_commendation_info(commendation['ID'])
        
        embed = discord.Embed(
            color=discord.Colour.from_rgb(10,10,10)
        )

        description = f"## {commendation['Emote']} {commendation['Name']} {commendation['Type']}\n"
        description += commendation['Description']
        users = [user for user in get_roblox_ids(" ".join([str(id) for id in commendation['Users']]))]
        description += f"\n### Recipients"
        for user in users:
            # skips if user is banned
            if user.get('id') == None:
                continue

            description += f"\n{user.get('username')}"
            user_commendations = db.get_user_commendations(user.get('id'))
            amount = [comm['Quantity'] for comm in user_commendations if comm['ID'] == commendation['ID']][0]
            description += f" **x{amount}**" if amount > 1 else ""

        embed.description = description
        await ctx.respond(embed=embed)
        

    @commendation_commands.command(name="create", description = "Create a new commendation")
    async def create(self, ctx: discord.ApplicationContext, 
                     title: discord.Option(str,required=True, description='The title of the commendation'), 
                     comm_type: discord.Option(str,required=True, name='type', description='The type of commendation (medal or ribbon)', choices=["Medal","Ribbon"]),
                     emote: discord.Option(str,required=False, description='The emoji symbol for this commendation'), 
                     description: discord.Option(str,required=False, description='The commendation description')):
    
        db.create_commendation(title,description,emote,comm_type)
        await ctx.respond(f"Created commendation: {title}")

    class DeleteCommendationView(discord.ui.View):
        def __init__(self, id, commendation, embed: discord.Embed):
            super().__init__()
            self.id = id
            self.commendation = commendation
            self.embed = embed

        @discord.ui.button(label="Really Delete", style=discord.ButtonStyle.danger) 
        async def button_callback(self, button, interaction):
            db.delete_commendation(self.id)
            self.clear_items()

            self.embed.title = "Deleted Commendation"
            await interaction.response.edit_message(view=self, embed=self.embed)

        @discord.ui.button(label="Keep Commendation", style=discord.ButtonStyle.blurple) 
        async def second_button_callback(self, button, interaction):
            self.clear_items()

            self.embed.title = "Kept Commendation"
            await interaction.response.edit_message(view=self, embed=self.embed)
    
    @commendation_commands.command(name="delete", description = "Delete a commendation from the database")
    async def delete(self, ctx: discord.ApplicationContext, 
                     id: discord.Option(int, required=True, description='Commendation ID')):

        commendation = db.get_commendation_info(id)

        embed = discord.Embed(
            title=f"Delete Commendation",
            color=discord.Colour.from_rgb(255,0,0)
        )
        embed.add_field(name="Name",value=f"{commendation['Emote']} {commendation['Name']}")
        embed.add_field(name="Description",value=f"{commendation['Description']}")

        await ctx.respond(embed=embed, view=self.DeleteCommendationView(id, commendation, embed))

    def get_commendation(self, desired_commendation):  
        commendations = db.get_all_commendations()

        try:
            if desired_commendation.isdigit():
                return [comm for comm in commendations if comm['ID'] == int(desired_commendation)][0]
            else:
                return [comm for comm in commendations if comm['Name'].lower() == desired_commendation.lower()][0]
        except:            
            return None
    
    @commendation_commands.command(name="award", description = "Award a commendation to player(s)")
    async def awardCommendation(self, ctx: discord.ApplicationContext, 
                         desired_commendation: discord.Option(str, name='commendation', description='The name or ID of the commendation'), 
                         users: discord.Option(str, name='players', description='The name, ID, or @mention of the user to award the commendation to')):
        
        users = [user for user in get_roblox_ids(users)]
      
        commendation = self.get_commendation(desired_commendation)
        if commendation == None:
            await ctx.respond(f"Could not find a commendation with that id or name.")
            return

        embed = discord.Embed(
            color=discord.Colour.from_rgb(255,255,255)
        )

        for user in users:
            try:
                if user.get('id') == None:
                    embed.set_thumbnail(url="")
                    embed.description = f"### Could not find user {user.get('username')}!"
                    await ctx.respond(embed=embed)
                    continue

                result = db.award_commendation(user.get('id'), commendation['ID'])

                embed.set_thumbnail(url=await get_avatar_thumbnail(user.get('id')))

                if result == 'Success':
                    embed.description = f"### Awarded {commendation['Type']} {commendation['Emote']} {commendation['Name']}.\n Congratulation {user.get('username')}!"
                    await ctx.respond(embed=embed)
                else:
                    embed.description = f"### {user.get('username')} already has the {commendation['Emote']} {commendation['Name']} {commendation['Type'].lower()}."
                    await ctx.respond(embed=embed)

            except Exception as e:
                await ctx.respond(e)

    @commendation_commands.command(name="unaward", description = "Unaward a commendation from player(s)")
    async def unawardCommendation(self, ctx: discord.ApplicationContext, 
                         desired_commendation: discord.Option(str, name='commendation', description='The name or ID of the commendation'), 
                         users: discord.Option(str, name='players', description='The name, ID, or @mention of the user to award the commendation to'),
                         amount: discord.Option(int, name='amount', description='The amount of times to unaward the commendation') = 1):
        
        users = [user for user in get_roblox_ids(users)]
        
        commendation = self.get_commendation(desired_commendation)
        if commendation == None:
            await ctx.respond(f"Could not find a commendation with that id or name.")
            return
        
        embed = discord.Embed(
            color=discord.Colour.from_rgb(255,255,255)
        )

        for user in users:
            try:
                if user.get('id') == None:
                    embed.set_thumbnail(url="")
                    embed.description = f"### Could not find user {user.get('username')}!"
                    await ctx.respond(embed=embed)
                    continue

                result = db.unaward_commendation(user.get('id'), commendation['ID'], amount)
                embed.set_thumbnail(url=await get_avatar_thumbnail(user.get('id')))

                if result['status'] == 'Success':
                    if amount == 1:
                        embed.description = f"### {user.get('username')} has lost the {commendation['Type']} {commendation['Emote']} {commendation['Name']}."
                    else:
                        embed.description = f"### {user.get('username')} has lost {result['unawarded_count']} {commendation['Type']}s of {commendation['Emote']} {commendation['Name']}."
                else:
                    embed.description = f"### {user.get('username')} does not have the {commendation['Emote']} {commendation['Name']} {commendation['Type'].lower()}."
                await ctx.respond(embed=embed)

            except Exception as e:
                await ctx.respond(e)



    @role_commands.command(name="assign", description = "Assign a role that will automatically be given to anyone who has this commendation")
    async def assignRoleToCommendation(self, ctx: discord.ApplicationContext, 
                                comm_id: discord.Option(int, name='commendation-id', description='Commendation ID'), 
                                role: discord.Option(str, description='The role ID')):
        role = int(role)
        # Check if the role is valid
        if ctx.guild.get_role(role) == None:
            await ctx.respond(f"Could not find a role with that id.")
            return

        # Check if the commendation is valid
        try:
            commendation_data = db.get_commendation_info(comm_id)
            previous_role = commendation_data['Role ID']
        except:
            await ctx.respond(f"Could not find a commendation with that id.")
            return
        
        # Assign the role to the commendation
        db.assign_role_to_commendation(comm_id, role)

        # Update roles for all users with the commendation
        # Note: Check that previously assigned comm roles are correctly removed
        for user in commendation_data['Users']:
            print(type(user))
            print(user)
            try:
                print("Trying to add role")
                member = await get_discord_user(ctx.guild, user)
                print(member)
                if member == None:
                    continue
                await member.add_roles(ctx.guild.get_role(role))
                print("Added role")
                if previous_role != None and previous_role != role:
                    await member.remove_roles(ctx.guild.get_role(previous_role))
                    print("Removed old role")
            except:
                print("Something went wrong")
        
        await ctx.respond(f"Successfully assigned role {ctx.guild.get_role(role).mention} to commendation **{commendation_data['Name']}**")

    @role_commands.command(name="remove", description = "Remove the link between a role and a commendation")
    async def removeRoleFromCommendation(self, ctx: discord.ApplicationContext, 
                                  comm_id: discord.Option(int, name='commendation-id', description='Commendation ID')):
        
        # Check if the commendation is valid
        try:
            commendation_data = db.get_commendation_info(comm_id)
            previous_role = commendation_data['Role ID']
        except:
            await ctx.respond(f"Could not find a commendation with that id.")
            return
        
        # Remove the role from the commendation
        db.remove_role_from_commendation(comm_id)

        # Update roles for all users with the commendation
        for user in commendation_data['Users']:
            try:
                member = await get_discord_user(ctx.guild, user)
                if member == None:
                    continue
                await member.remove_roles(ctx.guild.get_role(previous_role))
            except:
                continue

        await ctx.respond(f"Successfully removed role {ctx.guild.get_role(previous_role).mention} from commendation **{commendation_data['Name']}**")