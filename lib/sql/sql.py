import dotenv
import mysql.connector, os
from mysql.connector import Error
import pandas as pd

def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(err)
        raise Exception(err)

    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(err)
        raise Exception(err)

def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name,
            charset='utf8mb4'
        )
        connection.set_charset_collation('utf8mb4')
    except Error as err:
        print(err)
        raise Exception(err)

    return connection

dotenv.load_dotenv(override=True)
import os
SQL_PASS = os.getenv('SQL_PASSWORD')

def execute_query(query):
    connection = create_db_connection('localhost','root',SQL_PASS,'guf')
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
        if cursor.rowcount > 0:
            return 'Success'
        else:
            return 'No rows affected'
    except Error as err:
        print(err)
        cursor.close()
        connection.close()
        raise Exception(err)
    

def read_query(query):
    connection = create_db_connection('localhost','root',SQL_PASS,'guf')
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Error as err:
        print(err)
        cursor.close()
        connection.close()
        raise Exception(err)
    
    

# file = open('lib/sql/database.sql', 'r')
# init_db = file.read()
# file.close()
# init_queries = init_db.split(';')

# PASSWORD = os.getenv('SQL_PASSWORD')

# server_connection = create_server_connection('localhost','root',PASSWORD)
# create_database(server_connection,'CREATE DATABASE guf')
# db = create_db_connection('localhost','root',PASSWORD,'guf')
# for query in init_queries:
#     print(execute_query(db, query))