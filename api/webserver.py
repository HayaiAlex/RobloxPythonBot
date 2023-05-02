from aiohttp import web
from aiohttp_swagger import *
from discord.ext import commands, tasks
import discord
import os
import json
import aiohttp
from lib.discord_functions import DiscordManager
from lib.roblox.roblox_functions import check_for_promotions, get_roblox_ids
from lib.sql.queries import DB

db = DB()
discordManager = None

app = web.Application()
routes = web.RouteTableDef()


def setup(bot):
    global discordManager
    discordManager = DiscordManager(bot)
    bot.add_cog(Webserver(bot))


class Webserver(commands.Cog):
    def __init__(self, bot):
        print("Setting up web server")
        self.bot = bot
        self.web_server.start()
        print("Web server live")

        @routes.get('/')
        async def welcome(request):
            print("Hit")
            return web.Response(text="Hello, world")
        
        @routes.get('/user', allow_head=False)
        async def get_user(request):
            try:
                print(f"get user {request.query['id']}")
            
                profile = db.get_data_from_id(request.query['id'])
                medals = db.get_user_medals(request.query['id'])
                profile['medals'] = medals
                data = json.dumps(profile)

                return web.Response(status=200,content_type="application/json", body=data)
            except:
                return web.Response(status=404)
            
        @routes.get('/medal', allow_head=False)
        async def get_medal(request):
            try:
                print(f"getting medal {request.query['id']}")

                medal_data = db.get_medal_info(request.query['id'])
                data = json.dumps(medal_data, default=str)

                return web.Response(status=200,content_type="application/json", body=data)
            except:
                return web.Response(status=404)
            
        @routes.get('/allmedals', allow_head=False)
        async def get_all_medals(request):
            try:
                print(f"getting all medals")

                medals = db.get_all_medals()
                data = json.dumps(medals, default=str)

                return web.Response(status=200,content_type="application/json", body=data)
            except:
                return web.Response(status=404)

        @routes.post('/award')
        async def award(request):
            if request.headers.get('authorization') == 'some_code':
                data = await request.json()
                users = data['user']
                event = data['event']
                print("award hit")

                users = [user for user in get_roblox_ids(users)]
            
                try:
                    awarded = db.award(event,users)
                    could_not_find = [user.get('username') for user in users if user.get('username').lower() not in [user.get('username').lower() for user in awarded]]
                except:
                    awarded = []
                    could_not_find = []

                data = {
                    "awarded":awarded,
                    "could_not_find":could_not_find
                }

                if len(awarded) > 0:

                
                    promoted, skipped_ranks = check_for_promotions([user.get('id') for user in awarded])

                    data['promoted'] = promoted
                    data['skipped_rank'] = skipped_ranks

                    for user in skipped_ranks:
                        await DiscordManager.send_restore_stats_msg(user, event)

                    for user in promoted:
                        discordManager.update_roles(user)
                        
                    data = json.dumps(data) 
                    return web.Response(status=200,content_type="application/json", body=data)
                else:
                    data = json.dumps(data)
                    return web.Response(status=200,content_type="application/json", body=data)

            return web.Response(status=401)


        self.webserver_port = os.environ.get('PORT', 80)
        app.add_routes(routes)

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=self.webserver_port)
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()
        setup_swagger(app, swagger_url="/api/v1/doc", ui_version=3, swagger_from_file="api/swagger.yaml")
