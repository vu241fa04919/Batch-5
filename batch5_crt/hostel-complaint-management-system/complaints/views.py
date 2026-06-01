from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Complaint, Notification, CustomUser
import json

def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'warden':
            return redirect('admin:index')
        return redirect('student_dashboard')

    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'warden':
                return redirect('admin:index')
            return redirect('student_dashboard')
        else:
            error_message = "Invalid username or password. Please try again."

    return render(request, 'login.html', {'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('admin:index') # Warden goes to admin panel
    
    # Retrieve complaints for current logged-in student
    complaints = Complaint.objects.filter(student=request.user)
    
    # Calculate stats
    total_complaints = complaints.count()
    pending_complaints = complaints.filter(status='Pending').count()
    in_progress_complaints = complaints.filter(status='In Progress').count()
    resolved_complaints = complaints.filter(status='Resolved').count()
    
    # Pending is Pending + In Progress for visual simplicity or exact representation
    # In the reference image, it says "Pending: 2", "Resolved: 2", "My Complaints: 4"
    # So we can calculate total, pending (Pending + In Progress), and resolved.
    pending_sum = pending_complaints + in_progress_complaints

    # Fetch recent complaints (limit to 5)
    recent_complaints = complaints.order_by('-created_at')[:5]

    # Fetch notifications
    notifications = Notification.objects.filter(user=request.user)
    unread_notifications_count = notifications.filter(is_read=False).count()

    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_sum,
        'resolved_complaints': resolved_complaints,
        'recent_complaints': recent_complaints,
        'notifications': notifications[:5],
        'unread_count': unread_notifications_count,
        'categories': Complaint.CATEGORY_CHOICES,
    }
    return render(request, 'student_dashboard.html', context)


@login_required
@require_POST
def raise_complaint_api(request):
    if request.user.role != 'student':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        # Check if form data or JSON
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            title = data.get('title', '').strip()
            description = data.get('description', '').strip()
            category = data.get('category', '').strip()
        else:
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            category = request.POST.get('category', '').strip()

        if not title or not description or not category:
            return JsonResponse({'error': 'All fields (title, description, category) are required.'}, status=400)

        # Validate category
        valid_categories = [c[0] for c in Complaint.CATEGORY_CHOICES]
        if category not in valid_categories:
            return JsonResponse({'error': 'Invalid category selected.'}, status=400)

        # Create Complaint
        complaint = Complaint.objects.create(
            student=request.user,
            title=title,
            description=description,
            category=category,
            status='Pending'
        )

        # Notify student (success notification)
        Notification.objects.create(
            user=request.user,
            complaint=complaint,
            message=f"Your complaint #{complaint.id} ('{complaint.title[:30]}...') was raised successfully."
        )

        return JsonResponse({
            'message': 'Complaint raised successfully!',
            'complaint': {
                'id': complaint.id,
                'title': complaint.title,
                'category': complaint.category,
                'status': complaint.status,
                'created_at': complaint.created_at.strftime('%d %b %Y • %I:%M %p')
            }
        })
    except Exception as e:
        return JsonResponse({'error': f'Something went wrong: {str(e)}'}, status=500)


@login_required
@require_POST
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})
