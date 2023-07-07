import datetime, robloxpy, requests, os, discord
import json
from gsheets import Sheets
from discord.ext import tasks, commands
from discord.ext.pages import Paginator, Page
from lib.discord_functions import get_rover_data_from_roblox_id
from lib.roblox.roblox_functions import accept_join_request, decline_join_request, get_group_roles, get_avatar_thumbnail, get_recent_badges

GROUP_ID = os.getenv('GROUP_ID')
COOKIE = os.getenv('COOKIE')
with open('config.json', 'r') as file:
    config = json.load(file)

def setup(bot):
    bot.add_cog(JoinManager(bot))

class User():
    def __init__(self, user_data):
        self.id = user_data.get('userId')
        self.username = user_data.get('username')
        self.requested_at = user_data.get('requested_at')
        self.groups = None
        self.badges = None

class JoinManager(commands.Cog):
    def __init__(self, bot:discord.Bot):
        self.bot = bot
        self.check_join_requests.start()

    def cog_unload(self):
        self.check_join_requests.cancel()

    def get_join_requests(self):
        url = f'https://groups.roblox.com/v1/groups/{GROUP_ID}/join-requests?limit=50&sortOrder=Asc'
        request = requests.get(
            url,
            headers={'cookie': f'.ROBLOSECURITY={COOKIE}'})
        request = request.json()
        data = request.get('data')
        if not data:
            Exception('No data found')    
        return data
    
    @tasks.loop(seconds=60)
    async def check_join_requests(self):
        print('Checking join requests')
        try:
            join_requests = self.get_join_requests()
            for join_request in join_requests:
                user = User(join_request.get('requester'))
                user.requested_at = join_request.get('created')
                print(user)
                # check if join request is already in discord channel
                # if not, create join request view
                if await self.is_join_request_in_channel(user):
                    print(f"Found {user.username}")
                    continue
                else:
                    print("Creating join request view")
                    await self.create_join_request_view(user)
                    
        except:
            return

    @check_join_requests.before_loop
    async def before_check_join_requests(self):
        await self.bot.wait_until_ready()

    async def is_join_request_in_channel(self, user):
        print(f"Checking if {user.username} is in channel")
        channel = self.bot.get_channel(1046506345618210918)
        messages:list[discord.Message] = await channel.history(limit=50).flatten()
        for message in messages:
            if message.embeds and message.embeds[0].title == f'{user.username} has requested to join the group':
                if message.embeds[0].footer.text.find(self.format_request_time(user.requested_at)) == -1:
                    return False
                else:
                    return True
        return False

    async def create_join_request_view(self, user):
        print(f"Creating join request view for {user.username}")
        view = self.JoinRequestView(self.bot, user, [self.get_home_embed, self.get_groups_embed, self.get_badges_embed])
        channel = self.bot.get_channel(1046506345618210918)

        user.banned_groups = self.get_users_banned_groups(user)
        user.blacklisted = self.get_blacklist_status(user)
        user.rap = robloxpy.User.External.GetRAP(user.id)
        user.num_friends = robloxpy.User.Friends.External.GetCount(user.id)
        user.num_followers = robloxpy.User.Friends.External.GetFollowerCount(user.id)
        user.creation_date = robloxpy.User.External.CreationDate(user.id, 1)
        user.previous_usernames = robloxpy.User.External.UsernameHistory(user.id)
        month, day, year = user.creation_date.split('/')
        user.age = datetime.datetime.now() - datetime.datetime(int(year), int(month), int(day))
        user.age = f"{user.age.days // 365} years, {(user.age.days % 365) // 30} months, {user.age.days % 30} days"

        embed = await self.get_home_embed(user)
        await channel.send(embed=embed, view=view)

    def is_user_in_guild(self, user):
        print(f"Checking if user is in guild {user in self.bot.get_guild(GROUP_ID).members}")
        return user in self.bot.get_guild(GROUP_ID).members
    
    def format_request_time(self, time):
        return datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%m/%d/%Y at %I:%M %p')
    
    async def get_home_embed(self, user, embed_color=discord.Color.from_rgb(255,255,255)):
        description = ''
        
        banned_groups = user.banned_groups
        if banned_groups:
            description += "```diff\n-WARNING: This user is in a banned group\n"
            if len(banned_groups) > 1:
                description += f"-Banned Groups: {', '.join(banned_groups)}\n```\n"
            else:
                description += f"-Banned Group: {banned_groups[0]}\n```\n"

        if user.blacklisted in ['blacklisted', 'suspended']:
            description += f"```diff\n-WARNING: This user is {user.blacklisted}!\n-Check the [Justicars Database](https://docs.google.com/spreadsheets/d/1OC2tjU_TjYJMAriA2UxG9vhm01Ifv8ED_KYg6BykYQo/edit#gid=1547091865) for their record.\n```\n"

        if user.blacklisted == 'ccr':
            description += f"```diff\n-WARNING: This user is a potential cheater!\n```\n**Check their CCR record [here](https://ccr.catgang.ru/check.php?uid={user.id}).**\n"

        embed = discord.Embed(
            title=f'{user.username} has requested to join the group',
            url=f"https://www.roblox.com/users/{user.id}/profile",
            color=embed_color
        )

        if not user.previous_usernames:
            user.previous_usernames = ['None']

        description += "### Information\n"
        description += f"**Friends:** {user.num_friends}\n"
        description += f"**Followers:** {user.num_followers}\n"
        description += f"**RAP:** R$ {user.rap}\n"
        description += f"**Created:** {user.creation_date}\n"
        description += f"**Age:** {user.age}\n"
        description += f"**Previous Usernames:** {', '.join(user.previous_usernames)}\n"

        embed.description = description
        thumbnail = await get_avatar_thumbnail(user.id,"full")
        embed.set_image(url=thumbnail)
        embed.set_author(name="Office of Immigration", icon_url="https://i.imgur.com/ARh2iVP.png")
        embed.set_footer(text=f"Requested to join GUF on {self.format_request_time(user.requested_at)}")
        return embed
    
    async def get_groups_embed(self, user, page, embed_color=discord.Color.from_rgb(255,255,255)):
        description = ''

        banned_groups = user.banned_groups
        if banned_groups:
            description += "```diff\n-WARNING: This user is in a banned group\n"
            if len(banned_groups) > 1:
                description += f"-Banned Groups: {', '.join(banned_groups)}\n```\n"
            else:
                description += f"-Banned Group: {banned_groups[0]}\n```\n"


        embed = discord.Embed(
            title=f'{user.username} has requested to join the group',
            url=f"https://www.roblox.com/users/{user.id}/profile",
            color=embed_color
        )

        if len(user.groups) > 0:
            description += "**Groups**\n"            
        else:
            description += "**This user does not belong to any groups**\n"
            

        if len(user.groups) > 16:
            num_shown = page * 16 + 16
            if num_shown > len(user.groups):
                num_shown = len(user.groups)
            description += f"**Page {page + 1}** [{page * 16 + 1}-{num_shown}/{len(user.groups)}]\n"
            groups = user.groups[page * 16:page * 16 + 16]
        else:
            groups = user.groups

        for group in groups:
            description += f"**[{group['group']['name']}](https://www.roblox.com/groups/{group['group']['id']})**: {group['role']['name']}, Rank {group['role']['rank']}"
            if group['role']['rank'] == 255:
                icon = "<:HisokaSeal:1118224760636190812>\n"
            elif group['role']['rank'] > 10:
                icon = "<:HisokaSeal:1118224760636190812>\n"
            elif group['role']['rank'] > 1:
                icon = "<:AezijiSeal:1118224784598241380>\n"
            else:
                icon = "\n"
            description += icon

        embed.description = description
        thumbnail = await get_avatar_thumbnail(user.id,"full")
        embed.set_image(url=thumbnail)
        embed.set_author(name="Office of Immigration", icon_url="https://i.imgur.com/ARh2iVP.png")
        embed.set_footer(text=f"Requested to join GUF on {self.format_request_time(user.requested_at)}")
        return embed
    
    async def get_badges_embed(self, user, embed_color=discord.Color.from_rgb(255,255,255)):

        if not user.badges:
            user.badges = get_recent_badges(user.id)
        description = ''

        if user.banned_groups:
            description += "```diff\n-WARNING: This user is in a banned group\n"
            if len(user.banned_groups) > 1:
                description += f"-Banned Groups: {', '.join(user.banned_groups)}\n```\n"
            else:
                description += f"-Banned Group: {user.banned_groups[0]}\n```\n"


        embed = discord.Embed(
            title=f'{user.username} has requested to join the group',
            url=f"https://www.roblox.com/users/{user.id}/profile",
            color=embed_color
        )

        description += f"**Owned Badges: {'100+' if len(user.badges)==100 else len(user.badges)}**\n"
        if len(user.badges) > 1:
            description += "\n**Recent Badges**\n"
        for badge in user.badges[:15]:
            description += f"[{badge.get('name')}](https://www.roblox.com/games/{badge.get('awarder').get('id')})\n"

        embed.description = description
        thumbnail = await get_avatar_thumbnail(user.id,"full")
        embed.set_image(url=thumbnail)
        embed.set_author(name="Office of Immigration", icon_url="https://i.imgur.com/ARh2iVP.png")
        embed.set_footer(text=f"Requested to join GUF on {self.format_request_time(user.requested_at)}")
        return embed
    
    class JoinRequestView(discord.ui.View):
        def __init__(self, bot:discord.Bot, user, embeds):
            super().__init__(timeout=None)
            self.bot = bot
            self.user = user
            self.get_home_embed, self.get_groups_embed, self.get_badges_embed = embeds
            self.group_page = 0
            self.current_embed = None
            self.border_colour = discord.Color.from_rgb(255,255,255)

        def remove_group_page_buttons(self):
            remove_buttons = []
            for child in self.children:
                if child.custom_id == "⬅️" or child.custom_id == "➡️":
                    remove_buttons.append(child)
            for child in remove_buttons:
                self.remove_item(child)

        @discord.ui.button(emoji="🪪", row=0, style=discord.ButtonStyle.grey) 
        async def show_home(self, button:discord.ui.Button, interaction:discord.Interaction):
            self.remove_group_page_buttons()

            self.current_embed = self.get_home_embed
            home_embed = await self.get_home_embed(self.user, self.border_colour)
            await interaction.message.edit(embed=home_embed, view=self)
            await interaction.response.defer()

        @discord.ui.button(emoji="🌐", row=0, style=discord.ButtonStyle.grey) 
        async def show_groups(self, button, interaction, increment=0):
            try:
                num_groups = len(self.user.groups)
            except:
                self.user.groups = get_group_roles(self.user.id)
                num_groups = len(self.user.groups)     

            if num_groups > 16 and self.get_item("⬅️") is None:
                class PageButton(discord.ui.Button):
                    def __init__(self, view, emoji, label, increment):
                        super().__init__(emoji=emoji, style=discord.ButtonStyle.grey, custom_id=emoji, label=label)
                        self.increment = increment

                    async def callback(self, interaction:discord.Interaction):
                        new_page = self.view.group_page + self.increment
                        if new_page < 0:
                            new_page = 0
                        elif new_page > len(self.view.user.groups) // 16:
                            new_page = len(self.view.user.groups) // 16
                            
                        self.view.group_page = new_page    
                        self.view.current_embed = self.view.get_groups_embed
                        group_embed = await self.view.get_groups_embed(self.view.user, self.view.group_page, self.view.border_colour)
                        await interaction.message.edit(embed=group_embed, view=self.view)
                        await interaction.response.defer()

                self.add_item(PageButton(self, "⬅️", "Previous", -1))
                self.add_item(PageButton(self, "➡️", "Next", 1))
                
                self.group_page = 0

            self.current_embed = self.get_groups_embed
            group_embed = await self.get_groups_embed(self.user, self.group_page, self.border_colour)
            await interaction.message.edit(embed=group_embed, view=self)
            await interaction.response.defer()

        @discord.ui.button(emoji="🔰", row=0, style=discord.ButtonStyle.grey) 
        async def show_badges(self, button, interaction):
            self.remove_group_page_buttons()

            self.current_embed = self.get_badges_embed
            badge_embed = await self.get_badges_embed(self.user, self.border_colour)
            await interaction.message.edit(embed=badge_embed, view=self)
            await interaction.response.defer()
            pass

        @discord.ui.button(label="Decline", row=1, style=discord.ButtonStyle.danger, emoji="👎") 
        async def decline_button(self, button:discord.ui.Button, interaction:discord.Interaction):
            self.border_colour = discord.Color.from_rgb(255,40,40)
            self.remove_item(button)
            self.remove_item([i for i in self.children if i.label == "Accept"][0])

            result = decline_join_request(self.user.id)
            if result:
                label = f"{interaction.user.display_name} declined {self.user.username}"
                style = discord.ButtonStyle.danger
                emoji = "👎"
            else:
                label = f"This join request has already been handled"
                style = discord.ButtonStyle.grey
                emoji = "📝"

            self.add_item(discord.ui.Button(label=label, row=1, style=style, emoji=emoji, disabled=True))

            try:
                rover_member = get_rover_data_from_roblox_id(self.user.id)
                member = interaction.guild.get_member(rover_member['user']['id'])
                dm_channel = await self.bot.create_dm(member)
                await dm_channel.send(embed=discord.Embed(
                    title="Your join request was declined",
                    description=f"Your request to join The Grand Union of Frostaria was declined. If you believe this was a mistake, please contact an Admiral for more information.",
                    color=discord.Color.from_rgb(255,255,255)
                ))
            except:
                pass

            if not self.current_embed:
                updated_embed = await self.get_home_embed(self.user, self.border_colour)
            else:
                updated_embed = self.current_embed(self.user, self.border_colour)
            await interaction.message.edit(embed=updated_embed, view=self)
            await interaction.response.defer()

        @discord.ui.button(label="Accept", row=1, style=discord.ButtonStyle.green, emoji="👍") 
        async def accept_button(self, button, interaction:discord.Interaction):
            self.border_colour = discord.Color.from_rgb(40,255,40)
            self.remove_item(button)
            self.remove_item([i for i in self.children if i.label == "Decline"][0])

            result = accept_join_request(self.user.id)
            if result:
                label = f"{interaction.user.display_name} accepted {self.user.username}"
                style = discord.ButtonStyle.green
                emoji = "👍"
            else:
                label = f"This join request has already been handled"
                style = discord.ButtonStyle.grey
                emoji = "📝"

            self.add_item(discord.ui.Button(label=label, row=1, style=style, emoji=emoji, disabled=True))

            try:
                rover_member = get_rover_data_from_roblox_id(self.user.id)
                member = interaction.guild.get_member(rover_member['user']['id'])
                dm_channel = await self.bot.create_dm(member)
                await dm_channel.send(embed=discord.Embed(
                    title="Congratulations!",
                    description=f"Your request to join The Grand Union of Frostaria was accepted. Welcome to the group!",
                ))
            except:
                pass

            if not self.current_embed:
                updated_embed = await self.get_home_embed(self.user, self.border_colour)
            else:
                updated_embed = self.current_embed(self.user, self.border_colour)
            await interaction.message.edit(embed=updated_embed, view=self)
            await interaction.response.defer()


    def get_users_banned_groups(self, user):
        sheets = Sheets.from_files('./client_secrets.json', './storage.json')
        sheet = sheets['1OC2tjU_TjYJMAriA2UxG9vhm01Ifv8ED_KYg6BykYQo']
        banned_group_ids = sheet[412239904]['D11':'D50']

        url = f"https://groups.roblox.com/v1/users/{user.id}/groups/roles"
        request = requests.get(url)
        request = request.json()
        data = request.get('data')
        banned_groups = []
        for group in data:
            if group.get('group').get('id') in banned_group_ids:
                banned_groups.append(group.get('group').get('name'))
        return banned_groups

    def get_blacklist_status(self, user):        
        # Check if user is blacklisted in the database
        sheets = Sheets.from_files('./client_secrets.json', './storage.json')
        sheet = sheets['1OC2tjU_TjYJMAriA2UxG9vhm01Ifv8ED_KYg6BykYQo']
        blacklisted_users = sheet[1837621386]['C6':'C200']
        suspended_users = sheet[0]['C14':'C200']

        if user.id in [blacklisted_users]:
            return 'blacklisted'
        elif user.id in [suspended_users]:
            return 'suspended'
        
        # Check if user has a CCR record
        url = f"https://ccr.catgang.ru/check.php?uid={user.id}&format=json"
        request = requests.get(url)
        response = request.json()

        if response.get('accounts'):
            return 'ccr'
        else:
            return None
        
