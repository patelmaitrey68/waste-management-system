from django.contrib import admin
from .models import Feedback, collector_Registration

# Register your models here.

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)

@admin.register(collector_Registration)
class CollectorRegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'pincode', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'phone', 'pincode')
