# chats/middleware.py
from datetime import datetime
import os

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Process request
        user = "Anonymous"
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username
            
        # Log the request
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        
        # Write to requests.log file
        log_file_path = 'requests.log'
        with open(log_file_path, 'a') as log_file:
            log_file.write(log_entry)
        
        response = self.get_response(request)
        return response