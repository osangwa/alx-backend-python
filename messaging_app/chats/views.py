# messaging_app/chats/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Conversation, Message, User
from .serializers import (
    ConversationSerializer, MessageSerializer, 
    ConversationCreateSerializer, MessageCreateSerializer,
    UserSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        # Filter conversations for the current user (you can implement user authentication later)
        # For now, return all conversations
        return Conversation.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        
        # Return the created conversation with full details
        full_serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        queryset = Message.objects.all()
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # In a real application, you'd get the sender from the authenticated user
        # For now, we'll use the first user as sender (you can modify this logic)
        sender = User.objects.first()
        if not sender:
            return Response(
                {'error': 'No users available to send message'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get conversation from URL parameter or request data
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response(
                {'error': 'conversation_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        message = Message.objects.create(
            sender=sender,
            conversation=conversation,
            message_body=serializer.validated_data['message_body']
        )
        
        full_serializer = MessageSerializer(message)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)