import sqlite3
import functools
from datetime import datetime

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
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if query:
            print(f"[{timestamp}] Executing SQL Query: {query}")
        else:
            print(f"[{timestamp}] Executing function: {func.__name__}")
        
        # Execute the original function
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")