# chats/filters.py
import django_filters
from .models import Message, Conversation
from django_filters import rest_framework as filters

class MessageFilter(filters.FilterSet):
    conversation = filters.UUIDFilter(field_name='conversation__conversation_id')
    sender = filters.UUIDFilter(field_name='sender__user_id')
    sent_after = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_before = filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    search = filters.CharFilter(field_name='message_body', lookup_expr='icontains')
    
    class Meta:
        model = Message
        fields = ['conversation', 'sender', 'sent_after', 'sent_before', 'search']

class ConversationFilter(filters.FilterSet):
    participant = filters.UUIDFilter(field_name='participants__user_id')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Conversation
        fields = ['participant', 'created_after', 'created_before']
