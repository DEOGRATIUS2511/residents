from django import forms
from .models import Visitor
from residents.models import Household

class VisitorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = [
            'full_name', 'id_number', 'phone_number', 'address',
            'household_visited', 'person_visited', 'purpose', 'purpose_details',
            'entry_time', 'expected_exit_time', 'notes'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'household_visited': forms.Select(attrs={'class': 'form-select'}),
            'person_visited': forms.TextInput(attrs={'class': 'form-control'}),
            'purpose': forms.Select(attrs={'class': 'form-select'}),
            'purpose_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'entry_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'expected_exit_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['household_visited'].queryset = Household.objects.all()
