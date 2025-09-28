# messaging_app/chats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

app_name = 'chats'

urlpatterns = [
    path('', include(router.urls)),
]