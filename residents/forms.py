from django import forms
from .models import Resident, Household

class HouseholdForm(forms.ModelForm):
    class Meta:
        model = Household
        fields = ['household_number', 'street_name', 'house_number', 'ward']
        widgets = {
            'household_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter household number'}),
            'street_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street/Avenue name'}),
            'house_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 12B'}),
            'ward': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ward name'}),
        }

class ResidentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Resident
        fields = [
            'first_name', 'middle_name', 'last_name', 'nida_number', 'date_of_birth',
            'place_of_birth', 'tribe', 'religion', 'gender', 'marital_status', 'phone_number', 'email',
            'occupation', 'education_level', 'special_category', 'relationship_to_head', 'photo'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle name (optional)'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'nida_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'National ID (NIDA) number'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
            'place_of_birth': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City/District of birth'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'marital_status': forms.Select(attrs={'class': 'form-select'}),
            'tribe': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Chagga'}),
            'religion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Christianity'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., +2557XXXXXXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Teacher'}),
            'education_level': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Bachelor'}),
            'special_category': forms.Select(attrs={'class': 'form-select'}),
            'relationship_to_head': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Head, Spouse, Child'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Improve select placeholders by customizing the empty label
        self.fields['gender'].empty_label = 'Select gender'
        self.fields['marital_status'].empty_label = 'Select marital status'
        self.fields['special_category'].empty_label = 'Select category'
