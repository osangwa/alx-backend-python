from django.contrib import admin
from .models import Message, Notification, MessageHistory

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'receiver', 'timestamp', 'read', 'edited']
    list_filter = ['timestamp', 'read', 'edited']
    search_fields = ['content', 'sender__username', 'receiver__username']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'timestamp', 'read']
    list_filter = ['timestamp', 'read']
    search_fields = ['user__username', 'message__content']

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'edited_at']
    list_filter = ['edited_at']
    search_fields = ['message__content', 'old_content']