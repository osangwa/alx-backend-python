from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view(), name='conversations'),
    path('unread/', views.UnreadMessagesView.as_view(), name='unread_messages'),
    path('thread/<int:message_id>/', views.ThreadDetailView.as_view(), name='thread_detail'),
    path('message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('message/<int:message_id>/history/', views.view_message_history, name='message_history'),
    path('message/<int:message_id>/mark-read/', views.mark_as_read, name='mark_as_read'),
    path('delete-account/', views.delete_user, name='delete_account'),
]