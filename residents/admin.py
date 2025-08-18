from django.contrib import admin
from .models import Household, Resident

@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ('household_number', 'street_name', 'house_number', 'ward', 'created_at')
    list_filter = ('ward', 'created_at')
    search_fields = ('household_number', 'street_name', 'house_number')

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'nida_number', 'gender', 'age', 'household', 'special_category', 'is_active')
    list_filter = ('gender', 'marital_status', 'special_category', 'is_active', 'registration_date')
    search_fields = ('first_name', 'last_name', 'nida_number', 'phone_number', 'email')
    readonly_fields = ('age',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'nida_number', 'date_of_birth', 'gender', 'marital_status', 'photo')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Household Information', {
            'fields': ('household', 'relationship_to_head')
        }),
        ('Additional Information', {
            'fields': ('occupation', 'education_level', 'special_category')
        }),
        ('System Information', {
            'fields': ('user', 'is_active')
        }),
    )
