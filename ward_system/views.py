from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from letters.models import LetterRequest
from communications.models import Complaint, Announcement
from residents.models import Resident
from visitors.models import Visitor

def home(request):
    context = {}
    
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            # Admin dashboard data
            context.update({
                'total_residents': Resident.objects.filter(is_active=True).count(),
                'pending_requests': LetterRequest.objects.filter(status='pending').count(),
                'completed_requests': LetterRequest.objects.filter(status='completed').count(),
                'active_visitors': Visitor.objects.filter(is_active=True, actual_exit_time__isnull=True).count(),
                'recent_requests': LetterRequest.objects.select_related('resident', 'letter_type').order_by('-request_date')[:5],
            })
        elif request.user.role == 'resident':
            # Resident dashboard data
            letter_requests = LetterRequest.objects.filter(requested_by=request.user)
            
            context.update({
                'letter_requests_count': letter_requests.count(),
                'approved_requests_count': letter_requests.filter(status='approved').count(),
                'pending_requests_count': letter_requests.filter(status='pending').count(),
                # Recently approved letters ready for download (limit 5)
                'approved_letters': letter_requests.filter(status='approved').select_related('letter_type').order_by('-request_date')[:5],
            })
        
        # Recent announcements for authenticated users
        context['announcements'] = Announcement.objects.filter(is_active=True).order_by('-created_at')[:3]
        
    else:
        # Public announcements for non-authenticated users
        context['public_announcements'] = Announcement.objects.filter(
            is_active=True,
            priority__in=['high', 'urgent']
        ).order_by('-created_at')[:5]
    
    return render(request, 'home.html', context)
