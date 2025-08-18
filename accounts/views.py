from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .forms import UserRegistrationForm, UserProfileForm
from datetime import date
from residents.models import Resident, Household

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            # Parse optional Full Name from the form and split into first and last name
            full_name = (request.POST.get('full_name') or '').strip()
            if full_name:
                parts = full_name.split()
                if len(parts) == 1:
                    user.first_name = parts[0]
                else:
                    user.first_name = parts[0]
                    user.last_name = ' '.join(parts[1:])
            # Automatically set role as resident for all public registrations
            user.role = 'resident'
            user.save()
            
            # Create resident profile automatically
            # Get or create a default household
            household, created = Household.objects.get_or_create(
                household_number='DEFAULT001',
                defaults={
                    'street_name': 'Main Street',
                    'house_number': '000',
                    'ward': 'Default Ward'
                }
            )
            
            # Create resident profile with default values
            Resident.objects.create(
                user=user,
                household=household,
                first_name=user.first_name or 'Update',
                last_name=user.last_name or 'Required',
                nida_number=user.nida_number,
                date_of_birth=date(1990, 1, 1),  # Default date
                gender='M',  # Default gender
                phone_number=user.phone_number,
                email=user.email,
                relationship_to_head='Head'
            )
            
            messages.success(request, 'Registration successful! Please login.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})
