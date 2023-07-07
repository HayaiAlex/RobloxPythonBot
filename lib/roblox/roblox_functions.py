import robloxpy, requests, os, discord
from lib.sql.queries import DB
from dotenv import load_dotenv
load_dotenv(override=True)
GROUP_ID = os.getenv('GROUP_ID')
PRISM_API = os.getenv('PRISM_API')
COOKIE = os.getenv('COOKIE')
db = DB()

async def get_avatar_thumbnail(id, type='bust'):
    # get the user's avatar
    if type == 'full':
        url = f"https://thumbnails.roblox.com/v1/users/avatar?userIds={id}&size=150x150&format=Png&isCircular=false"
    else:
        url = f"https://thumbnails.roblox.com/v1/users/avatar-{type}?userIds={id}&size=150x150&format=Png&isCircular=false"
    
    request = requests.get(url)
    response = request.json()
    avatar_url = response['data'][0]['imageUrl']

    return avatar_url

def has_uniform(user):
    # check if the user has the uniform
    pants = 12193039426
    shirt = 12192983374
    url = f"https://inventory.roblox.com/v1/users/{user.get('id')}/items/0/{pants}/is-owned"
    request = requests.get(url)
    owns_pants = request.json()
    if owns_pants:
        url = f"https://inventory.roblox.com/v1/users/{user.get('id')}/items/0/{shirt}/is-owned"
        request = requests.get(url)
        owns_shirt = request.json()
        if owns_shirt:
            return True
    return False

def get_usernames_from_ids(ids):
    try:
        url = 'https://users.roblox.com/v1/users'
        request = requests.post(url, json={
            'userIds': ids,
            'excludeBannedUsers': True
        })
        response = request.json()['data']
        usernames = [{'username': user.get('name'), 'id': user.get('id')} for user in response]
        usernames += [{'username': id, 'id': None} for id in ids if int(id) not in [user.get('id') for user in response]]
        return usernames
    except:
        return [] 

def get_roblox_ids(usernames):
    # remove commas
    usernames = usernames.replace(",", " ")

    # remove any extra spaces
    while "  " in usernames:
        usernames = usernames.replace("  ", " ")
    usernames = usernames.split(" ")
    
    # First, process the usernames that are already numeric strings
    ids = [id for id in usernames if id.isdigit()]
    results = get_usernames_from_ids(ids)
    # Next, process the usernames that are Discord mentions
    for username in usernames:
        if username.startswith('<@') and username.endswith('>'):
            # user rover to get their roblox id
            API = os.getenv('ROVERIFY_API')
            GUILD_ID = os.getenv('DISCORD_GUILD')
            url = f"http://registry.rover.link/api/guilds/{GUILD_ID}/discord-to-roblox/{username[2:-1]}"
            request = requests.get(url,headers={'Authorization': f'Bearer {API}'})
            response = request.json()
            if response.get('robloxId'):
                results.append({'username':response.get('cachedUsername'), 'id':response.get('robloxId')})
            else:
                results.append({'username':username, 'id':None})
    
    remaining_usernames = [u for u in usernames if u not in [str(user.get('id')) for user in results] and not u.startswith('<@')]
    if remaining_usernames:
        try:
            url = 'https://users.roblox.com/v1/usernames/users'
            request = requests.post(url, json={
                'usernames': remaining_usernames,
                'excludeBannedUsers': True
            })
            response = request.json()['data']
            # May not include all ids if a user with this name on roblox does not exist
            for user in response:
                results.append({'username':user.get('name'), 'id':user.get('id')})

            for user in remaining_usernames:
                if user.lower() not in [user['username'].lower() for user in results]:
                    results.append({'username':user, 'id':None})
        except:
            pass
    
    # lastly remove duplicates
    for user in results:
        if results.count(user) > 1:
            results.remove(user)

    return results

def get_recent_badges(user_id, limit=100):
    url = f"https://badges.roblox.com/v1/users/{user_id}/badges?limit={limit}&sortOrder=Desc"
    try:
        request = requests.get(url)
        response = request.json()['data']
        return response
    except:
        return []

def get_role_in_group(user_id, group_id=GROUP_ID):
    url = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"
    try:
        request = requests.get(url)
        response = request.json()['data']
        role = [datum['role'] for datum in response if datum['group']['id'] == int(group_id)]
        return role[0]
    except:
        return {'name':'[0] Visitor','rank':0}
    
def get_group_roles(user_id):
    url = f"https://groups.roblox.com/v1/users/{user_id}/groups/roles"
    try:
        request = requests.get(url)
        response = request.json()['data']
        return response
    except:
        return []
    
def get_ordered_datastore_stat(user, unverse_id, datastore_name):
    url = f"https://apis.roblox.com/ordered-data-stores/v1/universes/{unverse_id}/orderedDataStores/{datastore_name}/scopes/global/entries/{user}"
    try:
      request = requests.get(
        url,
        headers={'x-api-key': PRISM_API})
      response = request.json()
      return response.get('value')
    except:
      return None
    
def accept_join_request(user_id, x_csrf_token=None, attempts=0):
    url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/join-requests/users/{user_id}"
    try:
        request = requests.post(
            url,
            headers={'cookie': f'.ROBLOSECURITY={COOKIE}', 'x-csrf-token': x_csrf_token}
        )
        if request.status_code == 200:
            return True
        elif request.status_code == 403 and attempts < 3:
            return accept_join_request(user_id, request.headers['x-csrf-token'], attempts+1)
        else:
            return False
    except Exception as e:
        print(e)
        return False
    
def decline_join_request(user_id, x_csrf_token=None, attempts=0):
    url = f"https://groups.roblox.com/v1/groups/{GROUP_ID}/join-requests/users/{user_id}"
    try:
        request = requests.delete(
            url,
            headers={'cookie': f'.ROBLOSECURITY={COOKIE}', 'x-csrf-token': x_csrf_token}
        )
        if request.status_code == 200:
            return True
        elif request.status_code == 403 and attempts < 3:
            return decline_join_request(user_id, request.headers['x-csrf-token'], attempts+1)
        else:
            return False
    except Exception as e:
        print(e)
        return False