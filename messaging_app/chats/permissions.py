# chats/permissions.py
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status

class IsAuthenticated(permissions.BasePermission):
    """
    Custom permission to only allow authenticated users to access the API.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants in a conversation to send, view, update and delete messages.
    """
    
    def has_permission(self, request, view):
        # Allow GET, POST, PUT, PATCH, DELETE only for authenticated users
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For conversation list/create, check if user is authenticated
        if view.action in ['list', 'create']:
            return True
        
        # For other actions, check object permission
        return True
    
    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if the user is a participant in the conversation
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        elif hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        
        return False

class IsMessageOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission to only allow message owners or conversation participants to access messages.
    """
    
    def has_permission(self, request, view):
        # Allow GET, POST, PUT, PATCH, DELETE only for authenticated users
        if not request.user or not request.user.is_authenticated:
            return False
        return True
    
    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Allow safe methods (GET, HEAD, OPTIONS) for participants
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'conversation'):
                return request.user in obj.conversation.participants.all()
        
        # Allow PUT, PATCH, DELETE only for message owner
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return obj.sender == request.user
        
        # Allow POST for participants (sending messages)
        if request.method == 'POST':
            if hasattr(obj, 'conversation'):
                return request.user in obj.conversation.participants.all()
        
        # Allow if user is the sender of the message
        if obj.sender == request.user:
            return True
        
        return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_permission(self, request, view):
        # Allow only authenticated users
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions (PUT, PATCH, DELETE) are only allowed to the owner.
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'sender'):
            return obj.sender == request.user
        elif hasattr(obj, 'host'):
            return obj.host == request.user
        
        return False