# messaging_app/chats/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message, User
from .serializers import (
    ConversationSerializer, MessageSerializer, 
    ConversationCreateSerializer, MessageCreateSerializer,
    UserSerializer, ConversationDetailSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['first_name', 'last_name', 'created_at']
    filterset_fields = ['role']

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['participants__first_name', 'participants__last_name', 'participants__email']
    ordering_fields = ['created_at']
    filterset_fields = ['participants__user_id']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        elif self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        # Filter conversations for specific user if user_id is provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Conversation.objects.filter(participants__user_id=user_id).distinct()
        return Conversation.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if we have at least 2 participants for a conversation
        participant_ids = serializer.validated_data.get('participant_ids', [])
        if len(participant_ids) < 2:
            return Response(
                {'error': 'A conversation must have at least 2 participants'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation = serializer.save()
        
        # If there's an initial message, create it
        initial_message = serializer.validated_data.get('initial_message')
        if initial_message:
            # Use the first participant as sender for the initial message
            sender = User.objects.get(user_id=participant_ids[0])
            Message.objects.create(
                sender=sender,
                conversation=conversation,
                message_body=initial_message
            )
        
        # Return the created conversation with full details
        full_serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to an existing conversation"""
        conversation = self.get_object()
        serializer = MessageCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check if sender is a participant in the conversation
            sender_id = serializer.validated_data['sender_id']
            if not conversation.participants.filter(user_id=sender_id).exists():
                return Response(
                    {'error': 'Sender is not a participant in this conversation'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            message = Message.objects.create(
                sender=User.objects.get(user_id=sender_id),
                conversation=conversation,
                message_body=serializer.validated_data['message_body']
            )
            
            message_serializer = MessageSerializer(message)
            return Response(message_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages for a specific conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all()
        
        # Apply filtering and ordering
        message_filter = filters.SearchFilter()
        filtered_queryset = message_filter.filter_queryset(request, messages, self)
        
        # Apply pagination
        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(filtered_queryset, many=True)
        return Response(serializer.data)


    # In chats/views.py, update MessageViewSet to handle nested routes
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['message_body', 'sender__first_name', 'sender__last_name']
    ordering_fields = ['sent_at']
    filterset_fields = ['sender__user_id', 'conversation__conversation_id']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        queryset = Message.objects.all()
        
        # Handle nested routing - get messages for specific conversation
        conversation_id = self.kwargs.get('conversation_pk')
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        
        # Filter by sender_id if provided
        sender_id = self.request.query_params.get('sender_id')
        if sender_id:
            queryset = queryset.filter(sender__user_id=sender_id)
            
        return queryset
    
    def perform_create(self, serializer):
        # Handle nested creation - automatically set conversation from URL
        conversation_id = self.kwargs.get('conversation_pk')
        if conversation_id:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            serializer.save(conversation=conversation)
        else:
            serializer.save()