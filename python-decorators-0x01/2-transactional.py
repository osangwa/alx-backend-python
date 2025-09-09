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

def transactional(func):
    """
    Decorator that manages database transactions by automatically 
    committing or rolling back changes.
    
    If the function raises an error, the transaction is rolled back;
    otherwise, the transaction is committed.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract connection from arguments (should be the first argument)
        if not args or not hasattr(args[0], 'execute'):
            raise ValueError("Function must receive a database connection as first argument")
        
        conn = args[0]
        
        try:
            # Begin transaction
            conn.execute("BEGIN")
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Commit if successful
            conn.commit()
            return result
            
        except Exception as e:
            # Rollback on any error
            conn.rollback()
            raise  # Re-raise the exception
    
    return wrapper

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 

#### Update user's email with automatic transaction handling 
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')