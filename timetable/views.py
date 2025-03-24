from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from datetime import datetime, timedelta
from .models import LectureHall, TimeSlot, FixedLecture
from bookings.models import Booking
import logging

logger = logging.getLogger(__name__)

def timetable_home(request):
    lecture_halls = LectureHall.objects.all()
    return render(request, "timetable/home.html", {"lecture_halls": lecture_halls})

def timetable_view(request, hall_id):
    hall = get_object_or_404(LectureHall, id=hall_id)

    # Get selected date or default to today
    selected_date_str = request.GET.get("date")
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            return HttpResponse("Invalid date format", status=400)
    else:
        selected_date = datetime.today().date()

    # Get start (Monday) and end (Sunday) of the selected week
    start_of_week = selected_date - timedelta(days=selected_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Get all time slots
    time_slots = TimeSlot.objects.all().order_by("start_time")

    # Fetch fixed lectures & approved/pending bookings for the week
    fixed_lectures = FixedLecture.objects.filter(hall=hall)
    bookings = Booking.objects.filter(
        lecture_hall=hall, 
        date__range=[start_of_week, end_of_week]
    ).exclude(status="Rejected")  # Exclude rejected bookings from timetable

    # Group bookings by (date, time_slot) key
    booking_dict = {}
    for booking in bookings:
        key = (booking.date, booking.time_slot.id)
        if key not in booking_dict:
            booking_dict[key] = []
        booking_dict[key].append(booking)

    # Create structured schedule
    schedule = {}
    for day_offset in range(7):  # Monday to Sunday
        date = start_of_week + timedelta(days=day_offset)
        weekday = date.strftime("%A")

        schedule[weekday] = []
        for time_slot in time_slots:
            lecture = fixed_lectures.filter(day=weekday, time_slot=time_slot).first()
            slot_bookings = booking_dict.get((date, time_slot.id), [])

            # Get approved booking
            approved_booking = next((b for b in slot_bookings if b.status == "Approved"), None)

            # Get pending bookings only for the requesting user
            pending_bookings = []
            for b in slot_bookings:
                if b.status == "Pending" and b.user == request.user:
                    # Find the next authority who has not approved yet
                    remaining_authorities = [email for email, approved in b.approvals_pending.items() if not approved]
                    pending_bookings.append({
                        "booking": b,
                        "remaining_authority": remaining_authorities[0] if remaining_authorities else "Waiting for final approval"
                    })

            # Construct timetable entry
            entry = {
                "date": date.strftime("%Y-%m-%d"),
                "time_slot": time_slot,
                "subject": lecture.subject if lecture else None,
                "approved_booking": approved_booking,
                "pending_bookings": pending_bookings,
            }
            schedule[weekday].append(entry)

    return render(request, "timetable/timetable.html", {
        "hall": hall,
        "schedule": schedule,
        "selected_date": selected_date.strftime("%Y-%m-%d"),
    })
