from django.contrib import admin
from .models import LetterType, LetterRequest, GeneratedLetter

@admin.register(LetterType)
class LetterTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')

@admin.register(LetterRequest)
class LetterRequestAdmin(admin.ModelAdmin):
    list_display = ('resident', 'letter_type', 'status', 'priority', 'request_date', 'approved_by')
    list_filter = ('status', 'priority', 'letter_type', 'request_date')
    search_fields = ('resident__first_name', 'resident__last_name', 'resident__nida_number', 'purpose')
    readonly_fields = ('request_date', 'approval_date', 'completion_date')
    
    fieldsets = (
        ('Request Information', {
            'fields': ('resident', 'letter_type', 'purpose', 'additional_info', 'priority')
        }),
        ('Status', {
            'fields': ('status', 'requested_by', 'approved_by')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes', 'rejection_reason')
        }),
        ('Generated Letter', {
            'fields': ('generated_letter_path',)
        }),
        ('Timestamps', {
            'fields': ('request_date', 'approval_date', 'completion_date')
        }),
    )

@admin.register(GeneratedLetter)
class GeneratedLetterAdmin(admin.ModelAdmin):
    list_display = ('letter_request', 'generated_at', 'generated_by')
    list_filter = ('generated_at', 'generated_by')
    readonly_fields = ('generated_at',)
