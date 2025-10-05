from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages as django_messages
from django.contrib.auth import logout
from .models import Message, User, MessageHistory

@login_required
def edit_message(request, message_id):
    """View to edit a message"""
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    
    if request.method == 'POST':
        old_content = message.content
        new_content = request.POST.get('content')
        
        if new_content and new_content != old_content:
            # Set the editor before saving
            message.content = new_content
            message.edited_by = request.user  # Set the user who is editing
            # Add editor to instance for signal to use
            message._editor = request.user
            message.save()
            
            django_messages.success(request, 'Message updated successfully!')
            return redirect('thread_detail', message_id=message_id)
    
    return render(request, 'messaging/edit_message.html', {'message': message})

@method_decorator(login_required, name='dispatch')
@method_decorator(cache_page(60), name='dispatch')
class ConversationListView(View):
    """View to display conversations with caching"""
    
    def get(self, request):
        # Get messages for the current user with optimization
        received_messages = Message.objects.filter(
            receiver=request.user
        ).select_related('sender').prefetch_related('replies').only(
            'id', 'content', 'timestamp', 'read', 'edited', 'sender__username'
        )
        
        sent_messages = Message.objects.filter(
            sender=request.user
        ).select_related('receiver').prefetch_related('replies').only(
            'id', 'content', 'timestamp', 'read', 'edited', 'receiver__username'
        )
        
        # Get unread messages count using custom manager with .only() optimization
        unread_count = Message.unread.unread_for_user(request.user).count()
        
        # Get unread messages for display using custom manager with .only()
        unread_messages = Message.unread.unread_for_user(request.user)
        
        context = {
            'received_messages': received_messages,
            'sent_messages': sent_messages,
            'unread_count': unread_count,
            'unread_messages': unread_messages,
        }
        
        return render(request, 'messaging/conversations.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(cache_page(60), name='dispatch')
class UnreadMessagesView(View):
    """View to display only unread messages using custom manager"""
    
    def get(self, request):
        # Use custom manager to get unread messages for the user with .only() optimization
        unread_messages = Message.unread.unread_for_user(request.user)
        
        context = {
            'unread_messages': unread_messages,
            'unread_count': unread_messages.count(),
        }
        
        return render(request, 'messaging/unread_messages.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(cache_page(60), name='dispatch')
class ThreadDetailView(View):
    """View to display a specific message thread with caching"""
    
    def get(self, request, message_id):
        message = get_object_or_404(
            Message.objects.select_related('sender', 'receiver', 'edited_by')
                          .prefetch_related('replies__sender', 'replies__receiver', 'replies__edited_by')
                          .only('id', 'content', 'timestamp', 'edited', 'sender__username', 
                                'receiver__username', 'edited_by__username'),
            id=message_id
        )
        
        # Get message history if any with optimization
        history = message.history.all().select_related('edited_by').only(
            'old_content', 'edited_at', 'edited_by__username'
        ).order_by('-edited_at')
        
        context = {
            'message': message,
            'history': history,
        }
        
        return render(request, 'messaging/thread_detail.html', context)

@login_required
def edit_message(request, message_id):
    """View to edit a message"""
    message = get_object_or_404(Message, id=message_id, sender=request.user)
    
    if request.method == 'POST':
        old_content = message.content
        new_content = request.POST.get('content')
        
        if new_content and new_content != old_content:
            message.content = new_content
            message.edited_by = request.user  # Set the user who is editing
            message.save()
            
            django_messages.success(request, 'Message updated successfully!')
            return redirect('thread_detail', message_id=message_id)
    
    return render(request, 'messaging/edit_message.html', {'message': message})

@login_required
def view_message_history(request, message_id):
    """View to display message edit history"""
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user has permission to view history
    if message.sender != request.user and message.receiver != request.user:
        django_messages.error(request, 'You do not have permission to view this message history.')
        return redirect('conversations')
    
    # Use .only() to optimize the query
    history = MessageHistory.objects.filter(message=message).select_related('edited_by').only(
        'old_content', 'edited_at', 'edited_by__username'
    ).order_by('-edited_at')
    
    context = {
        'message': message,
        'history': history,
    }
    
    return render(request, 'messaging/message_history.html', context)

@login_required
def mark_as_read(request, message_id):
    """View to mark a message as read"""
    message = get_object_or_404(Message.unread.unread_for_user(request.user), id=message_id)
    message.read = True
    message.save()
    
    django_messages.success(request, 'Message marked as read!')
    return redirect('unread_messages')

@login_required
def delete_user(request):
    """View to delete user account and clean up related data"""
    if request.method == 'POST':
        user = request.user
        
        # The post_delete signal will handle cleaning up related data
        user.delete()
        
        # Logout the user after deletion
        logout(request)
        
        django_messages.success(request, 'Your account and all associated data have been deleted successfully.')
        return render(request, 'messaging/account_deleted.html')
    
    return render(request, 'messaging/confirm_delete.html')