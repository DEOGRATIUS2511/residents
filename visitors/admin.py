from django.contrib import admin
from .models import Visitor, VisitorLog

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'household_visited', 'person_visited', 'purpose', 'entry_time', 'is_currently_visiting')
    list_filter = ('purpose', 'is_active', 'entry_time')
    search_fields = ('full_name', 'id_number', 'person_visited', 'household_visited__household_number')
    readonly_fields = ('is_currently_visiting', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Visitor Information', {
            'fields': ('full_name', 'id_number', 'phone_number', 'address')
        }),
        ('Visit Details', {
            'fields': ('household_visited', 'person_visited', 'purpose', 'purpose_details')
        }),
        ('Time Information', {
            'fields': ('entry_time', 'expected_exit_time', 'actual_exit_time')
        }),
        ('Status', {
            'fields': ('is_active', 'notes', 'registered_by')
        }),
    )

@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('visitor', 'action', 'performed_by', 'timestamp')
    list_filter = ('action', 'timestamp', 'performed_by')
    search_fields = ('visitor__full_name', 'action', 'description')
    readonly_fields = ('timestamp',)
