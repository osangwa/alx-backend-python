# chats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, UserViewSet

router = DefaultRouter()
router.register('conversations', ConversationViewSet)
router.register('messages', MessageViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]