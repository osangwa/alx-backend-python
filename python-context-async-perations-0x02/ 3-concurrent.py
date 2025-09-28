#!/usr/bin/env python3
"""
2-concurrent.py
Concurrent asynchronous database queries using aiosqlite
"""

import asyncio
import aiosqlite

async def create_sample_database():
    """Create a sample database with users table"""
    async with aiosqlite.connect("users_async.db") as db:
        await db.execute("DROP TABLE IF EXISTS users")
        await db.execute("""
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
            ("Grace Lee", 41, "grace@example.com"),
            ("Henry Taylor", 35, "henry@example.com"),
            ("Ivy Chen", 27, "ivy@example.com"),
            ("Jack Harris", 48, "jack@example.com")
        ]
        
        await db.executemany(
            "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
            users
        )
        await db.commit()

async def async_fetch_users():
    """Fetch all users from the database"""
    async with aiosqlite.connect("users_async.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            print("All users fetched:")
            print("-" * 40)
            for row in results:
                print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")
            print(f"Total users: {len(results)}")
            print("-" * 40)
            return results

async def async_fetch_older_users():
    """Fetch users older than 40"""
    async with aiosqlite.connect("users_async.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            results = await cursor.fetchall()
            print("Users older than 40:")
            print("-" * 40)
            for row in results:
                print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")
            print(f"Users older than 40: {len(results)}")
            print("-" * 40)
            return results

async def fetch_concurrently():
    """Execute both queries concurrently using asyncio.gather"""
    print("Starting concurrent database queries...")
    print("=" * 50)
    
    # Execute both queries concurrently
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users(),
        return_exceptions=True
    )
    
    print("=" * 50)
    print("Concurrent queries completed!")
    return results

async def main():
    """Main async function"""
    # Create sample database first
    await create_sample_database()
    
    # Run concurrent queries
    await fetch_concurrently()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())