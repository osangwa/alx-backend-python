from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

class SignalTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'password')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'password')
        self.user3 = User.objects.create_user('user3', 'user3@test.com', 'password')
    
    def test_notification_created_on_new_message(self):
        """Test that a notification is created when a new message is sent"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello, user2!"
        )
        
        # Check if notification was created
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
    
    def test_message_history_created_on_edit(self):
        """Test that message history is created when a message is edited"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        # Edit the message
        message.content = "Edited content"
        message.edited_by = self.user1
        message.save()
        
        # Check if message history was created
        self.assertEqual(MessageHistory.objects.count(), 1)
        history = MessageHistory.objects.first()
        self.assertEqual(history.message, message)
        self.assertEqual(history.old_content, "Original content")
        self.assertEqual(history.edited_by, self.user1)
        self.assertTrue(message.edited)

    def test_user_deletion_cleanup(self):
        """Test that all user-related data is deleted when a user is deleted"""
        # Create messages
        message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message from user1 to user2"
        )
        message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Message from user2 to user1"
        )
        
        # Create notifications
        notification1 = Notification.objects.create(user=self.user2, message=message1)
        notification2 = Notification.objects.create(user=self.user1, message=message2)
        
        # Edit a message to create history
        message1.content = "Edited content"
        message1.edited_by = self.user1
        message1.save()
        
        # Verify data exists before deletion
        self.assertEqual(Message.objects.filter(sender=self.user1).count(), 1)
        self.assertEqual(Message.objects.filter(receiver=self.user1).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.user1).count(), 1)
        self.assertEqual(MessageHistory.objects.filter(edited_by=self.user1).count(), 1)
        
        # Delete user1
        self.user1.delete()
        
        # Verify all user1 related data is deleted
        self.assertEqual(Message.objects.filter(sender=self.user1).count(), 0)
        self.assertEqual(Message.objects.filter(receiver=self.user1).count(), 0)
        self.assertEqual(Notification.objects.filter(user=self.user1).count(), 0)
        self.assertEqual(MessageHistory.objects.filter(edited_by=self.user1).count(), 0)
        
        # Verify user2's data is still intact
        self.assertEqual(Message.objects.filter(sender=self.user2).count(), 1)
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 1)

class MessageHistoryUITest(TestCase):
    """Test the message history user interface functionality"""
    
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'password')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'password')
        self.message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original message"
        )
    
    def test_message_history_tracking(self):
        """Test that multiple edits create multiple history entries"""
        # First edit
        self.message.content = "First edit"
        self.message.edited_by = self.user1
        self.message.save()
        
        # Second edit
        self.message.content = "Second edit"
        self.message.edited_by = self.user2
        self.message.save()
        
        # Check history entries
        self.assertEqual(MessageHistory.objects.count(), 2)
        history_entries = MessageHistory.objects.all().order_by('edited_at')
        
        self.assertEqual(history_entries[0].old_content, "Original message")
        self.assertEqual(history_entries[0].edited_by, self.user1)
        
        self.assertEqual(history_entries[1].old_content, "First edit")
        self.assertEqual(history_entries[1].edited_by, self.user2)