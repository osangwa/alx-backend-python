#!/usr/bin/python3
"""
Memory-efficient aggregation using generators
"""
import mysql.connector
from mysql.connector import Error

def stream_user_ages():
    """Generator that yields user ages one by one"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',      # Replace with your MySQL username
            password='',      # Replace with your MySQL password
            database='ALX_prodev'
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT age FROM user_data")
        
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row[0]  # Yield the age value
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Error streaming ages: {e}")
        yield from []

def calculate_average_age():
    """Calculate average age using generator"""
    total = 0
    count = 0
    
    for age in stream_user_ages():
        total += age
        count += 1
    
    if count > 0:
        average = total / count
        print(f"Average age of users: {average:.2f}")
    else:
        print("No users found")

if __name__ == "__main__":
    calculate_average_age()