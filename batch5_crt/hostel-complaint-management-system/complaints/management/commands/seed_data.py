from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from complaints.models import CustomUser, Complaint, Notification

class Command(BaseCommand):
    help = 'Seeds the database with initial users and complaints matching the reference image'

    def handle(self, *args, **kwargs):
        # 1. Clean existing data (optional but good for a deterministic seed)
        Complaint.objects.all().delete()
        Notification.objects.all().delete()
        CustomUser.objects.filter(username__in=['ananya', 'warden_sheela']).delete()

        self.stdout.write('Clearing existing mock data...')

        # 2. Create Student: Ananya (Password: ananya123)
        student = CustomUser.objects.create_user(
            username='ananya',
            email='ananya@hostel.edu',
            password='ananya123',
            role='student',
            room_number='205',
            hostel_block='Lotus Block A',
            phone_number='9876543210',
            first_name='Ananya',
            last_name=''
        )
        self.stdout.write(self.style.SUCCESS(f'Created student: {student.username} (Room 205)'))

        # 3. Create Warden: Sheela (Password: warden123, is_staff=True, is_superuser=True)
        warden = CustomUser.objects.create_superuser(
            username='warden_sheela',
            email='sheela@hostel.edu',
            password='warden123',
            role='warden',
            room_number='101',
            hostel_block='Lotus Block A',
            phone_number='9876543211',
            first_name='Sheela',
            last_name='Devi'
        )
        self.stdout.write(self.style.SUCCESS(f'Created warden admin: {warden.username}'))

        # 4. Create Complaints matching the UI stats
        # We need: 4 complaints in total (2 Pending, 2 Resolved)
        
        # Complaint 1: Water not available in bathroom (Pending) - 20 May 2024, 10:30 AM
        dt1 = timezone.make_aware(datetime(2026, 5, 20, 10, 30, 0))
        c1 = Complaint.objects.create(
            student=student,
            title='Water not available in bathroom',
            description='There has been no water supply in Lotus Block A, 2nd floor bathroom since morning. Please resolve this as it is causing extreme inconvenience.',
            category='Plumbing',
            status='Pending',
        )
        # Override auto_now_add for precise matching
        Complaint.objects.filter(id=c1.id).update(created_at=dt1)

        # Complaint 2: Fan not working in room (Resolved) - 18 May 2024, 09:15 PM
        dt2 = timezone.make_aware(datetime(2026, 5, 18, 21, 15, 0))
        c2 = Complaint.objects.create(
            student=student,
            title='Fan not working in room',
            description='The ceiling fan in room 205 is making a loud buzzing noise and not rotating. Might need a capacitor replacement.',
            category='Electrical',
            status='Resolved',
            warden_remarks='Electrician visited Room 205 and replaced the faulty capacitor. Fan is working fine now.',
            resolved_at=timezone.make_aware(datetime(2026, 5, 19, 11, 0, 0))
        )
        Complaint.objects.filter(id=c2.id).update(created_at=dt2)

        # Complaint 3: Wi-Fi signal very weak in corridor (Pending) - 22 May 2026, 04:00 PM
        dt3 = timezone.make_aware(datetime(2026, 5, 22, 16, 0, 0))
        c3 = Complaint.objects.create(
            student=student,
            title='Wi-Fi connection extremely slow',
            description='The Wi-Fi router on the second floor is frequently disconnecting and the download speeds are less than 1 Mbps. Cannot complete assignments.',
            category='Internet/Wi-Fi',
            status='Pending',
        )
        Complaint.objects.filter(id=c3.id).update(created_at=dt3)

        # Complaint 4: Cleanliness issue in study room (Resolved) - 15 May 2026, 11:00 AM
        dt4 = timezone.make_aware(datetime(2026, 5, 15, 11, 0, 0))
        c4 = Complaint.objects.create(
            student=student,
            title='Study room dustbins overflowing',
            description='The dustbins in the main library study room have not been cleared for three days. Bad smell is spreading.',
            category='Housekeeping',
            status='Resolved',
            warden_remarks='Housekeeping team cleared the bins and sanitized the study room area.',
            resolved_at=timezone.make_aware(datetime(2026, 5, 15, 16, 30, 0))
        )
        Complaint.objects.filter(id=c4.id).update(created_at=dt4)

        # 5. Create some notifications
        Notification.objects.create(
            user=student,
            complaint=c2,
            message="Your complaint #2 ('Fan not working...') has been marked as Resolved by Warden Sheela.",
            is_read=False
        )
        Notification.objects.create(
            user=student,
            complaint=c4,
            message="Your complaint #4 ('Study room dustbins...') has been marked as Resolved by Warden Sheela.",
            is_read=True
        )
        Notification.objects.create(
            user=student,
            message="Welcome to HostelCare! Raise complaints and track their progress live.",
            is_read=True
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with beautiful mock complaints matching the UI!'))
