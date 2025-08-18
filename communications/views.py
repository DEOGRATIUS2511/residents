from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Announcement, Complaint, ComplaintResponse
from .forms import AnnouncementForm, ComplaintForm, ComplaintResponseForm

@login_required
def announcements(request):
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    paginator = Paginator(announcements, 10)
    page_number = request.GET.get('page')
    announcements = paginator.get_page(page_number)
    
    return render(request, 'communications/announcements.html', {'announcements': announcements})

@login_required
def create_announcement(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, 'Announcement created successfully!')
            return redirect('communications:announcements')
    else:
        form = AnnouncementForm()
    
    return render(request, 'communications/create_announcement.html', {'form': form})

@login_required
def delete_announcement(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    announcement = get_object_or_404(Announcement, pk=pk)

    if request.method == 'POST':
        title = announcement.title
        announcement.delete()
        messages.success(request, f'Announcement "{title}" deleted successfully!')
        return redirect('communications:announcements')

    # For non-POST, do not delete; just redirect back safely
    messages.info(request, 'No changes made to announcements.')
    return redirect('communications:announcements')

@login_required
def complaints(request):
    if request.user.role == 'admin':
        complaints = Complaint.objects.all().select_related('submitted_by').order_by('-submitted_at')
    else:
        complaints = Complaint.objects.filter(submitted_by=request.user).order_by('-submitted_at')
    
    paginator = Paginator(complaints, 10)
    page_number = request.GET.get('page')
    complaints = paginator.get_page(page_number)
    
    return render(request, 'communications/complaints.html', {'complaints': complaints})

@login_required
def create_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.submitted_by = request.user
            complaint.save()
            messages.success(request, 'Complaint submitted successfully!')
            return redirect('communications:complaints')
    else:
        form = ComplaintForm()
    
    return render(request, 'communications/create_complaint.html', {'form': form})

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Check permissions
    if request.user.role != 'admin' and complaint.submitted_by != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    responses = complaint.responses.all().order_by('created_at')
    return render(request, 'communications/complaint_detail.html', {
        'complaint': complaint,
        'responses': responses
    })

@login_required
def respond_complaint(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        form = ComplaintResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.complaint = complaint
            response.responded_by = request.user
            response.save()
            
            # Update complaint status if needed
            if complaint.status == 'open':
                complaint.status = 'in_progress'
                complaint.save()
            
            messages.success(request, 'Response added successfully!')
            return redirect('communications:complaint_detail', pk=pk)
    else:
        form = ComplaintResponseForm()
    
    return render(request, 'communications/respond_complaint.html', {
        'form': form,
        'complaint': complaint
    })
