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
        
    def get_data_from_id(self, id):
        query = f"""
        SELECT * FROM users WHERE User_ID = {id}
        """
        try:
            results = read_query(query)
            columns = ['User_ID','Rank_ID','Raids','Defenses','Defense_Trainings','Prism_Trainings','Spar_Gun_Wins','Spar_Gun_Kills','Spar_Sword_Wins','Spar_Sword_Kills','Solo_Aim_Trainer_Kills','Passed_Entrance_Exam','Passed_MR_Vote']
            return dict(zip(columns,results[0]))
        except:
            raise Exception('Error finding userdata')
        
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

    def get_user_commendations(self,id:int):
        try:
            query = f"""
            SELECT commendations.Commendation_ID, Emote, Name, Description, Created, Type, Quantity FROM commendations JOIN user_commendations ON commendations.Commendation_ID = user_commendations.Commendation_ID JOIN users ON users.User_ID = user_commendations.User_ID WHERE users.User_ID = {id};
            """
            results = read_query(query)
            columns = ['ID','Emote','Name','Description','Created','Type','Quantity']
            commendations = [dict(zip(columns,rank)) for rank in results]
            return commendations
        except:
            print("Error getting user's commendations")
            return []

    def get_commendation_info(self,id:int):
        try:
            commendation_query = f"""
            SELECT Name, Emote, Description, Role_ID, Created, Type FROM commendations WHERE commendations.Commendation_ID = {id};
            """
            commendation_data = read_query(commendation_query)[0]
            
            users_query = f"""
            SELECT users.User_ID FROM commendations JOIN user_commendations ON commendations.Commendation_ID = user_commendations.Commendation_ID JOIN users ON users.User_ID = user_commendations.User_ID WHERE commendations.Commendation_ID = {id};
            """
            users = read_query(users_query)
            users = [user[0] for user in users]
            
            columns = ["Name", "Emote", "Description", "Role ID", "Created", "Type"]
            commendation_data = dict(zip(columns,commendation_data))

            commendation_data['Users'] = users
            
            return commendation_data
        except:
            raise Exception('Could not find commendation')
        
    def get_all_commendations(self):
        try:
            commendation_query = f"""
            SELECT Commendation_ID, Name, Emote, Description, Role_ID, Created, Type FROM commendations;
            """
            commendations = read_query(commendation_query)
            
            columns = ["ID", "Name", "Emote", "Description", "Role ID", "Created", "Type"]
            commendations = [dict(zip(columns,commendation)) for commendation in commendations]

            return commendations
        except:
            raise Exception('Could not find any commendations')
        
    def create_commendation(self, title, description, emote, comm_type, role_id='NULL'):
        try:
            query = f"""
            INSERT INTO commendations (Name,Description,Emote,Role_ID,Created,Type)
            VALUES ('{title}', '{description}', '{emote}', {role_id}, CURRENT_TIMESTAMP, '{comm_type}');
            """
            execute_query(query)
        except:
            raise Exception('Could not create commendation')  

    def award_commendation(self, user_id, comm_id):
        try:
            # first check if user already has commendation
            # if the commendation is a medal then return already awarded
            # if the commendation is a ribbon count how many times they have been awarded it
            awarded_count = 0
            user_commendations = self.get_user_commendations(user_id)
            for commendation in user_commendations:
                if commendation['ID'] == comm_id:
                    if commendation['Type'] == 'Medal':
                        return 'Already awarded'
                    elif commendation['Type'] == 'Ribbon':
                        awarded_count = commendation['Quantity']
                        
            if awarded_count == 0:
                query = f"""
                INSERT INTO user_commendations (User_ID,Commendation_ID,Quantity)
                VALUES ({user_id}, {comm_id}, {awarded_count + 1});
                """
            else:
                query = f"""
                UPDATE user_commendations SET Quantity = {awarded_count + 1} WHERE User_ID = {user_id} AND Commendation_ID = {comm_id};
                """
            return execute_query(query)
        except:
            raise Exception('Could not award commendation') 
        
    def unaward_commendation(self, user_id, comm_id, remove_quantity):
        try:       
            # first check how many times they have been awarded it
            awarded_count = 0
            user_commendations = self.get_user_commendations(user_id)
            for commendation in user_commendations:
                if commendation['ID'] == comm_id:
                    awarded_count = commendation['Quantity']

            if awarded_count == 0:
                return {'status':'Not awarded'}
            
            if awarded_count > remove_quantity:
                query = f"""
                UPDATE user_commendations SET Quantity = {awarded_count - remove_quantity} WHERE User_ID = {user_id} AND Commendation_ID = {comm_id};
                """
            else:
                query = f"""
                DELETE FROM user_commendations WHERE User_ID = {user_id} AND Commendation_ID = {comm_id};
                """
            execute_query(query)
            remaining_commendations = awarded_count - remove_quantity
            if remaining_commendations < 0:
                unawarded_count = awarded_count
            else:
                unawarded_count = remove_quantity
            return {'status':'Success','unawarded_count':unawarded_count}
        except:
            raise Exception('Could not unaward commendation') 

    def delete_commendation(self, id):
        try:
            query = f"""
            DELETE FROM commendations WHERE Commendation_ID = {id};
            """
            execute_query(query)
        except:
            raise Exception('Could not delete commendation')
        
    def has_user_passed_mr_vote(self, user):
        try:
            query = f"""
            SELECT User_ID FROM users WHERE User_ID = {user} AND Passed_MR_Vote = 1;
            """
            result = read_query(query)
            if result:
                return True
            else:
                return False
        except:
            raise Exception('Could not find user')
        
    def has_user_passed_entrance_exam(self, user):
        try:
            query = f"""
            SELECT User_ID FROM users WHERE User_ID = {user} AND Passed_Entrance_Exam = 1;
            """
            result = read_query(query)
            if result:
                return True
            else:
                return False
        except:
            raise Exception('Could not find user')
        