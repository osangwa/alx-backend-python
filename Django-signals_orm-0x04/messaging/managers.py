from django.db import models

class UnreadMessagesManager(models.Manager):
    """Custom manager for unread messages"""
    
    def get_queryset(self):
        """Return only unread messages"""
        return super().get_queryset().filter(read=False)
    
    def unread_for_user(self, user):
        """Return unread messages for a specific user"""
        return self.get_queryset().filter(receiver=user).only('id', 'content', 'sender', 'timestamp')

class MessageManager(models.Manager):
    """Default manager for Message model with custom methods"""
    
    def get_queryset(self):
        return super().get_queryset()
    
    def unread(self):
        """Return the unread messages manager"""
        return UnreadMessagesManager()