from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import ConversationViewSet, MessageViewSet, UserViewSet

# Using NestedDefaultRouter to automatically create nested routes
# for conversations and their messages
router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('conversations', ConversationViewSet)

# Create nested router for messages under conversations
conversations_router = routers.NestedDefaultRouter(router, 'conversations', lookup='conversation')
conversations_router.register('messages', MessageViewSet, basename='conversation-messages')

app_name = 'chats'

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]