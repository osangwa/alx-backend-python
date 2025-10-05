from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

class SignalTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'password')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'password')
    
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