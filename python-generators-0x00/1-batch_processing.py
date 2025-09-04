#!/usr/bin/python3
"""
Batch processing of large data using generators
"""
import mysql.connector
from mysql.connector import Error

def stream_users_in_batches(batch_size):
    """Generator that fetches users in batches"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',      # Replace with your MySQL username
            password='',      # Replace with your MySQL password
            database='ALX_prodev'
        )
        
        offset = 0
        while True:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM user_data LIMIT {batch_size} OFFSET {offset}")
            
            batch = cursor.fetchall()
            if not batch:
                break
                
            yield batch
            offset += batch_size
            cursor.close()
        
        connection.close()
        
    except Error as e:
        print(f"Error streaming batches: {e}")
        yield from []

def batch_processing(batch_size):
    """Process batches to filter users over age 25 and yield them"""
    for batch in stream_users_in_batches(batch_size):  # First loop
        for user in batch:  # Second loop
            if user['age'] > 25:
                yield user  # Using yield to return filtered users