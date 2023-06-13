import datetime, robloxpy, requests, os, discord
from gsheets import Sheets
from discord.ext import tasks, commands
from lib.roblox.roblox_functions import accept_join_request, decline_join_request, get_group_roles, get_avatar_thumbnail, get_recent_badges

GROUP_ID = os.getenv('GROUP_ID')
COOKIE = os.getenv('COOKIE')

def setup(bot):
    bot.add_cog(JoinManager(bot))

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
                user = join_request.get('requester')
                user['requested_at'] = join_request.get('created')
                print(user)
                # check if join request is already in discord channel
                # if not, create join request view
                if await self.is_join_request_in_channel(user):
                    continue
                else:
                    await self.create_join_request_view(user)
                    
        except:
            return

    @check_join_requests.before_loop
    async def before_check_join_requests(self):
        await self.bot.wait_until_ready()

    async def is_join_request_in_channel(self, user):
        username = user.get('username')
        print(f"Checking if {username} is in channel")
        channel = self.bot.get_channel(1046506345618210918)
        messages:list[discord.Message] = await channel.history(limit=50).flatten()
        for message in messages:
            if message.embeds and message.embeds[0].title == f'{username} has requested to join the group':
                if message.embeds[0].footer.text.find(self.format_request_time(user.get('requested_at'))) == -1:
                    return False
                else:
                    return True
        return False

    async def create_join_request_view(self, user):
        print("Creating join request view")
        view = self.JoinRequestView(user, self.get_home_embed, self.get_groups_embed, self.get_badges_embed)
        channel = self.bot.get_channel(1046506345618210918)


        user['banned_groups'] = self.get_users_banned_groups(user)
        user['rap'] = robloxpy.User.External.GetRAP(user.get('userId'))
        user['num_friends'] = robloxpy.User.Friends.External.GetCount(user.get('userId'))
        user['num_followers'] = robloxpy.User.Friends.External.GetFollowerCount(user.get('userId'))
        user['creation_date'] = robloxpy.User.External.CreationDate(user.get('userId'), 1)
        user['previous_usernames'] = robloxpy.User.External.UsernameHistory(user.get('userId'))
        print(user)
        embed = await self.get_home_embed(user)
        await channel.send(embed=embed, view=view)

    def is_user_in_guild(self, user):
        print(f"Checking if user is in guild {user in self.bot.get_guild(GROUP_ID).members}")
        return user in self.bot.get_guild(GROUP_ID).members
    
    def format_request_time(self, time):
        return datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%m/%d/%Y at %I:%M %p')
    
    async def get_home_embed(self, user):
        description = ''

        banned_groups = user.get('banned_groups')
        if banned_groups:
            description += "```diff\n-WARNING: This user is in a banned group\n"
            if len(banned_groups) > 1:
                description += f"-Banned Groups: {', '.join(banned_groups)}\n```\n"
            else:
                description += f"-Banned Group: {banned_groups[0]}\n```\n"

        embed = discord.Embed(
            title=f'{user.get("username")} has requested to join the group',
            url=f"https://www.roblox.com/users/{user.get('userId')}/profile",
            description=description,
            color=discord.Color.blurple()
        )

        if not user.get('previous_usernames'):
            user['previous_usernames'] = ['None']

        stats = f"""
        **Friends:** {user.get('num_friends')}
        **Followers:** {user.get('num_followers')}
        **RAP:** R$ {user.get('rap')}
        **Created:** {user.get('creation_date')}
        **Previous Usernames:** {', '.join(user.get('previous_usernames'))}
        """

        embed.add_field(name="Information", value=stats, inline=True)
        
        thumbnail = await get_avatar_thumbnail(user.get("userId"),"full")
        embed.set_image(url=thumbnail)
        embed.set_author(name="Ventis Group Datacenter", icon_url="https://i.imgur.com/YT9EJty.png")
        embed.set_footer(text=f"Requested to join GUF on {self.format_request_time(user.get('requested_at'))}")
        return embed
    
    async def get_groups_embed(self, user):

        if not user.get('groups'):
            user['groups'] = get_group_roles(user.get('userId'))

        description = ''

        banned_groups = user.get('banned_groups')
        if banned_groups:
            description += "```diff\n-WARNING: This user is in a banned group\n"
            if len(banned_groups) > 1:
                description += f"-Banned Groups: {', '.join(banned_groups)}\n```\n"
            else:
                description += f"-Banned Group: {banned_groups[0]}\n```\n"


        embed = discord.Embed(
            title=f'{user.get("username")} has requested to join the group',
            url=f"https://www.roblox.com/users/{user.get('userId')}/profile",
            color=discord.Color.blurple()
        )

        if len(user.get('groups')) > 1:
            description += "**Groups**\n"
        else:
            description += "**This user does not belong to any groups**\n"
        for group in user.get('groups'):
            description += f"**{group['group']['name']}**: {group['role']['name']}, Rank {group['role']['rank']} {'👍' if group['role']['rank'] > 2 else ''}\n"

        embed.description = description
        thumbnail = await get_avatar_thumbnail(user.get("userId"),"full")
        embed.set_image(url=thumbnail)
        embed.set_author(name="Ventis Group Datacenter", icon_url="https://i.imgur.com/YT9EJty.png")
        embed.set_footer(text=f"Requested to join GUF on {self.format_request_time(user.get('requested_at'))}")
        return embed
    
    async def get_badges_embed(self, user):

        if not user.get('badges'):
            user['badges'] = get_recent_badges(user.get('userId'))
        description = ''

        banned_groups = user.get('banned_groups')
        if banned_groups:
            description += "```diff\n-WARNING: This user is in a banned group\n"
            if len(banned_groups) > 1:
                description += f"-Banned Groups: {', '.join(banned_groups)}\n```\n"
            else:
                description += f"-Banned Group: {banned_groups[0]}\n```\n"


        embed = discord.Embed(
            title=f'{user.get("username")} has requested to join the group',
            url=f"https://www.roblox.com/users/{user.get('userId')}/profile",
            color=discord.Color.blurple()
        )

        description += f"**Owned Badges: {'100+' if len(user.get('badges'))==100 else len(user.get('badges'))}**\n"
        if len(user.get('badges')) > 1:
            description += "\n**Recent Badges**\n"
        for badge in user.get('badges')[:15]:
            description += f"{badge.get('name')}\n"

        embed.description = description
        thumbnail = await get_avatar_thumbnail(user.get("userId"),"full")
        embed.set_image(url=thumbnail)
        embed.set_author(name="Ventis Group Datacenter", icon_url="https://i.imgur.com/YT9EJty.png")
        embed.set_footer(text=f"Requested to join GUF on {self.format_request_time(user.get('requested_at'))}")
        return embed
    
    class JoinRequestView(discord.ui.View):
        def __init__(self, user, get_home_embed, get_groups_embed, get_badges_embed):
            super().__init__(timeout=None)
            self.user = user
            self.get_home_embed = get_home_embed
            self.get_groups_embed = get_groups_embed
            self.get_badges_embed = get_badges_embed
            self.current_embed = None

        @discord.ui.button(emoji="🪪", row=0, style=discord.ButtonStyle.blurple) 
        async def show_home(self, button:discord.ui.Button, interaction:discord.Interaction):
            home_embed = await self.get_home_embed(self.user)
            self.current_embed = home_embed
            await interaction.message.edit(embed=home_embed, view=self)
            await interaction.response.defer()

        @discord.ui.button(emoji="🌐", row=0, style=discord.ButtonStyle.blurple) 
        async def show_groups(self, button, interaction):
            group_embed = await self.get_groups_embed(self.user)
            self.current_embed = group_embed
            await interaction.message.edit(embed=group_embed, view=self)
            await interaction.response.defer()

        @discord.ui.button(emoji="🔰", row=0, style=discord.ButtonStyle.blurple) 
        async def show_badges(self, button, interaction):
            badges_embed = await self.get_badges_embed(self.user)
            self.current_embed = badges_embed
            await interaction.message.edit(embed=badges_embed, view=self)
            await interaction.response.defer()
            pass

        @discord.ui.button(label="Decline", row=1, style=discord.ButtonStyle.danger, emoji="👎") 
        async def decline_button(self, button:discord.ui.Button, interaction:discord.Interaction):
            self.remove_item(button)
            self.remove_item([i for i in self.children if i.label == "Accept"][0])

            self.add_item(discord.ui.Button(label=f"{interaction.user.display_name} declined {self.user.get('username')}", row=1, style=discord.ButtonStyle.danger, emoji="👎", disabled=True))

            decline_join_request(self.user.get('userId'))

            if not self.current_embed:
                self.current_embed = await self.get_home_embed(self.user)
            await interaction.message.edit(embed=self.current_embed, view=self)
            await interaction.response.defer()

        @discord.ui.button(label="Accept", row=1, style=discord.ButtonStyle.blurple, emoji="👍") 
        async def accept_button(self, button, interaction:discord.Interaction):
            self.remove_item(button)
            self.remove_item([i for i in self.children if i.label == "Decline"][0])

            self.add_item(discord.ui.Button(label=f"{interaction.user.display_name} accepted {self.user.get('username')}", row=1, style=discord.ButtonStyle.blurple, emoji="👍", disabled=True))

            accept_join_request(self.user.get('userId'))

            if not self.current_embed:
                self.current_embed = await self.get_home_embed(self.user)
            await interaction.message.edit(embed=self.current_embed, view=self)
            await interaction.response.defer()


    def get_users_banned_groups(self, user):
        sheets = Sheets.from_files('./client_secrets.json', './storage.json')
        sheet = sheets['1OC2tjU_TjYJMAriA2UxG9vhm01Ifv8ED_KYg6BykYQo']
        banned_group_ids = sheet[412239904]['D11':'D50']

        url = f"https://groups.roblox.com/v1/users/{user.get('userId')}/groups/roles"
        request = requests.get(url)
        request = request.json()
        data = request.get('data')
        banned_groups = []
        for group in data:
            if group.get('group').get('id') in banned_group_ids:
                banned_groups.append(group.get('group').get('name'))
        return banned_groups
