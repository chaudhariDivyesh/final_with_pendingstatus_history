# import uuid
# from django.db import models
# from django.conf import settings
# from django.core.mail import send_mail
# from timetable.models import LectureHall, TimeSlot

# class Booking(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     lecture_hall = models.ForeignKey(LectureHall, on_delete=models.CASCADE)
#     date = models.DateField()
#     time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
#     purpose = models.TextField(blank=True, null=True)
#     approvals_pending = models.JSONField(default=dict)

#     STATUS_CHOICES = [
#         ('Pending', 'Pending'),
#         ('Approved', 'Approved'),
#         ('Rejected', 'Rejected')
#     ]
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
#     approval_token = models.UUIDField(default=uuid.uuid4, unique=True)

#     def approve(self, authority_email):
#         """Marks approval from a specific authority and updates status."""
#         if authority_email in self.approvals_pending:
#             self.approvals_pending[authority_email] = True
#             self.save()

#         if all(self.approvals_pending.values()):
#             self.status = 'Approved'
#             self.save()
#             self._handle_conflicting_bookings()

#     def _handle_conflicting_bookings(self):
#         """Rejects conflicting bookings for the same time slot and notifies users."""
#         conflicting_bookings = Booking.objects.filter(
#             date=self.date,
#             time_slot=self.time_slot,
#             status='Pending'
#         ).exclude(id=self.id)

#         for booking in conflicting_bookings:
#             booking.status = 'Rejected'
#             booking.save()
#             self._notify_conflicting_booking(booking)

#     def _notify_conflicting_booking(self, booking):
#         """Notify the user of the rejection of their booking due to a conflict."""
#         send_mail(
#             subject="Your Booking has been Canceled Due to a Conflict",
#             message=(
#                 f"Dear {booking.user.username},\n\n"
#                 f"Your booking for {booking.lecture_hall.name} on {booking.date} at "
#                 f"{booking.time_slot.start_time} - {booking.time_slot.end_time} has been canceled "
#                 f"because another user was approved for the same time slot.\n\n"
#                 "We apologize for the inconvenience. Please book a different time.\n\n"
#                 "Best regards,\nLHC Booking Portal"
#             ),
#             from_email="noreply@lhcportal.com",
#             recipient_list=[booking.user.email],
#         )

#     def __str__(self):
#         return f"Booking for {self.user.username} on {self.date} at {self.lecture_hall.name} ({self.status})"
import uuid
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from timetable.models import LectureHall, TimeSlot

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lecture_hall = models.ForeignKey(LectureHall, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    purpose = models.TextField(blank=True, null=True)
    approvals_pending = models.JSONField(default=dict)

    ac_required = models.BooleanField(default=False)
    projector_required = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approval_token = models.UUIDField(default=uuid.uuid4, unique=True)

    def approve(self, authority_email):
        """Marks approval from a specific authority and updates status."""
        if authority_email in self.approvals_pending:
            self.approvals_pending[authority_email] = True
            self.save()

        if all(self.approvals_pending.values()):
            self.status = 'Approved'
            self.save()
            self._handle_conflicting_bookings()

    def _handle_conflicting_bookings(self):
        """Rejects conflicting bookings for the same time slot and notifies users."""
        conflicting_bookings = Booking.objects.filter(
            date=self.date,
            lecture_hall=self.lecture_hall,
            time_slot=self.time_slot,
            status='Pending'
        ).exclude(id=self.id)

        for booking in conflicting_bookings:
            booking.status = 'Rejected'
            booking.save()
            self._notify_conflicting_booking(booking)

    def _notify_conflicting_booking(self, booking):
        """Notify the user of the rejection of their booking due to a conflict."""
        send_mail(
            subject="Your Booking has been Canceled Due to a Conflict",
            message=(
                f"Dear {booking.user.username},\n\n"
                f"Your booking for {booking.lecture_hall.name} on {booking.date} at "
                f"{booking.time_slot.start_time} - {booking.time_slot.end_time} has been canceled "
                f"because another user was approved for the same time slot.\n\n"
                "We apologize for the inconvenience. Please book a different time.\n\n"
                "Best regards,\nLHC Booking Portal"
            ),
            from_email="noreply@lhcportal.com",
            recipient_list=[booking.user.email],
        )

    def calculate_price(self):
        """Calculate the total price based on AC and projector requirements."""
        base_price = 0

        if self.ac_required:
            base_price += self.lecture_hall.ac_price

        if self.projector_required and self.lecture_hall.id in [18, 19, 20]:  
            base_price += self.lecture_hall.projector_price

        base_hours = 3
        extra_hours = max(0, 1 - base_hours)  
        base_price += (extra_hours * (self.lecture_hall.ac_price * 0.35))

        self.price = base_price
        self.save()

    def __str__(self):
        return f"Booking for {self.user.username} on {self.date} at {self.lecture_hall.name} ({self.status})"
