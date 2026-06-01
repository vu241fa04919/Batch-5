from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('warden', 'Warden'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    room_number = models.CharField(max_length=20, blank=True, null=True)
    hostel_block = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Complaint(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    )
    
    CATEGORY_CHOICES = (
        ('Electrical', 'Electrical'),
        ('Plumbing', 'Plumbing'),
        ('Housekeeping', 'Housekeeping'),
        ('Internet/Wi-Fi', 'Internet/Wi-Fi'),
        ('Mess/Food', 'Mess/Food'),
        ('Other', 'Other'),
    )

    student = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='complaints',
        limit_choices_to={'role': 'student'}
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES, default='Other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    warden_remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id}: {self.title} - {self.student.username} ({self.status})"

    def save(self, *args, **kwargs):
        # Automatically set resolved_at when status changes to Resolved
        if self.status == 'Resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status != 'Resolved':
            self.resolved_at = None
        super().save(*args, **kwargs)


class Notification(models.Model):
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    complaint = models.ForeignKey(
        Complaint, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        blank=True, 
        null=True
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}"
