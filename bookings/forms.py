from django import forms
from datetime import datetime
from .models import Booking
from timetable.models import FixedLecture, TimeSlot

class BookingForm(forms.ModelForm):
    time_slots = forms.ModelMultipleChoiceField(
        queryset=TimeSlot.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Booking
        fields = ["lecture_hall", "date", "time_slots"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "lecture_hall" in self.data and "date" in self.data:
            try:
                hall_id = int(self.data.get("lecture_hall"))
                date_str = self.data.get("date")
                date = datetime.strptime(date_str, "%Y-%m-%d").date()

                occupied_slots = set(
                    FixedLecture.objects.filter(hall_id=hall_id, day=date.strftime('%A'))
                    .values_list("time_slot", flat=True)
                ) | set(
                    Booking.objects.filter(lecture_hall_id=hall_id, date=date)
                    .exclude(status="Rejected")
                    .values_list("time_slot", flat=True)
                )

                self.fields["time_slots"].queryset = TimeSlot.objects.exclude(id__in=occupied_slots)
            except (ValueError, TypeError):
                self.fields["time_slots"].queryset = TimeSlot.objects.none()
        else:
            self.fields["time_slots"].queryset = TimeSlot.objects.none()
