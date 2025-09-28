# messaging_app/chats/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, UserViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

app_name = 'chats'

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]

# Alternatively, you can also include the router URLs directly:
# urlpatterns = router.urls