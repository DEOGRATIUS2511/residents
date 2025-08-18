from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Visitor, VisitorLog
from .forms import VisitorRegistrationForm

@login_required
def visitor_log(request):
    if request.user.role not in ['admin', 'clerk']:
        messages.error(request, 'Access denied. Admin or clerk privileges required.')
        return redirect('home')
    
    visitors = Visitor.objects.all().select_related('household_visited').order_by('-entry_time')
    paginator = Paginator(visitors, 20)
    page_number = request.GET.get('page')
    visitors = paginator.get_page(page_number)
    
    return render(request, 'visitors/log.html', {'visitors': visitors})

@login_required
def register_visitor(request):
    if request.user.role not in ['admin', 'clerk']:
        messages.error(request, 'Access denied. Admin or clerk privileges required.')
        return redirect('home')
    
    if request.method == 'POST':
        form = VisitorRegistrationForm(request.POST)
        if form.is_valid():
            visitor = form.save(commit=False)
            visitor.registered_by = request.user
            visitor.save()
            
            # Create visitor log entry
            VisitorLog.objects.create(
                visitor=visitor,
                action='entry',
                description=f'Visitor registered for entry at {visitor.entry_time}',
                performed_by=request.user
            )
            
            messages.success(request, f'Visitor {visitor.full_name} registered successfully!')
            return redirect('visitors:log')
    else:
        form = VisitorRegistrationForm()
    
    return render(request, 'visitors/register.html', {'form': form})

@login_required
def visitor_exit(request, pk):
    if request.user.role not in ['admin', 'clerk']:
        messages.error(request, 'Access denied. Admin or clerk privileges required.')
        return redirect('home')
    
    visitor = get_object_or_404(Visitor, pk=pk)
    
    if request.method == 'POST':
        visitor.actual_exit_time = timezone.now()
        visitor.is_active = False
        visitor.save()
        
        # Create visitor log entry
        VisitorLog.objects.create(
            visitor=visitor,
            action='exit',
            description=f'Visitor exited at {visitor.actual_exit_time}',
            performed_by=request.user
        )
        
        messages.success(request, f'Visitor {visitor.full_name} has been marked as exited.')
        return redirect('visitors:log')
    
    return render(request, 'visitors/exit.html', {'visitor': visitor})

@login_required
def visitor_detail(request, pk):
    if request.user.role not in ['admin', 'clerk']:
        messages.error(request, 'Access denied. Admin or clerk privileges required.')
        return redirect('home')
    
    visitor = get_object_or_404(Visitor, pk=pk)
    logs = visitor.logs.all().order_by('-timestamp')
    
    return render(request, 'visitors/detail.html', {
        'visitor': visitor,
        'logs': logs
    })
