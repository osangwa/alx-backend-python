import sqlite3
import functools
import datetime

def log_queries(func):
    """
    Decorator that logs SQL queries executed by any function.
    
    This decorator intercepts function calls and logs the SQL query
    along with timestamp information before executing the function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        query = None
        
        # Check if 'query' is passed as a keyword argument
        if 'query' in kwargs:
            query = kwargs['query']
        # Check if 'query' is the first positional argument (common pattern)
        elif args and len(args) > 0:
            # Look for the query in the first few arguments
            for arg in args:
                if isinstance(arg, str) and ('SELECT' in arg.upper() or 'INSERT' in arg.upper() or 
                                           'UPDATE' in arg.upper() or 'DELETE' in arg.upper()):
                    query = arg
                    break
        
        # Log the query with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if query:
            print(f"[{timestamp}] Executing SQL Query: {query}")
        else:
            print(f"[{timestamp}] Executing function: {func.__name__}")
        
        # Execute the original function
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    """Fetch all users from the database with query logging."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Example usage and testing
if __name__ == "__main__":
    # Create a sample database and table for testing
    def setup_database():
        """Set up a sample users database for testing."""
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER
            )
        ''')
        
        # Insert sample data if table is empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            sample_users = [
                ('Alice Johnson', 'alice@example.com', 28),
                ('Bob Smith', 'bob@example.com', 35),
                ('Charlie Brown', 'charlie@example.com', 22),
                ('Diana Prince', 'diana@example.com', 30)
            ]
            cursor.executemany(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                sample_users
            )
        
        conn.commit()
        conn.close()
        print("Database setup completed.")
    
    # Set up the database
    setup_database()
    
    # Fetch users while logging the query
    print("\n--- Testing log_queries decorator ---")
    users = fetch_all_users(query="SELECT * FROM users")
    print(f"Retrieved {len(users)} users:")
    for user in users:
        print(f"  ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Age: {user[3]}")
    
    # Test with different queries
    print("\n--- Testing with different queries ---")
    young_users = fetch_all_users(query="SELECT * FROM users WHERE age < 30")
    print(f"Found {len(young_users)} users under 30")
    
    specific_user = fetch_all_users(query="SELECT * FROM users WHERE name LIKE '%Alice%'")
    print(f"Found {len(specific_user)} users with 'Alice' in name")