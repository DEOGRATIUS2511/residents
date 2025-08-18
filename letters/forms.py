from django import forms
from .models import LetterRequest, LetterType

class LetterRequestForm(forms.ModelForm):
    class Meta:
        model = LetterRequest
        fields = ['letter_type', 'purpose', 'additional_info', 'priority']
        widgets = {
            'letter_type': forms.Select(attrs={'class': 'form-select'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'State clearly why you need this letter'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional: any extra information for the officer'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = LetterType.objects.filter(is_active=True)
        if not qs.exists():
            qs = LetterType.objects.all()
        self.fields['letter_type'].queryset = qs
        # Improve select placeholders
        self.fields['letter_type'].empty_label = 'Select letter type'
        self.fields['priority'].empty_label = 'Select priority level'
