#!/usr/bin/python3
"""
Generator that streams rows from SQL database one by one
"""
import mysql.connector
from mysql.connector import Error

def stream_users():
    """Generator function that yields users one by one from database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',      # Replace with your MySQL username
            password='',      # Replace with your MySQL password
            database='ALX_prodev'
        )
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error streaming users: {e}")
        yield from []