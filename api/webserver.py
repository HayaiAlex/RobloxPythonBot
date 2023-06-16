from aiohttp import web
from aiohttp_swagger import *
from discord.ext import commands, tasks
import discord, os, json, aiohttp
from lib.discord_functions import DiscordManager
from lib.progression import check_for_promotions
from lib.roblox.roblox_functions import get_roblox_ids
from lib.sql.queries import DB

Auth = os.getenv('AUTH')

db = DB()
discordManager = None

app = web.Application()
routes = web.RouteTableDef()


def setup(bot):
    global discordManager
    discordManager = DiscordManager(bot)
    bot.add_cog(Webserver(bot))
    print("Setup complete")

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
                commendations = db.get_user_commendations(request.query['id'])
                profile['Commendations'] = commendations
                data = json.dumps(profile, default=str)

                return web.Response(status=200,content_type="application/json", body=data)
            except:
                return web.Response(status=404)
            
        @routes.post('/update-user')
        async def update_user(request):
            data = await request.json()
            print(data)
            if request.headers.get('authorization') != Auth:
                return web.Response(status=401)
            try:
                id = data.pop('id')
                print(f"update user {id}")
                msg = ""
                for stat,value in data.items():
                    print(f"updating {stat} to {value}")
                    try:
                        db.set_user_stat(id, stat, value)
                        msg += f"Updated {stat} to {value}\n"
                    except Exception as e:
                        msg += f"Error updating {stat} to {value}\n"
                        msg += f"Error: {e}\n"
                return web.Response(status=200, text=msg)
            except:
                return web.Response(status=404)
            
        
        @routes.get('/commendation', allow_head=False)
        async def get_commendation(request):
            try:
                print(f"getting commendation {request.query['id']}")

                commendation_data = db.get_commendation_info(request.query['id'])
                data = json.dumps(commendation_data, default=str)

                return web.Response(status=200,content_type="application/json", body=data)
            except:
                return web.Response(status=404)
            
        @routes.get('/all-commendations', allow_head=False)
        async def get_all_commendations(request):
            try:
                print(f"getting all commendations")

                commendations = db.get_all_commendations()
                data = json.dumps(commendations, default=str)

                return web.Response(status=200,content_type="application/json", body=data)
            except:
                return web.Response(status=404)
            
        @routes.post('/award-commendation')
        async def award_commendation(request):
            if request.headers.get('authorization') != Auth:
                return web.Response(status=401)
            
            data = await request.json()
            users = data['users']
            commendation = data['commendation']

            users = get_roblox_ids(users)
            try:
                for user in users:
                    db.award_commendation(user.get('id'),commendation)
                return web.Response(status=200)
            except:
                return web.Response(status=404)
            
        @routes.delete('/remove-commendation')
        async def remove_commendation(request):
            if request.headers.get('authorization') != Auth:
                return web.Response(status=401)
            
            data = await request.json()
            users = data['users']
            commendation = data['commendation']
            try:
                quantity = data['quantity']
            except:
                quantity = 1

            users = get_roblox_ids(users)
            success = []
            failed = []
            for user in users:
                try:
                    db.unaward_commendation(user.get('id'),commendation,quantity)
                    success.append(user.get('username'))
                except:
                    failed.append(user.get('username'))

            if len(success) == 0:
                return web.Response(status=404)
            
            data = {
                "success":success,
                "failed":failed
            }

            data = json.dumps(data)
            return web.Response(status=200,content_type="application/json", body=data)
        
        
        

        @routes.post('/award')
        async def award(request):
            if request.headers.get('authorization') != Auth:
                return web.Response(status=401)
            
            data = await request.json()
            users = data['user']
            event = data['event']
            print("award hit")

            users = get_roblox_ids(users)
            print(users)
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
