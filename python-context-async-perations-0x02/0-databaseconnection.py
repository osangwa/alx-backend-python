#!/usr/bin/env python3
"""
0-databaseconnection.py
Custom class-based context manager for database connections
"""

import sqlite3

class DatabaseConnection:
    """Custom context manager for SQLite database connections"""
    
    def __init__(self, db_name="users.db"):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        """Setup the database connection when entering the context"""
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        return self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup the database connection when exiting the context"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

def main():
    """Demonstrate the DatabaseConnection context manager"""
    # Create a sample database with users table
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT NOT NULL
            )
        """)
        # Insert sample data
        users = [
            ("Alice Johnson", 28, "alice@example.com"),
            ("Bob Smith", 32, "bob@example.com"),
            ("Carol Davis", 45, "carol@example.com"),
            ("David Wilson", 22, "david@example.com"),
            ("Eva Brown", 38, "eva@example.com")
        ]
        cursor.executemany(
            "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
            users
        )
        conn.commit()
    
    # Use the custom context manager
    with DatabaseConnection("users.db") as cursor:
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        print("All users in the database:")
        print("-" * 50)
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}, Email: {row[3]}")
        print("-" * 50)

if __name__ == "__main__":
    main()