#!/usr/bin/python3
"""
Lazy loading paginated data using generators
"""
import mysql.connector
from mysql.connector import Error

def paginate_users(page_size, offset):
    """Fetch a page of users from database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',      # Replace with your MySQL username
            password='',      # Replace with your MySQL password
            database='ALX_prodev'
        )
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
        rows = cursor.fetchall()
        
        cursor.close()
        connection.close()
        return rows
        
    except Error as e:
        print(f"Error paginating users: {e}")
        return []

def lazy_pagination(page_size):
    """Generator for lazy pagination"""
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size