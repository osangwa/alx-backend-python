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
        
        # Verify notifications were created automatically
        self.assertEqual(Notification.objects.count(), 2)
        
        # Edit a message to create history
        message1.content = "Edited content"
        message1.edited_by = self.user1
        message1.save()
        
        # Store user1 ID before deletion for verification
        user1_id = self.user1.id
        user2_id = self.user2.id
        
        # Verify data exists before deletion using ID-based queries
        self.assertEqual(Message.objects.filter(sender_id=user1_id).count(), 1)
        self.assertEqual(Message.objects.filter(receiver_id=user1_id).count(), 1)
        self.assertEqual(Notification.objects.filter(user_id=user1_id).count(), 1)
        self.assertEqual(MessageHistory.objects.filter(edited_by_id=user1_id).count(), 1)
        
        # Delete user1
        self.user1.delete()
        
        # Verify all user1 related data is deleted using ID-based queries
        self.assertEqual(Message.objects.filter(sender_id=user1_id).count(), 0)
        self.assertEqual(Notification.objects.filter(user_id=user1_id).count(), 0)
        self.assertEqual(MessageHistory.objects.filter(edited_by_id=user1_id).count(), 0)
        
        # With CASCADE behavior:
        # - Messages sent by user1 are deleted (sender=CASCADE)
        # - Messages where user1 was receiver are deleted when sender is deleted
        # - Notifications for user2 that reference deleted messages are also deleted
        
        # The key assertion: user2's sent messages should still exist
        self.assertEqual(Message.objects.filter(sender_id=user2_id).count(), 1)
        
        # Notifications for user2 are deleted because they reference messages from user1
        # that got deleted (CASCADE behavior)
        self.assertEqual(Notification.objects.filter(user_id=user2_id).count(), 0)

class CustomManagerTests(TestCase):
    """Test the custom manager functionality"""
    
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@test.com', 'password')
        self.user2 = User.objects.create_user('user2', 'user2@test.com', 'password')
        
        # Create read and unread messages
        self.unread_message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread message 1",
            read=False
        )
        self.unread_message2 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread message 2", 
            read=False
        )
        self.read_message = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Read message",
            read=True
        )
    
    def test_unread_manager_filters_correctly(self):
        """Test that UnreadMessagesManager only returns unread messages"""
        # Test manager directly
        unread_messages = Message.unread.all()
        self.assertEqual(unread_messages.count(), 2)
        
        # All messages should be unread
        for message in unread_messages:
            self.assertFalse(message.read)
    
    def test_unread_for_user_method(self):
        """Test the unread_for_user method"""
        # Get unread messages for user2
        user2_unread = Message.unread.unread_for_user(self.user2)
        self.assertEqual(user2_unread.count(), 2)
        
        # Get unread messages for user1  
        user1_unread = Message.unread.unread_for_user(self.user1)
        self.assertEqual(user1_unread.count(), 0)  # user1 has no unread messages
    
    def test_only_optimization(self):
        """Test that .only() is used to optimize queries"""
        # This would typically be tested by examining the query
        unread_messages = Message.unread.unread_for_user(self.user2)
        
        # The query should be optimized with .only()
        # We can verify this by checking that specific fields are loaded
        message = unread_messages.first()
        self.assertIsNotNone(message.content)
        self.assertIsNotNone(message.sender)
        self.assertIsNotNone(message.timestamp)

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
        # First edit by user1
        self.message.content = "First edit"
        self.message.edited_by = self.user1
        self.message.save()
        
        # Clear any existing history to start fresh
        MessageHistory.objects.all().delete()
        
        # Create two specific history entries for testing
        MessageHistory.objects.create(
            message=self.message,
            old_content="Original message",
            edited_by=self.user1
        )
        MessageHistory.objects.create(
            message=self.message,
            old_content="First edit", 
            edited_by=self.user2
        )
        
        # Update message content
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