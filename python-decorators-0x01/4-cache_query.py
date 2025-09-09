import time
import sqlite3 
import functools

def with_db_connection(func):
    """
    Decorator that automatically handles opening and closing database connections.
    
    This decorator opens a database connection, passes it to the function as the
    first argument, and ensures the connection is closed afterward.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open database connection
        conn = sqlite3.connect('users.db')
        try:
            # Pass connection as the first argument to the decorated function
            return func(conn, *args, **kwargs)
        finally:
            # Always close the connection, even if an exception occurs
            conn.close()
    
    return wrapper

query_cache = {}

def cache_query(func):
    """
    Decorator that caches the results of database queries to avoid redundant calls.
    
    This decorator caches query results based on the SQL query string.
    If the same query is executed again, it returns the cached result
    instead of executing the query again.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from function arguments
        query = None
        
        # Check if 'query' is passed as a keyword argument
        if 'query' in kwargs:
            query = kwargs['query']
        # Check positional arguments for the query
        elif args and len(args) > 1:  # Skip conn (first arg) and look for query
            for arg in args[1:]:  # Start from index 1 to skip connection
                if isinstance(arg, str) and ('SELECT' in arg.upper() or 'INSERT' in arg.upper() or 
                                           'UPDATE' in arg.upper() or 'DELETE' in arg.upper()):
                    query = arg
                    break
        
        # Use query as cache key if found
        cache_key = query if query else str(args) + str(kwargs)
        
        # Check if result is already cached
        if cache_key in query_cache:
            print("Cache hit! Returning cached result.")
            return query_cache[cache_key]
        
        # Execute the function and cache the result
        print("Cache miss! Executing query and caching result.")
        result = func(*args, **kwargs)
        query_cache[cache_key] = result
        
        return result
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")