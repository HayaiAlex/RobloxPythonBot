from lib.sql.sql import create_db_connection, execute_query, read_query

class DB():
    def __init__(self):
        self.db = create_db_connection('localhost','root','','guf_test')

    def award(self, event, users):
        users = [user for user in users if user.get('id') != None]
        if not users:
            raise Exception('No users found')
        
        # get a list of users that exist/do not exist in the database
        check_users = f"""
        SELECT User_ID FROM users WHERE User_ID IN ({', '.join(map(str,[user.get('id') for user in users]))})
        """
        results = read_query(self.db,check_users)
        try:
            if results.find('Error'):
                raise Exception(f'Error checking users {results}')
        except:
            pass
        
        ids = [user[0] for user in results]
        new_ids = [user.get('id') for user in users if user.get('id') not in ids]
        
        # create records for those users
        if new_ids:
            new_users = [(id,1,0,0,0,0) for id in new_ids]
            create_users = f"""
            INSERT INTO users
            VALUES {', '.join(map(str,new_users))}
            """
            result = execute_query(self.db, create_users)
            if not result == 'Success':
                raise Exception(f"Error trying to create new user records {result}")

        # add 1 to event for all users
        db_events = {'Raid':'Raids','Defense':'Defenses','Defense Training':'Defense_Trainings','Prism Training':'Prism_Trainings'}
        event = db_events[event]
        awarded = []
        for user in users:
            award_event = f"""
            UPDATE users
            SET {event} = {event} + 1
            WHERE User_ID IN ({user.get('id')})
            """
            result = execute_query(self.db, award_event)
            if result == 'Success':
                awarded.append(user)
            elif result == 'No rows affected':
                print("no rows affected")
            else:
                raise Exception(f'Error updating {event} column {result}')
        return awarded
        
    def update_rank(self, id, rank):
        query = f"""
        UPDATE users SET Rank_ID = {rank} WHERE User_ID = {id}
        """
        result = execute_query(self. db, query)
        if result == 'Success':
            return result
        else:
            return f'Error updating rank {result}'

    def get_user_rank(self, id):
        query = f"""
        SELECT Rank_ID FROM users WHERE User_ID = {id}
        """
        results = read_query(self.db, query)
        try:
            return int(results[0][0])
        except:
            return f'Error checking users {results}'
        
    def get_rank(self, id):
        print(id)
        query = f"""
        SELECT * FROM rank_requirements WHERE Rank_ID = {id}
        """
        results = read_query(self.db, query)
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
        results = read_query(self.db, query)
        try:
            return int(results[0][0])
        except:
            return f'Error checking users {results}'
        
    def get_data_from_id(self, id):
        query = f"""
        SELECT * FROM users WHERE User_ID = {id}
        """
        try:
            results = read_query(self.db, query)
            columns = ['User_ID','Rank_ID','Raids','Defenses','Defense Trainings','Prism Trainings']
            return dict(zip(columns,results[0]))
        except:
            raise Exception('Error finding userdata')
        
    def get_rank_requirements(self, rank):
        query = f"""
        SELECT Raids, Defenses, Defense_Trainings, Prism_Trainings FROM rank_requirements WHERE Rank_ID = {rank}
        """
        try:
            results = read_query(self.db, query)
            columns = ['Raids','Defenses','Defense Trainings','Prism Trainings']
            return dict(zip(columns,results[0]))
        except:
            return f'Error finding rank requirement {results}'
        