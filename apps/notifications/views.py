from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notification_list(request):
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    if request.GET.get('mark_all_read') == 'true':
        notifications.update(is_read=True)
        return redirect('notifications:list')

    context = {
        'notifications': notifications
    }
    return render(request, 'notifications/notification_list.html', context)

@login_required
def mark_as_read(request, pk):
    
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('HX-Request'):
        return render(request, 'notifications/partials/notification_item.html', {'notification': notification})
    
    return redirect('notifications:list')