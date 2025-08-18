from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Resident, Household
from .forms import ResidentRegistrationForm, HouseholdForm
from accounts.models import User

@login_required
def resident_list(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    search_query = request.GET.get('search', '')
    residents = (
        Resident.objects.filter(is_active=True)
        .select_related('household', 'user')
        .order_by('last_name', 'first_name', 'pk')
    )
    
    if search_query:
        residents = residents.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(nida_number__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    paginator = Paginator(residents, 20)
    page_number = request.GET.get('page')
    residents = paginator.get_page(page_number)
    
    return render(request, 'residents/list.html', {
        'residents': residents,
        'search_query': search_query
    })

@login_required
def resident_register(request):
    # Residents should be able to complete their own registration.
    # If a resident already has a profile, redirect to their profile page.
    if request.user.role == 'resident':
        if Resident.objects.filter(user=request.user).exists():
            messages.info(request, 'You have already completed your registration.')
            return redirect('home')
    
    if request.method == 'POST':
        resident_form = ResidentRegistrationForm(request.POST, request.FILES)
        household_form = HouseholdForm(request.POST)
        
        if resident_form.is_valid() and household_form.is_valid():
            household = household_form.save()
            resident = resident_form.save(commit=False)
            resident.household = household
            # Link the created resident to the logged-in user if the user is a resident.
            if request.user.role == 'resident':
                resident.user = request.user
            resident.save()
            
            messages.success(request, f'Resident {resident.full_name} registered successfully!')
            # After self-registration, send the user to the dashboard; otherwise to detail page.
            if request.user.role == 'resident':
                return redirect('home')
            return redirect('residents:detail', pk=resident.pk)
    else:
        resident_form = ResidentRegistrationForm()
        household_form = HouseholdForm()
    
    return render(request, 'residents/register.html', {
        'resident_form': resident_form,
        'household_form': household_form
    })

@login_required
def resident_profile(request):
    try:
        resident = request.user.resident
        # Get statistics for the resident
        from letters.models import LetterRequest
        letter_requests = LetterRequest.objects.filter(requested_by=request.user)
        
        context = {
            'resident': resident,
            'letter_requests_count': letter_requests.count(),
            'approved_requests_count': letter_requests.filter(status='approved').count(),
            'pending_requests_count': letter_requests.filter(status='pending').count(),
        }
        return render(request, 'residents/profile.html', context)
    except Resident.DoesNotExist:
        messages.info(request, 'Please complete your resident registration.')
        return redirect('residents:register')

@login_required
def resident_detail(request, pk):
    resident = get_object_or_404(Resident, pk=pk)
    
    # Check permissions
    if request.user.role == 'resident' and resident.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    return render(request, 'residents/detail.html', {'resident': resident})

@login_required
def resident_edit(request, pk):
    resident = get_object_or_404(Resident, pk=pk)
    
    # Check permissions
    if request.user.role == 'resident' and resident.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    elif request.user.role not in ['admin', 'clerk'] and resident.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ResidentRegistrationForm(request.POST, request.FILES, instance=resident)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resident information updated successfully!')
            return redirect('residents:detail', pk=resident.pk)
    else:
        form = ResidentRegistrationForm(instance=resident)
    
    return render(request, 'residents/edit.html', {'form': form, 'resident': resident})
