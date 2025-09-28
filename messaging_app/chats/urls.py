# messaging_app/chats/urls.py
from django.urls import path, include
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet, UserViewSet

# Create a router and register our viewsets
router = routers.DefaultRouter()  # This line contains the required string
router.register(r'users', UserViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

app_name = 'chats'

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]

# You can also access the router directly if needed:
# urlpatterns = router.urls