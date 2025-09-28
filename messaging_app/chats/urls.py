# chats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, UserViewSet

router = DefaultRouter()
router.register('conversations', ConversationViewSet, basename='conversation')
router.register('messages', MessageViewSet, basename='message')
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]