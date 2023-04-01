import robloxpy
import requests
import os
from lib.sql.queries import get_rank, get_highest_possible_rank, update_rank

COOKIE = os.getenv('COOKIE')
robloxpy.User.Internal.SetCookie(COOKIE)

def get_usernames_from_ids(ids):
    try:
        url = 'https://users.roblox.com/v1/users'
        request = requests.post(url, json={
            'userIds': ids,
            'excludeBannedUsers': True
        })
        response = request.json()['data']
        return [{'username': user.get('name'), 'id': user.get('id')} for user in response]
    except:
        return [] 

def get_roblox_ids(usernames):
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
            request = requests.get(url,headers={'Authorization': f"Bearer {API}"})
            print(request)
            response = request.json()
            print(response)

            if response.get('robloxId'):
                results.append({username:response.get('cachedUsername'), id:response.get('robloxId')})
    
    
    remaining_usernames = [u for u in usernames if u not in results and not username.startswith('<@')]
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
        except:
            pass

    # lastly remove any duplicates
    return [dict(t) for t in {tuple(d.items()) for d in results}]


def check_for_promotions(users):
    for user in users:
        # get the current rank of user
        rank = get_rank(user)
        
        # if they are a diplomat or above don't change rank
        if rank >= 10:
            continue

        deserved_rank = get_highest_possible_rank(user)

        if rank != deserved_rank:
            print(f"Promote this person to {deserved_rank}")
            response = robloxpy.User.Groups.Internal.ChangeRank(16413178,id,rank)
            if response == 'Sent':
                update_rank(user, deserved_rank)
        else:
            print(f"{user} is the correct rank.")



        # if they can be promoted double check their rank on the roblox api before promoting them 
        # in the case a conscript was manually promoted to diplomat not checking might demote them to solider

def get_role_in_group(user_id, group_id):
    url = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"
    request = requests.get(url)
    response = request.json()['data']
    role = [data['role'] for data in response if data['group']['id'] == group_id]
    if len(role)>0:
        return role[0]
    else:
        return {'name':'[0] Visitor','rank':0}
