# from django import forms
# from datetime import datetime
# from .models import Booking
# from timetable.models import FixedLecture, TimeSlot, LectureHall


# class BookingForm(forms.ModelForm):
#     time_slots = forms.ModelMultipleChoiceField(
#         queryset=TimeSlot.objects.none(),
#         widget=forms.CheckboxSelectMultiple,
#         required=True
#     )
#     ac_required = forms.BooleanField(required=False)
#     projector_required = forms.BooleanField(required=False)
#     purpose = forms.CharField(
#         widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Enter the purpose of booking..."}),
#         required=True
#     )

#     class Meta:
#         model = Booking
#         fields = ["lecture_hall", "date", "time_slots", "ac_required", "projector_required", "purpose"]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         if "lecture_hall" in self.data and "date" in self.data:
#             try:
#                 hall_id = int(self.data.get("lecture_hall"))
#                 date_str = self.data.get("date")
#                 date = datetime.strptime(date_str, "%Y-%m-%d").date()

#                 # Fetch lecture hall details
#                 lecture_hall = LectureHall.objects.get(id=hall_id)

#                 # Fetch occupied slots from FixedLecture and existing bookings
#                 occupied_slots = set(
#                     FixedLecture.objects.filter(hall_id=hall_id, day=date.strftime('%A'))
#                     .values_list("time_slot_id", flat=True)
#                 ) | set(
#                     Booking.objects.filter(lecture_hall_id=hall_id, date=date)
#                     .exclude(status="Rejected")
#                     .values_list("time_slots", flat=True)  # Fix for ManyToManyField
#                 )

#                 # Available time slots
#                 self.fields["time_slots"].queryset = TimeSlot.objects.exclude(id__in=occupied_slots)

#             except (ValueError, TypeError, LectureHall.DoesNotExist):
#                 self.fields["time_slots"].queryset = TimeSlot.objects.none()
#         else:
#             self.fields["time_slots"].queryset = TimeSlot.objects.none()
from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, date
from .models import Booking
from timetable.models import FixedLecture, TimeSlot, LectureHall

# Helper functions for validation
def is_exam_period(booking_date):
    MIDSEM_START_DATE = date(2025, 4, 1)
    MIDSEM_END_DATE = date(2025, 4, 10)
    ENDSEM_START_DATE = date(2025, 5, 1)
    ENDSEM_END_DATE = date(2025, 5, 10)
    
    return MIDSEM_START_DATE <= booking_date <= MIDSEM_END_DATE or \
           ENDSEM_START_DATE <= booking_date <= ENDSEM_END_DATE

def is_holiday_or_sunday(booking_date):
    HOLIDAY_DATES = [date(2025, 12, 25), date(2025, 1, 1)]
    return booking_date.weekday() == 6 or booking_date in HOLIDAY_DATES

def is_at_least_2_days_advance(booking_date):
    return (booking_date - date.today()).days >= 2

class BookingForm(forms.ModelForm):
    time_slots = forms.ModelMultipleChoiceField(
        queryset=TimeSlot.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    ac_required = forms.BooleanField(required=False)
    projector_required = forms.BooleanField(required=False)
    purpose = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Enter the purpose of booking..."}),
        required=True
    )
    booking_type = forms.ChoiceField(
        choices=[('academic', 'Academic'), ('non-academic', 'Non-Academic')],
        required=True,
        label="Booking Type"
    )

    class Meta:
        model = Booking
        fields = ["lecture_hall", "date", "time_slots", "ac_required", "projector_required", "purpose", "booking_type"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Store user reference
        super().__init__(*args, **kwargs)

        # Restrict booking type choices based on user role
        if self.user:
            if self.user.role == 'student':
                self.fields['booking_type'].choices = [('non-academic', 'Non-Academic')]
            else:
                self.fields['booking_type'].choices = [('academic', 'Academic'), ('non-academic', 'Non-Academic')]

        # Dynamically populate available time slots based on lecture hall & date
        if "lecture_hall" in self.data and "date" in self.data:
            try:
                hall_id = int(self.data.get("lecture_hall"))
                date_str = self.data.get("date")
                booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()

                # Fetch occupied time slots
                occupied_slots = set(
                    FixedLecture.objects.filter(hall_id=hall_id, day=booking_date.strftime('%A'))
                    .values_list("time_slot_id", flat=True)
                ) | set(
                    Booking.objects.filter(lecture_hall_id=hall_id, date=booking_date)
                    .exclude(status="Rejected")
                    .values_list("time_slots__id", flat=True)  # Fix for ManyToManyField
                )

                # Available time slots
                self.fields["time_slots"].queryset = TimeSlot.objects.exclude(id__in=occupied_slots)

            except (ValueError, TypeError, LectureHall.DoesNotExist):
                self.fields["time_slots"].queryset = TimeSlot.objects.none()
        else:
            self.fields["time_slots"].queryset = TimeSlot.objects.none()

    def clean_date(self):
        booking_date = self.cleaned_data['date']
        booking_type = self.cleaned_data.get('booking_type')

        # Prevent past bookings
        if booking_date < date.today():
            raise ValidationError("You cannot book a lecture hall for a past date.")

        # Restrict bookings during exam periods
        if is_exam_period(booking_date):
            raise ValidationError("Bookings are not allowed during midsem and endsem exams.")

        # Restrict students from making academic bookings
        if self.user and self.user.role == 'student' and booking_type == 'academic':
            raise ValidationError("Students cannot apply for academic bookings. Only faculty/admin can do so.")

        # Prevent academic bookings on holidays or Sundays
        if booking_type == 'academic' and is_holiday_or_sunday(booking_date):
            raise ValidationError("Academic bookings are not allowed on holidays or Sundays.")

        # Enforce 2-day advance booking for non-academic purposes
        if booking_type == 'non-academic' and not is_at_least_2_days_advance(booking_date):
            raise ValidationError("Non-academic bookings require at least 2 days in advance.")

        return booking_date


