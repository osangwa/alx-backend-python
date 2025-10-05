from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    """Create notification when a new message is created"""
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """Log old content when a message is edited"""
    if instance.pk:  # Only for existing instances (edits)
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                # Get the user who edited the message (you might need to pass this via request)
                # For now, we'll use the message sender as the editor
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender  # In real implementation, this should be the actual editor
                )
                instance.edited = True
                instance.edited_by = instance.sender  # Update edited_by field
        except Message.DoesNotExist:
            pass

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """Clean up related data when a user is deleted"""
    # Messages, notifications, and message histories will be deleted 
    # automatically due to CASCADE, but we can add additional cleanup here
    pass