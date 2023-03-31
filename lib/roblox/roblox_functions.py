import robloxpy
import requests
import os

def get_roblox_ids(usernames):
    usernames = usernames.split()

    # First, process the usernames that are already numeric strings
    results = [id for id in usernames if id.isdigit()]
    
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
                results.append(response.get('robloxId'))
    
    
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
                results.append(user.get('id'))
        except:
            pass

    # lastly remove any duplicates
    results = list(set(results))
    
    return results
