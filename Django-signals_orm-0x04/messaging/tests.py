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
        message.save()
        
        # Check if message history was created
        self.assertEqual(MessageHistory.objects.count(), 1)
        history = MessageHistory.objects.first()
        self.assertEqual(history.message, message)
        self.assertEqual(history.old_content, "Original content")
        self.assertTrue(message.edited)

class ORMTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'password')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'password')
        
        # Create some messages
        self.message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message 1"
        )
        self.message2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message 2",
            read=True
        )
    
    def test_unread_messages_manager(self):
        """Test custom manager for unread messages"""
        unread_messages = Message.unread_messages.for_user(self.user2)
        self.assertEqual(unread_messages.count(), 1)
        self.assertEqual(unread_messages.first(), self.message1)
    
    def test_threaded_conversations(self):
        """Test threaded conversations with replies"""
        parent_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Parent message"
        )
        
        reply = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply message",
            parent_message=parent_message
        )
        
        # Test prefetch_related for optimization
        messages_with_replies = Message.objects.filter(
            parent_message__isnull=True
        ).prefetch_related('replies')
        
        self.assertEqual(messages_with_replies.count(), 1)
        parent = messages_with_replies.first()
        self.assertEqual(parent.replies.count(), 1)
        self.assertEqual(parent.replies.first(), reply)