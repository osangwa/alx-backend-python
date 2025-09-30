# messaging_app/chats/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

# Use Django's get_user_model to work with custom user model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'full_name', 'email', 'phone_number', 'role', 'created_at']
        read_only_fields = ['user_id', 'created_at']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True, required=False)
    conversation_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'sender_id', 'conversation', 'conversation_id', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sender', 'sent_at']
    
    def create(self, validated_data):
        sender_id = validated_data.pop('sender_id', None)
        conversation_id = validated_data.pop('conversation_id', None)
        
        if sender_id:
            try:
                sender = User.objects.get(user_id=sender_id)
                validated_data['sender'] = sender
            except User.DoesNotExist:
                raise serializers.ValidationError({"sender_id": "User with this ID does not exist"})
        
        if conversation_id:
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_id)
                validated_data['conversation'] = conversation
            except Conversation.DoesNotExist:
                raise serializers.ValidationError({"conversation_id": "Conversation with this ID does not exist"})
        
        return super().create(validated_data)

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True
    )
    participant_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_preview = serializers.CharField(source='get_last_message_preview', read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 
            'participants', 
            'participant_ids', 
            'participant_count',
            'messages', 
            'last_message',
            'last_message_preview',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'participants', 'messages', 'created_at']
    
    def get_participant_count(self, obj):
        return obj.participants.count()
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create(**validated_data)
        
        # Add participants to the conversation
        for user_id in participant_ids:
            try:
                user = User.objects.get(user_id=user_id)
                conversation.participants.add(user)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User with ID {user_id} does not exist")
        
        return conversation

class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True,
        help_text="List of user IDs to include in the conversation"
    )
    initial_message = serializers.CharField(
        write_only=True, 
        required=False,
        allow_blank=True,
        help_text="Optional initial message to start the conversation"
    )
    
    class Meta:
        model = Conversation
        fields = ['participant_ids', 'initial_message']

class ConversationDetailSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'message_count', 'created_at']
        read_only_fields = ['conversation_id', 'participants', 'messages', 'created_at']
    
    def get_messages(self, obj):
        messages = obj.messages.all().order_by('sent_at')
        return MessageSerializer(messages, many=True).data
    
    def get_message_count(self, obj):
        return obj.messages.count()

class MessageCreateSerializer(serializers.ModelSerializer):
    sender_id = serializers.UUIDField(write_only=True)
    conversation_id = serializers.UUIDField(write_only=True)
    message_body = serializers.CharField(
        max_length=1000,
        required=True,
        help_text="The content of the message"
    )
    
    class Meta:
        model = Message
        fields = ['sender_id', 'conversation_id', 'message_body']
    
    def create(self, validated_data):
        sender_id = validated_data.pop('sender_id')
        conversation_id = validated_data.pop('conversation_id')
        
        try:
            sender = User.objects.get(user_id=sender_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"sender_id": "User with this ID does not exist"})
        
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError({"conversation_id": "Conversation with this ID does not exist"})
        
        # Check if sender is a participant in the conversation
        if not conversation.participants.filter(user_id=sender_id).exists():
            raise serializers.ValidationError({"sender_id": "User is not a participant in this conversation"})
        
        return Message.objects.create(
            sender=sender,
            conversation=conversation,
            message_body=validated_data['message_body']
        )

# Add a method to the Conversation model to get last message preview
# Add this to your models.py or here as a mixin
def get_last_message_preview(self):
    last_message = self.messages.last()
    if last_message:
        preview = last_message.message_body[:50]
        if len(last_message.message_body) > 50:
            preview += "..."
        return preview
    return "No messages yet"

# Add this method to the Conversation model
# You can either add it directly to models.py or use this approach
Conversation.get_last_message_preview = get_last_message_preview