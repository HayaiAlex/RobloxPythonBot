import asyncio
import json
import robloxpy, os, discord
from discord.ext import commands

GROUP_ID = os.getenv('GROUP_ID')
COOKIE = os.getenv('COOKIE')
with open('config.json', 'r') as file:
    config = json.load(file)

def setup(bot):
    bot.add_cog(RoleManager(bot))

class RoleManager(commands.Cog):
    def __init__(self, bot:discord.Bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):

        role_channel_id = config.get('role_channel_id')
        self.role_channel = self.bot.get_channel(role_channel_id)

        self.bot.add_view(self.TimezoneView())

        await self.setup_role_channel()

    async def setup_role_channel(self):
        # check if role channel exists
        if self.role_channel is None:
            print("Role channel does not exist")
            return
        
        # check if role channel has no messages
        if len(await self.role_channel.history(limit=1).flatten()) != 0:
            print("Role channel is not empty")
            # find role message
            message_history = await self.role_channel.history(limit=2).flatten()
            self.role_message = message_history[1]
            return
        
        # if role channel is empty and exists, send message
        notification_embed = discord.Embed(
            title = "Which notifications would you like to receive?",
            description="👪 - Community Announcements\n🎲 - Game Nights\n🌳 - Minecraft\n🔨 - Dev Updates",
            color = discord.Color.from_rgb(255,255,255)
        )

        timezone_embed = discord.Embed(
            title = "Please select your timezone",
            color = discord.Color.from_rgb(255,255,255)
        )

        await self.role_channel.send(embed=notification_embed)
        last_message = await self.role_channel.history(limit=1).flatten()
        last_message = last_message[0]
        await last_message.add_reaction('👪')
        await last_message.add_reaction('🎲')
        await last_message.add_reaction('🌳')
        await last_message.add_reaction('🔨')
        self.role_message = last_message
        await self.role_channel.send(embed=timezone_embed, view=self.TimezoneView())

    # on reaction added
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload:discord.RawReactionActionEvent):
        # check if reaction is from bot
        if payload.user_id == self.bot.user.id:
            return
        
        # check if reaction is from role channel
        if payload.message_id != self.role_message.id:
            return
        
        # check if reaction is valid
        if payload.emoji.name not in ['👪', '🎲', '🌳', '🔨']:
            return await self.role_message.remove_reaction(payload.emoji, payload.member)
        
        # get user
        print(f"User: {payload.member} reacted with {payload.emoji.name}")

        # get role
        roles = {
            '👪': 1124438097401221140,
            '🎲': 1124438192821649480,
            '🌳': 1124438054069866606,
            '🔨': 1124438126841036961
        }
        role = payload.member.guild.get_role(roles[payload.emoji.name])
        await payload.member.add_roles(role)

    # on reaction removed
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload:discord.RawReactionActionEvent):
        # check if reaction is from role channel
        if payload.message_id != self.role_message.id:
            return

        # get role
        roles = {
            '👪': config.get('community_announcements_role_id'),
            '🎲': config.get('game_nights_role_id'),
            '🌳': config.get('minecraft_role_id'),
            '🔨': config.get('dev_updates_role_id'),
        }

        # get user
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        role = guild.get_role(roles[payload.emoji.name])
        await member.remove_roles(role)

    class TimezoneView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.select(
            placeholder='Select your timezone',
            custom_id='timezone-select',
            min_values=1,
            max_values=1,
            options=[
                discord.SelectOption(
                    label='EST',
                    value='est'
                ),
                discord.SelectOption(
                    label='CST',
                    value='cst'
                ),
                discord.SelectOption(
                    label='MST',
                    value='mst'
                ),
                discord.SelectOption(
                    label='PST',
                    value='pst'
                ),
                discord.SelectOption(
                    label='GMT',
                    value='gmt'
                ),
                discord.SelectOption(
                    label='CET',
                    value='cet'
                )
            ]
        )

        async def timezone(self, select: discord.ui.Select, interaction: discord.Interaction):
            roles = {
                'pst': config.get('pst_role_id'),
                'mst': config.get('mst_role_id'),
                'cst': config.get('cst_role_id'),
                'est': config.get('est_role_id'),
                'gmt': config.get('gmt_role_id'),
            }
            # reset roles
            for role_id in roles.values():
                role = interaction.guild.get_role(role_id)
                await interaction.user.remove_roles(role)

            # give new timezone role
            role = interaction.guild.get_role(roles[select.values[0]])
            await interaction.user.add_roles(role)

            await interaction.response.defer()

