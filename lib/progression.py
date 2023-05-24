import robloxpy, os
from lib.roblox.roblox_functions import get_role_in_group
from lib.sql.queries import DB
db = DB()

from dotenv import load_dotenv
load_dotenv(override=True)
GROUP_ID = os.getenv('GROUP_ID')

def get_top_rank(profile):
    def check_rank_6(profile):
        if profile['Passed_MR_Vote'] == True:
            return True
        
        return False

    def check_rank_5(profile):
        if profile['Raids'] + profile['Defenses'] >= 8 and profile['Raids'] > 3 and \
            profile['Prism_Trainings'] + profile['Defense_Trainings'] > 18 and \
            profile['Spar_Gun_Wins'] + profile['Spar_Sword_Wins'] >= 25:
            return True
        
        return False

    def check_rank_4(profile):
        if profile['Raids'] + profile['Defenses'] >= 2 and \
            profile['Prism_Trainings'] + profile['Defense_Trainings'] >= 13 and \
            profile['Solo_Aim_Trainer_Kills'] >= 60:
            return True
        
        return False

    def check_rank_3(profile):
        if profile['Defense_Trainings'] >= 4 and \
            profile['Prism_Trainings'] >= 4:
            return True
        
        return False

    def check_rank_2(profile):
        if profile['Defense_Trainings'] >= 1 and \
            profile['Prism_Trainings'] >= 1 and \
            profile['Passed_Entrance_Exam'] == 1:
            return True
        
        return False


    rank_requirements = {'2':check_rank_2, '3':check_rank_3, '4':check_rank_4, '5':check_rank_5, '6':check_rank_6}
    current_rank = 1
    
    for rank, passes_rank in rank_requirements.items():
        if not passes_rank(profile):
            return current_rank
        else:
            current_rank = int(rank)
    return current_rank

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
            user_profile = db.get_data_from_id(user)
            deserved_rank = get_top_rank(user_profile)
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
