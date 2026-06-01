from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Complaint, Notification

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'room_number', 'hostel_block', 'phone_number', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Hostel Information', {'fields': ('role', 'room_number', 'hostel_block', 'phone_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Hostel Information', {'fields': ('role', 'room_number', 'hostel_block', 'phone_number')}),
    )

class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'title', 'category', 'status', 'created_at', 'resolved_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['student__username', 'student__room_number', 'title', 'description', 'warden_remarks']
    list_editable = ['status']
    readonly_fields = ['created_at', 'resolved_at']
    
    actions = ['mark_in_progress', 'mark_resolved']

    def mark_in_progress(self, request, queryset):
        queryset.update(status='In Progress')
        # Create notifications for users
        for complaint in queryset:
            Notification.objects.create(
                user=complaint.student,
                complaint=complaint,
                message=f"Your complaint #{complaint.id} ('{complaint.title[:30]}...') is now In Progress."
            )
        self.message_user(request, f"Selected complaints marked as In Progress.")
    mark_in_progress.short_description = "Mark selected complaints as In Progress"

    def mark_resolved(self, request, queryset):
        for complaint in queryset:
            complaint.status = 'Resolved'
            complaint.save() # Triggers automatic resolved_at timestamp
            Notification.objects.create(
                user=complaint.student,
                complaint=complaint,
                message=f"Congratulations! Your complaint #{complaint.id} ('{complaint.title[:30]}...') has been Resolved."
            )
        self.message_user(request, f"Selected complaints marked as Resolved.")
    mark_resolved.short_description = "Mark selected complaints as Resolved"


class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'message']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(Notification, NotificationAdmin)

admin.site.site_header = "HostelCare Warden Panel"
admin.site.site_title = "HostelCare Admin"
admin.site.index_title = "Welcome, Hostel Warden"
