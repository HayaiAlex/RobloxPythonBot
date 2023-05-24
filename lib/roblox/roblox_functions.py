import robloxpy, requests, os, discord
from lib.sql.queries import DB
from dotenv import load_dotenv
load_dotenv(override=True)
GROUP_ID = os.getenv('GROUP_ID')
db = DB()

def get_usernames_from_ids(ids):
    try:
        url = 'https://users.roblox.com/v1/users'
        request = requests.post(url, json={
            'userIds': ids,
            'excludeBannedUsers': True
        })
        response = request.json()['data']
        usernames = [{'username': user.get('name'), 'id': user.get('id')} for user in response]
        usernames += [{'username': id, 'id': None} for id in ids if id not in [user.get('id') for user in response]]
        return usernames
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
            request = requests.get(url,headers={'Authorization': f'Bearer {API}'})
            response = request.json()
            if response.get('robloxId'):
                results.append({'username':response.get('cachedUsername'), 'id':response.get('robloxId')})
            else:
                results.append({'username':username, 'id':None})
    
    
    remaining_usernames = [u for u in usernames if u not in results and not u.startswith('<@')]
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
                if user not in [user['username'] for user in results]:
                    results.append({'username':user, 'id':None})
        except:
            pass

    # lastly remove duplicates
    for user in results:
        if results.count(user) > 1:
            results.remove(user)

    return results

def check_for_promotions(users):
    promoted = []
    skipped_ranks = []
    for user in users:
        # get the current rank of user on the database
        try:
            rank = db.get_user_rank(user)
        except Exception as err:
            print(err)
            rank = 0
        
        try:
            deserved_rank = db.get_highest_possible_rank(user)
        except Exception as err:
            print(err)
            deserved_rank = 0
        print(f"rank: {rank}, deserved rank: {deserved_rank}")

        # always check if they are the correct rank in the group
        role = get_role_in_group(user,GROUP_ID)
        print(f"Actual role in group is: {role['rank']}")
        if role['rank'] >= 10:
            if rank != role['rank']:
                db.update_rank(user, role['rank'])
            print(f"{user} is the correct rank.")
            continue
        
        if role['rank'] != deserved_rank and role['rank'] > 0:
            # if they are conscript and being promoted multiple ranks they probably left so prompt reset stats
            if role['rank'] == 1 and deserved_rank > 2:
                skipped_ranks.append(user)

            print(f"Promote user {user} to {deserved_rank}")
            response = robloxpy.User.Groups.Internal.ChangeRank(GROUP_ID,user,rank)
            if response == 'Sent':
                db.update_rank(user, deserved_rank)
                promoted.append(user)
        else:
            print(f"{user} is the correct rank.")
    return (promoted, skipped_ranks)

def get_role_in_group(user_id, group_id):
    url = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"
    try:
        request = requests.get(url)
        response = request.json()['data']
        role = [datum['role'] for datum in response if datum['group']['id'] == int(group_id)]
        return role[0]
    except:
        return {'name':'[0] Visitor','rank':0}
    

