#!/usr/bin/env python3
"""
1-execute.py
Reusable query context manager
"""

import sqlite3

class ExecuteQuery:
    """Reusable context manager for executing queries"""
    
    def __init__(self, db_name="users.db", query="", params=()):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """Setup connection and execute query"""
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        return self.results
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup resources"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

def main():
    """Demonstrate the ExecuteQuery context manager"""
    # Ensure the database exists with sample data
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
        users = [
            ("Alice Johnson", 28, "alice@example.com"),
            ("Bob Smith", 32, "bob@example.com"),
            ("Carol Davis", 45, "carol@example.com"),
            ("David Wilson", 22, "david@example.com"),
            ("Eva Brown", 38, "eva@example.com"),
            ("Frank Miller", 29, "frank@example.com"),
            ("Grace Lee", 41, "grace@example.com")
        ]
        cursor.executemany(
            "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
            users
        )
        conn.commit()
    
    # Use the reusable query context manager
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)
    
    with ExecuteQuery("users.db", query, params) as results:
        print("Users older than 25:")
        print("-" * 50)
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}, Email: {row[3]}")
        print("-" * 50)
        print(f"Total users found: {len(results)}")

if __name__ == "__main__":
    main()