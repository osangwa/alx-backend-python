# chats/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Conversation, Message, User
from .serializers import (
    ConversationSerializer, MessageSerializer, 
    ConversationCreateSerializer, MessageCreateSerializer,
    UserSerializer, ConversationDetailSerializer
)
from .permissions import IsParticipantOfConversation, IsMessageOwnerOrParticipant, IsOwnerOrReadOnly
from .pagination import MessagePagination

# Import filters conditionally to avoid circular imports
try:
    from .filters import MessageFilter, ConversationFilter
except ImportError:
    MessageFilter = None
    ConversationFilter = None

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['first_name', 'last_name', 'email']
    ordering_fields = ['first_name', 'last_name', 'created_at']
    filterset_fields = ['role']
    
    def get_queryset(self):
        # Users can only see their own profile by default
        if self.action == 'list':
            return User.objects.filter(user_id=self.request.user.user_id)
        return User.objects.all()

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['participants__first_name', 'participants__last_name', 'participants__email']
    ordering_fields = ['created_at']
    
    # Set filterset_class conditionally
    @property
    def filterset_class(self):
        return ConversationFilter if ConversationFilter else None
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        elif self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        # Users can only see conversations they are participating in
        return Conversation.objects.filter(participants=self.request.user)
    
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
        
        # Add the current user to participants if not already included
        if request.user.user_id not in participant_ids:
            participant_ids.append(request.user.user_id)
        
        # Check if all users exist
        users = []
        for user_id in participant_ids:
            try:
                user = User.objects.get(user_id=user_id)
                users.append(user)
            except User.DoesNotExist:
                return Response(
                    {'error': f'User with ID {user_id} does not exist'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create the conversation
        conversation = Conversation.objects.create()
        
        # Add participants to the conversation
        for user in users:
            conversation.participants.add(user)
        
        # If there's an initial message, create it
        initial_message = serializer.validated_data.get('initial_message', '')
        if initial_message:
            Message.objects.create(
                sender=request.user,
                conversation=conversation,
                message_body=initial_message
            )
        
        # Return the created conversation with full details
        full_serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsParticipantOfConversation])
    def send_message(self, request, pk=None):
        """Send a message to an existing conversation"""
        conversation = self.get_object()
        serializer = MessageCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            message_body = serializer.validated_data.get('message_body')
            
            # Create the message with current user as sender
            message = Message.objects.create(
                sender=request.user,
                conversation=conversation,
                message_body=message_body
            )
            
            message_serializer = MessageSerializer(message)
            return Response(message_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsParticipantOfConversation])
    def messages(self, request, pk=None):
        """Get all messages for a specific conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all()
        
        # Apply pagination
        paginator = MessagePagination()
        paginated_messages = paginator.paginate_queryset(messages, request, view=self)
        serializer = MessageSerializer(paginated_messages, many=True)
        return paginator.get_paginated_response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsMessageOwnerOrParticipant]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['message_body', 'sender__first_name', 'sender__last_name']
    ordering_fields = ['sent_at']
    pagination_class = MessagePagination
    
    # Set filterset_class conditionally
    @property
    def filterset_class(self):
        return MessageFilter if MessageFilter else None
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def get_queryset(self):
        # Users can only see messages from conversations they are participating in
        user_conversations = Conversation.objects.filter(participants=self.request.user)
        return Message.objects.filter(conversation__in=user_conversations)
    
    def perform_create(self, serializer):
        # Automatically set the sender to the current user
        serializer.save(sender=self.request.user)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent messages with pagination"""
        recent_messages = self.get_queryset().order_by('-sent_at')
        
        # Apply pagination
        paginator = MessagePagination()
        paginated_messages = paginator.paginate_queryset(recent_messages, request, view=self)
        serializer = MessageSerializer(paginated_messages, many=True)
        return paginator.get_paginated_response(serializer.data)