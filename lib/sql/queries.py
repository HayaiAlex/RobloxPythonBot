from lib.sql.sql import create_db_connection, execute_query, read_query
import os

SQL_PASS = os.getenv('SQL_PASSWORD')
db = create_db_connection('localhost','root',SQL_PASS,'guf')

class DB():
    def __init__(self):
        global db
        self.db = db

    def check_connection(self):
        test_query = f"""
        SELECT * FROM users
        """
        try:
            read_query(db,test_query)
        except:
            print("Re-establishing connection")
            self.db = create_db_connection('localhost','root',SQL_PASS,'guf')
    
    def award(self, event, users):
        self.check_connection()
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
            results = read_query(self.db,check_users)
            print(f"reading existing records {results}")
        except:            
            raise Exception(f'Error checking users {results}')

        print(users)
        
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
            result = execute_query(self.db, create_users)
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
            result = execute_query(self.db, award_event)
            if result == 'Success':
                awarded.append(user)
                print(f"awarded to {user}")
            elif result == 'No rows affected':
                print("no rows affected")
            else:
                raise Exception(f'Error updating {event} column {result}')
        return awarded
    
    def update_rank(self, id, rank):
        self.check_connection()

        query = f"""
        UPDATE users SET Rank_ID = {rank} WHERE User_ID = {id}
        """
        result = execute_query(self.db, query)
        if result == 'Success':
            return result
        else:
            return f'Error updating rank {result}'

    def get_user_rank(self, id):
        self.check_connection()

        query = f"""
        SELECT users.Rank_ID, rank_requirements.Rank_Name, rank_requirements.Role_ID FROM users JOIN rank_requirements ON users.Rank_ID = rank_requirements.Rank_ID WHERE User_ID = {id};
        """
        results = read_query(self.db, query)
        try:
            columns = ['Rank_ID','Rank_Name','Role_ID']
            return dict(zip(columns,results[0]))
        except:
            return f'Error checking users {results}'

    def get_rank(self, id):
        self.check_connection()

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
        self.check_connection()

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
        self.check_connection()

        query = f"""
        SELECT * FROM users WHERE User_ID = {id}
        """
        try:
            results = read_query(self.db, query)
            columns = ['User_ID','Rank_ID','Raids','Defenses','Defense_Trainings','Prism_Trainings']
            return dict(zip(columns,results[0]))
        except:
            raise Exception('Error finding userdata')
        
    def get_rank_requirements(self, rank):
        self.check_connection()

        query = f"""
        SELECT Raids, Defenses, Defense_Trainings, Prism_Trainings FROM rank_requirements WHERE Rank_ID = {rank}
        """
        try:
            results = read_query(self.db, query)
            columns = ['Raids','Defenses','Defense Trainings','Prism Trainings']
            return dict(zip(columns,results[0]))
        except:
            raise Exception(f'Error finding rank requirement {results}')
        
    def get_all_ranks(self):
        self.check_connection()

        query = f"""
        SELECT * FROM rank_requirements
        """
        results = read_query(self.db, query)
        try:
            columns = ['Rank_ID','Rank_Name','Role_ID','Raids','Defenses','Defense Trainings','Prism Trainings']
            return [dict(zip(columns,rank)) for rank in results]
        except:
            return f'Error getting all ranks {results}'
        
    def set_event(self,id,event,num):
        self.check_connection()

        query = f"""
        UPDATE users SET {event} = {num} WHERE User_ID = {id}  
        """
        result = execute_query(self.db, query)
        if result == 'Success':
            return result
        else:
            return f'Error setting rank {result}'
        
    def reset_events(self,id):
        self.check_connection()

        try:
            query = f"""
            UPDATE users SET Raids = 0, Defenses = 0, Defense_Trainings = 0, Prism_Trainings = 0 WHERE User_ID = {id}  
            """
            result = execute_query(self.db, query)
            if result == 'Success':
                return result
            else:
                return f'Error reseting events {result}'
        except:
            # they have no profile to reset
            pass

    def get_user_medals(self,id:int):
        self.check_connection()

        try:
            query = f"""
            SELECT Emote, Name FROM medals JOIN user_medals ON medals.Medal_ID = user_medals.Medal_ID JOIN users ON users.User_ID = user_medals.User_ID WHERE users.User_ID = {id};
            """
            results = read_query(db, query)
            columns = ['Emote','Name']
            return [dict(zip(columns,rank)) for rank in results]
        except:
            return []
