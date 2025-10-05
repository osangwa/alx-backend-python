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
            if old_message.content != instance.content and not old_message.edited:
                # Only create history if content changed and it wasn't already marked as edited
                # Use the edited_by field if it's set, otherwise default to sender
                editor = instance.edited_by if instance.edited_by else instance.sender
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=editor
                )
                instance.edited = True
                # Ensure edited_by is set
                if not instance.edited_by:
                    instance.edited_by = instance.sender
        except Message.DoesNotExist:
            pass

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """Clean up related data when a user is deleted"""
    # Use ID-based queries to avoid issues with deleted user instances
    user_id = instance.id
    
    # Delete all messages sent by the user (CASCADE will handle this)
    # Delete all notifications for the user
    Notification.objects.filter(user_id=user_id).delete()
    
    # Delete all message history entries edited by the user
    MessageHistory.objects.filter(edited_by_id=user_id).delete()
    
    # Delete notifications for messages where the user was the receiver
    Notification.objects.filter(message__receiver_id=user_id).delete()