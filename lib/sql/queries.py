from lib.sql.sql import create_db_connection, execute_query, read_query

db = create_db_connection('localhost','root','','guf_test')

def award(event, users):
    print(users)
    if not users:
        return 'No users found'
    
    # get a list of users that exist/do not exist in the database
    check_users = f"""
    SELECT User_ID FROM users WHERE User_ID IN ({', '.join(map(str,users))})
    """
    print(check_users)
    results = read_query(db,check_users)
    try:
        if results.find('Error'):
            return f'Error checking users {results}'
    except:
        pass
    
    print(results)
    ids = [user[0] for user in results]
    new_ids = [id for id in users if id not in ids]
    print(f"ids: {ids}")
    print(f"new ids: {new_ids}")
    
    # create records for those users
    if new_ids:
        new_users = [(id,1,0,0,0,0) for id in new_ids]
        create_users = f"""
        INSERT INTO users
        VALUES {', '.join(map(str,new_users))}
        """
        result = execute_query(db, create_users)
        if not result == 'Success':
            return f"Error trying to create new user records {result}"

    # add 1 to event for all users
    db_events = {'Raid':'Raids','Defense':'Defenses','Defense Training':'Defense_Trainings','Prism Training':'Prism_Trainings'}
    event = db_events[event]
    award_event = f"""
    UPDATE users
    SET {event} = {event} + 1
    WHERE User_ID IN ({', '.join(map(str,users))})
    """
    result = execute_query(db, award_event)
    if result == 'Success':
        return result
    else:
        return f'Error updating {event} column {result}'
    
def update_rank(id, rank):
    query = f"""
    UPDATE users SET Rank_ID = {rank} WHERE User_ID = {id}
    """
    result = execute_query(db, query)
    if result == 'Success':
        return result
    else:
        return f'Error updating rank {result}'

def get_rank(id):
    query = f"""
    SELECT Rank_ID FROM users WHERE User_ID = {id}
    """
    results = read_query(db, query)
    try:
        return results[0][0]
    except:
        return f'Error checking users {results}'

def get_highest_possible_rank(id):
    query = f"""
    SELECT MAX(rank_requirements.Rank_ID)
    FROM rank_requirements
    CROSS JOIN users 
    WHERE users.User_ID = {id}
    AND users.Raids >= rank_requirements.Raids
    AND users.Defenses >= rank_requirements.Defenses
    AND users.Defense_Training >= rank_requirements.Defense_Training
    AND users.Prism_Trainings >= rank_requirements.Prism_Trainings;
    """
    results = read_query(db, query)
    try:
        return results[0][0]
    except:
        return f'Error checking users {results}'