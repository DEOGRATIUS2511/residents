from django.contrib import admin
from .models import Announcement, Complaint, ComplaintResponse, Suggestion

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'is_active', 'created_by', 'created_at', 'expires_at')
    list_filter = ('priority', 'is_active', 'created_at', 'expires_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'submitted_by', 'assigned_to', 'submitted_at')
    list_filter = ('status', 'category', 'anonymous', 'submitted_at')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('submitted_at', 'updated_at')

@admin.register(ComplaintResponse)
class ComplaintResponseAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'responded_by', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at', 'responded_by')
    readonly_fields = ('created_at',)

@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'submitted_by', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('title', 'description')
    readonly_fields = ('submitted_at', 'updated_at')
