from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views import View
from .models import Message, User

@method_decorator(login_required, name='dispatch')
@method_decorator(cache_page(60), name='dispatch')
class ConversationListView(View):
    """View to display conversations with caching"""
    
    def get(self, request):
        # Get messages for the current user with optimization
        received_messages = Message.objects.filter(
            receiver=request.user
        ).select_related('sender').prefetch_related('replies')
        
        sent_messages = Message.objects.filter(
            sender=request.user
        ).select_related('receiver').prefetch_related('replies')
        
        # Get unread messages count using custom manager
        unread_count = Message.unread_messages.for_user(request.user).count()
        
        context = {
            'received_messages': received_messages,
            'sent_messages': sent_messages,
            'unread_count': unread_count,
        }
        
        return render(request, 'messaging/conversations.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(cache_page(60), name='dispatch')
class ThreadDetailView(View):
    """View to display a specific message thread with caching"""
    
    def get(self, request, message_id):
        message = get_object_or_404(
            Message.objects.select_related('sender', 'receiver')
                          .prefetch_related('replies__sender', 'replies__receiver'),
            id=message_id
        )
        
        # Get message history if any
        history = message.history.all().order_by('-edited_at')
        
        context = {
            'message': message,
            'history': history,
        }
        
        return render(request, 'messaging/thread_detail.html', context)

@login_required
def delete_user(request):
    """View to delete user account"""
    if request.method == 'POST':
        user = request.user
        user.delete()
        # User will be logged out automatically
        return render(request, 'messaging/account_deleted.html')
    
    return render(request, 'messaging/confirm_delete.html')