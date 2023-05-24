from lib.sql.sql import execute_query, read_query

class DB():
    def __init__(self):
        pass
    
    def award(self, event, users):
        print(users)
        users = [user for user in users if user.get('id') != None]
        if not users:
            raise Exception('No users found')
        print(users)
        # get a list of users that exist/do not exist in the database
        check_users = f"""
        SELECT User_ID FROM users WHERE User_ID IN ({', '.join(map(str,[user.get('id') for user in users]))})
        """
        try:
            results = read_query(check_users)
            print(f"reading existing records {results}")
        except:            
            raise Exception(f'Error checking users {results}')
        
        ids = [user[0] for user in results]
        new_ids = [user.get('id') for user in users if user.get('id') not in ids]
        print(f"ids:{ids}")
        print(f"new ids:{new_ids}")
        # create records for those users
        if new_ids:
            new_users = [(id,1,0,0,0,0) for id in new_ids]
            create_users = f"""
            INSERT INTO users
            VALUES {', '.join(map(str,new_users))}
            """
            print(create_users)
            result = execute_query(create_users)
            print(f"creating new user records {results}")
            if not result == 'Success':
                print("not success")
                raise Exception(f"Error trying to create new user records {result}")

        print('test')
        # add 1 to event for all users
        db_events = {'Raid':'Raids','Defense':'Defenses','Defense Training':'Defense_Trainings','Prism Training':'Prism_Trainings'}
        event = db_events[event]
        awarded = []
        print(users)
        for user in users:
            award_event = f"""
            UPDATE users
            SET {event} = {event} + 1
            WHERE User_ID IN ({user.get('id')})
            """
            print(f"trying to award {user}")
            result = execute_query(award_event)
            if result == 'Success':
                awarded.append(user)
                print(f"awarded to {user}")
            elif result == 'No rows affected':
                print("no rows affected")
            else:
                raise Exception(f'Error updating {event} column {result}')
        return awarded
    
    def update_rank(self, id, rank):
        query = f"""
        UPDATE users SET Rank_ID = {rank} WHERE User_ID = {id}
        """
        result = execute_query(query)
        if result == 'Success':
            return result
        else:
            return f'Error updating rank {result}'

    def get_user_rank(self, id):
        query = f"""
        SELECT users.Rank_ID FROM users WHERE User_ID = {id};
        """
        results = read_query(query)
        try:
            return int(results[0][0])
        except:
            raise Exception(f'Could not find {id}')

    def get_rank(self, id):
        query = f"""
        SELECT * FROM rank_requirements WHERE Rank_ID = {id}
        """
        results = read_query(query)
        try:
            columns = ['Rank_ID','Rank_Name','Role_ID','Raids','Defenses','Defense Trainings','Prism Trainings']
            return dict(zip(columns,results[0]))
        except:
            return f'Error getting rank {results}'

    def get_highest_possible_rank(self, id):
        query = f"""
        SELECT MAX(rank_requirements.Rank_ID)
        FROM rank_requirements
        CROSS JOIN users 
        WHERE users.User_ID = {id}
        AND users.Raids >= rank_requirements.Raids
        AND users.Defenses >= rank_requirements.Defenses
        AND users.Defense_Trainings >= rank_requirements.Defense_Trainings
        AND users.Prism_Trainings >= rank_requirements.Prism_Trainings;
        """
        results = read_query(query)
        try:
            return int(results[0][0])
        except:
            raise Exception(f'Error getting highest rank.')
        
    def get_data_from_id(self, id):
        query = f"""
        SELECT * FROM users WHERE User_ID = {id}
        """
        try:
            results = read_query(query)
            columns = ['User_ID','Rank_ID','Raids','Defenses','Defense_Trainings','Prism_Trainings','Spar_Gun_Wins','Spar_Gun_Kills','Spar_Sword_Wins','Spar_Sword_Kills','Solo_Aim_Trainer_Kills']
            return dict(zip(columns,results[0]))
        except:
            raise Exception('Error finding userdata')
        
    def get_rank_requirements(self, rank):
        query = f"""
        SELECT Raids, Defenses, Defense_Trainings, Prism_Trainings FROM rank_requirements WHERE Rank_ID = {rank}
        """
        try:
            results = read_query(query)
            columns = ['Raids','Defenses','Defense Trainings','Prism Trainings']
            return dict(zip(columns,results[0]))
        except:
            raise Exception(f'Error finding rank requirement {results}')
        
    def get_all_ranks(self):
        query = f"""
        SELECT * FROM rank_requirements
        """
        results = read_query(query)
        try:
            columns = ['Rank_ID','Rank_Name','Role_ID','Raids','Defenses','Defense Trainings','Prism Trainings']
            return [dict(zip(columns,rank)) for rank in results]
        except:
            return f'Error getting all ranks {results}'
        
    def set_user_stat(self, id, stat, value):
        try:
            query = f"""
            UPDATE users SET {stat} = {value} WHERE User_ID = {id};
            """
            result = execute_query(query)
            return result
        except Exception as e:
            raise e

        
    def reset_events(self,id):
        try:
            query = f"""
            UPDATE users SET Raids = 0, Defenses = 0, Defense_Trainings = 0, Prism_Trainings = 0 WHERE User_ID = {id}  
            """
            result = execute_query(query)
            if result == 'Success':
                return result
            else:
                return f'Error reseting events {result}'
        except:
            # they have no profile to reset
            pass

    def get_user_medals(self,id:int):
        try:
            query = f"""
            SELECT Emote, Name FROM medals JOIN user_medals ON medals.Medal_ID = user_medals.Medal_ID JOIN users ON users.User_ID = user_medals.User_ID WHERE users.User_ID = {id};
            """
            results = read_query(query)
            print(results)
            columns = ['Emote','Name']
            medals = [dict(zip(columns,rank)) for rank in results]
            print(medals)
            return medals
        except:
            print("Error getting user's medals")
            return []

    def get_medal_info(self,id:int):
        try:
            medal_query = f"""
            SELECT Name, Emote, Description, Role_ID, Created FROM medals WHERE medals.Medal_ID = {id};
            """
            medal_data = read_query(medal_query)[0]
            
            users_query = f"""
            SELECT users.User_ID FROM medals JOIN user_medals ON medals.Medal_ID = user_medals.Medal_ID JOIN users ON users.User_ID = user_medals.User_ID WHERE medals.Medal_ID = {id};
            """
            users = read_query(users_query)
            users = [user[0] for user in users]
            
            columns = ["Name", "Emote", "Description", "Role ID", "Created"]
            medal_data = dict(zip(columns,medal_data))

            medal_data['Users'] = users
            
            return medal_data
        except:
            raise Exception('Could not find medal')
        
    def get_all_medals(self):
        try:
            medal_query = f"""
            SELECT Medal_ID, Name, Emote, Description, Role_ID, Created FROM medals;
            """
            medals = read_query(medal_query)
            
            columns = ["ID", "Name", "Emote", "Description", "Role ID", "Created"]
            medals = [dict(zip(columns,medal)) for medal in medals]

            return medals
        except:
            raise Exception('Could not find any medals')
        
    def create_medal(self, title, description, emote, role_id='NULL'):
        try:
            query = f"""
            INSERT INTO medals (Name,Description,Emote,Role_ID,Created)
            VALUES ('{title}', '{description}', '{emote}', {role_id}, CURRENT_TIMESTAMP);
            """
            execute_query(query)
        except:
            raise Exception('Could not create medal')   
        
    def delete_medal(self, id):
        try:
            query = f"""
            DELETE FROM medals WHERE Medal_ID = {id};
            """
            execute_query(query)
        except:
            raise Exception('Could not delete medal')
        