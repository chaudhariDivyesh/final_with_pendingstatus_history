# def send_approval_email(authority_email, bookings):
#     """Send a single email containing all approval tokens."""
#     tokens = [str(b.approval_token) for b in bookings]  # ✅ Convert UUIDs to strings
#     token_string = ",".join(tokens)  

#     approval_link = f"http://127.0.0.1:8000/bookings/approve/?tokens={token_string}"
#     rejection_link = f"http://127.0.0.1:8000/bookings/reject/?tokens={token_string}"

#     time_slots = ", ".join(f"{b.time_slot.start_time} - {b.time_slot.end_time}" for b in bookings)

#     send_mail(
#         subject="LHC Booking Approval Required",
#         message=(
#             f"A new booking request needs your approval.\n\n"
#             f"Lecture Hall: {bookings[0].lecture_hall.name}\n"
#             f"Date: {bookings[0].date}\n"
#             f"Time Slots: {time_slots}\n"
#             f"Requested by: {bookings[0].user.username}\n\n"
#             f"✅ Approve: {approval_link}\n"
#             f"❌ Reject: {rejection_link}"
#         ),
#         from_email="noreply@lhcportal.com",
#         recipient_list=[authority_email],
#     )

# @login_required
# def booking_form(request):
#     """Handles multiple-slot booking and prevents conflicts."""
#     if request.method == 'POST':
#         form = BookingForm(request.POST)
#         if form.is_valid():
#             lecture_hall = form.cleaned_data["lecture_hall"]
#             date = form.cleaned_data["date"]
#             time_slots = form.cleaned_data["time_slots"]

#             existing_bookings = Booking.objects.filter(
#                 lecture_hall=lecture_hall, date=date, time_slot__in=time_slots
#             ).exclude(status="Rejected")

#             if existing_bookings.exists():
#                 return render(request, 'bookings/booking_failed.html', {
#                     'message': 'One or more selected slots are already booked or pending.'
#                 })

#             authorities = list(request.user.authorities.all())
#             if not authorities:
#                 return render(request, 'bookings/booking_failed.html', {'message': 'No authorities assigned for approval'})

#             bookings = []
#             for time_slot in time_slots:
#                 booking = Booking.objects.create(
#                     user=request.user,
#                     lecture_hall=lecture_hall,
#                     date=date,
#                     time_slot=time_slot,
#                     status="Pending",
#                     approval_token=str(uuid.uuid4()),  
#                     approvals_pending={auth.email: False for auth in authorities}
#                 )
#                 bookings.append(booking)

#             first_authority_email = next(iter(bookings[0].approvals_pending.keys()), None)
#             if first_authority_email:
#                 send_approval_email(first_authority_email, bookings)

#             return redirect('bookings:booking_success')

#     else:
#         form = BookingForm()

#     return render(request, 'bookings/booking_form.html', {'form': form})
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.core.mail import send_mail
# from django.http import JsonResponse, HttpResponse
# from timetable.models import FixedLecture, TimeSlot, LectureHall
# from .models import Booking
# from .forms import BookingForm
# from datetime import datetime
# import uuid

# def get_pricing(request):
#     lecture_hall_id = request.GET.get("lecture_hall")
#     if not lecture_hall_id:
#         return JsonResponse({"error": "Missing lecture hall ID"}, status=400)

#     try:
#         hall = LectureHall.objects.get(id=lecture_hall_id)
#         return JsonResponse({
#             "ac_price": float(hall.ac_price),  # Convert Decimal to float for JSON
#             "non_ac_price": float(hall.non_ac_price),
#             "projector_price": float(hall.projector_price),
#             "extra_charge": round(float(hall.ac_price) * 0.35, 2)  # Fix Decimal multiplication
#         })
#     except LectureHall.DoesNotExist:
#         return JsonResponse({"error": "Lecture hall not found"}, status=404)
# def send_approval_email(authority_email, bookings):
#     """Send a single email containing all approval tokens."""
#     tokens = [str(b.approval_token) for b in bookings]
#     token_string = ",".join(tokens)

#     approval_link = f"http://127.0.0.1:8000/bookings/approve/?tokens={token_string}"
#     rejection_link = f"http://127.0.0.1:8000/bookings/reject/?tokens={token_string}"

#     time_slots = ", ".join(f"{b.time_slot.start_time} - {b.time_slot.end_time}" for b in bookings)

#     send_mail(
#         subject="LHC Booking Approval Required",
#         message=(
#             f"A new booking request needs your approval.\n\n"
#             f"Lecture Hall: {bookings[0].lecture_hall.name}\n"
#             f"Date: {bookings[0].date}\n"
#             f"Time Slots: {time_slots}\n"
#             f"Requested by: {bookings[0].user.username}\n\n"
#             f"AC Required: {'Yes' if bookings[0].ac_required else 'No'}\n"
#             f"Projector Required: {'Yes' if bookings[0].projector_required else 'No'}\n"
#             f"Purpose: {bookings[0].purpose}\n\n"
#             f"Estimated Price: {bookings[0].price} INR\n\n"
#             f"✅ Approve: {approval_link}\n"
#             f"❌ Reject: {rejection_link}"
#         ),
#         from_email="noreply@lhcportal.com",
#         recipient_list=[authority_email],
#     )

# @login_required
# def booking_form(request):
#     """Handles multiple-slot booking, price calculation, and conflict validation."""
#     if request.method == 'POST':
#         form = BookingForm(request.POST)
#         if form.is_valid():
#             lecture_hall = form.cleaned_data["lecture_hall"]
#             date = form.cleaned_data["date"]
#             time_slots = form.cleaned_data["time_slots"]
#             ac_required = form.cleaned_data["ac_required"]
#             projector_required = form.cleaned_data["projector_required"]
#             purpose = form.cleaned_data["purpose"]

#             existing_bookings = Booking.objects.filter(
#                 lecture_hall=lecture_hall, date=date, time_slot__in=time_slots
#             ).exclude(status="Rejected")

#             if existing_bookings.exists():
#                 return render(request, 'bookings/booking_failed.html', {
#                     'message': 'One or more selected slots are already booked or pending.'
#                 })

#             authorities = list(request.user.authorities.all())
#             if not authorities:
#                 return render(request, 'bookings/booking_failed.html', {'message': 'No authorities assigned for approval'})

#             # Base price (for up to 3 hours = 6 slots)
#             base_price = lecture_hall.ac_price if ac_required else lecture_hall.non_ac_price
#             per_slot_price = base_price / 6  # 3 hours = 6 slots

#             total_slots = len(time_slots)
#             extra_slots = max(0, total_slots - 6)  # Extra slots beyond 3 hours

#             # Extra charge: 35% per extra slot
#             extra_charge = (per_slot_price * 0.35) * extra_slots  

#             # Projector charge: Only for L18, L19, L20 at ₹1000 per slot
#             projector_charge = 0
#             if projector_required and lecture_hall.name in ["L18", "L19", "L20"]:
#                 projector_charge = 1000 * total_slots  # ₹1000 per slot

#             # Final price calculation
#             total_price = base_price + extra_charge + projector_charge
#             print("----------------------------------------------------")
#             print(total_price)
#             print("----------------------------------------------------")
#             bookings = []
#             for time_slot in time_slots:
#                 booking = Booking.objects.create(
#                     user=request.user,
#                     lecture_hall=lecture_hall,
#                     date=date,
#                     time_slot=time_slot,
#                     status="Pending",
#                     approval_token=str(uuid.uuid4()),  
#                     approvals_pending={auth.email: False for auth in authorities},
#                     ac_required=ac_required,
#                     projector_required=projector_required,
#                     purpose=purpose,
#                     price=total_price
#                 )
#                 bookings.append(booking)

#             first_authority_email = next(iter(bookings[0].approvals_pending.keys()), None)
#             if first_authority_email:
#                 send_approval_email(first_authority_email, bookings)

#             return redirect('bookings:booking_success')

#     else:
#         form = BookingForm()

#     return render(request, 'bookings/booking_form.html', {'form': form})

# @login_required
# def get_available_slots(request):
#     """Returns available slots for a selected hall and date."""
#     hall_id = request.GET.get("lecture_hall")
#     date_str = request.GET.get("date")

#     if not hall_id or not date_str:
#         return JsonResponse([], safe=False)

#     try:
#         date = datetime.strptime(date_str, "%Y-%m-%d").date()
#     except ValueError:
#         return JsonResponse([], safe=False)

#     occupied_slots = set(
#         FixedLecture.objects.filter(hall_id=hall_id, day=date.strftime('%A')).values_list("time_slot", flat=True)
#     ) | set(
#         Booking.objects.filter(lecture_hall_id=hall_id, date=date)
#         .exclude(status="Rejected")
#         .values_list("time_slot", flat=True)
#     )

#     available_slots = TimeSlot.objects.exclude(id__in=occupied_slots).values("id", "start_time", "end_time")

#     return JsonResponse(list(available_slots), safe=False)




# def approve_booking(request):
#     """Approves all bookings from the provided tokens."""
#     tokens = request.GET.get("tokens")
#     if not tokens:
#         return HttpResponse("Invalid or expired approval link.", status=400)

#     tokens_list = tokens.split(",")
#     bookings = Booking.objects.filter(approval_token__in=tokens_list)

#     if not bookings.exists():
#         return HttpResponse("Invalid or expired approval link.", status=400)

#     authority_email = next(
#         (email for email, approved in bookings[0].approvals_pending.items() if not approved), 
#         None
#     )

#     if not authority_email:
#         return HttpResponse("This booking is already fully approved.", status=400)

#     for booking in bookings:
#         booking.approvals_pending[authority_email] = True
#         if all(booking.approvals_pending.values()):  # If all approvals are done
#             booking.status = "Approved"
#         booking.save()

#     next_approver_email = next(
#         (email for email, approved in bookings[0].approvals_pending.items() if not approved), 
#         None
#     )

#     if next_approver_email:
#         send_approval_email(next_approver_email, bookings)
#     else:
#         send_mail(
#             subject="Booking Approved ✅",
#             message=f"Your booking for {bookings[0].lecture_hall.name} on {bookings[0].date} "
#                     f"({', '.join([b.time_slot.start_time.strftime('%H:%M') for b in bookings])}) has been fully approved!",
#             from_email="noreply@lhcportal.com",
#             recipient_list=[bookings[0].user.email],
#         )

#     return HttpResponse("Booking approved successfully!", status=200)


# def reject_booking(request):
#     """Rejects all bookings from the provided tokens."""
#     tokens = request.GET.get("tokens")
#     if not tokens:
#         return HttpResponse("Invalid or expired rejection link.", status=400)

#     tokens_list = tokens.split(",")
#     bookings = Booking.objects.filter(approval_token__in=tokens_list)

#     if not bookings.exists():
#         return HttpResponse("Invalid or expired rejection link.", status=400)

#     for booking in bookings:
#         booking.status = "Rejected"
#         booking.approvals_pending = {}  
#         booking.save()

#     send_mail(
#         subject="Booking Rejected ❌",
#         message=f"Your booking for {bookings[0].lecture_hall.name} on {bookings[0].date} "
#                 f"({', '.join([b.time_slot.start_time.strftime('%H:%M') for b in bookings])}) has been rejected.",
#         from_email="noreply@lhcportal.com",
#         recipient_list=[bookings[0].user.email],
#     )

#     return HttpResponse("Booking rejected successfully!", status=200)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from timetable.models import FixedLecture, TimeSlot, LectureHall
from .models import Booking
from .forms import BookingForm
from datetime import datetime
import uuid
from decimal import Decimal

def get_pricing(request):
    lecture_hall_id = request.GET.get("lecture_hall")
    if not lecture_hall_id:
        return JsonResponse({"error": "Missing lecture hall ID"}, status=400)

    try:
        hall = LectureHall.objects.get(id=lecture_hall_id)
        return JsonResponse({
            "capacity": hall.capacity,
            "ac_price": float(hall.ac_price),  # Convert Decimal to float for JSON
            "non_ac_price": float(hall.non_ac_price),
            "projector_price": float(hall.projector_price),
            "extra_charge": round(float(hall.ac_price) * 0.35, 2)  # Fix Decimal multiplication
             # Assuming the field name is 'capacity
        })
    except LectureHall.DoesNotExist:
        return JsonResponse({"error": "Lecture hall not found"}, status=404)


def send_approval_email(authority_email, booking):
    """Send a single email containing all approval tokens for a booking."""
    approval_link = f"http://127.0.0.1:8000/bookings/approve/?token={booking.approval_token}"
    rejection_link = f"http://127.0.0.1:8000/bookings/reject/?token={booking.approval_token}"

    time_slots = ", ".join(f"{ts.start_time} - {ts.end_time}" for ts in booking.time_slots.all())

    send_mail(
        subject="LHC Booking Approval Required",
        message=(
            f"A new booking request needs your approval.\n\n"
            f"Lecture Hall: {booking.lecture_hall.name}\n"
            f"Date: {booking.date}\n"
            f"Time Slots: {time_slots}\n"
            f"Requested by: {booking.user.username}\n\n"
            f"AC Required: {'Yes' if booking.ac_required else 'No'}\n"
            f"Projector Required: {'Yes' if booking.projector_required else 'No'}\n"
            f"Purpose: {booking.purpose}\n\n"
            f"Estimated Price: {booking.price} INR\n\n"
            f"✅ Approve: {approval_link}\n"
            f"❌ Reject: {rejection_link}"
        ),
        from_email="noreply@lhcportal.com",
        recipient_list=[authority_email],
    )


@login_required
def booking_form(request):
    """Handles multiple-slot booking, price calculation, and conflict validation."""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            lecture_hall = form.cleaned_data["lecture_hall"]
            date = form.cleaned_data["date"]
            time_slots = form.cleaned_data["time_slots"]
            ac_required = form.cleaned_data["ac_required"]
            projector_required = form.cleaned_data["projector_required"]
            purpose = form.cleaned_data["purpose"]

            # Check if any selected slot is already booked
            existing_bookings = Booking.objects.filter(
                lecture_hall=lecture_hall,
                date=date,
                time_slots__in=time_slots  # ✅ Use 'in' for ManyToManyField
            ).exclude(status="Rejected").distinct()


            if existing_bookings.exists():
                return render(request, 'bookings/booking_failed.html', {
                    'message': 'One or more selected slots are already booked or pending.'
                })

            authorities = list(request.user.authorities.all())
            if not authorities:
                return render(request, 'bookings/booking_failed.html', {'message': 'No authorities assigned for approval'})

            # Base price (for up to 3 hours = 6 slots)
            base_price = lecture_hall.ac_price if ac_required else lecture_hall.non_ac_price
            per_slot_price = base_price / 6  # 3 hours = 6 slots

            total_slots = len(time_slots)
            extra_slots = max(0, total_slots - 6)  # Extra slots beyond 3 hours

            # Extra charge: 35% per extra slot
            extra_charge = (per_slot_price * Decimal("0.35")) * extra_slots  

            # Projector charge: Only for L18, L19, L20 at ₹1000 per slot
            projector_charge = 0
            if projector_required and lecture_hall.name in ["L18", "L19", "L20"]:
                projector_charge = 1000 * total_slots  # ₹1000 per slot

            # Final price calculation
            total_price = base_price + extra_charge + projector_charge

            # Create a single booking instance and assign multiple time slots
            booking = Booking.objects.create(
                user=request.user,
                lecture_hall=lecture_hall,
                date=date,
                status="Pending",
                approval_token=str(uuid.uuid4()),  
                approvals_pending={auth.email: False for auth in authorities},
                ac_required=ac_required,
                projector_required=projector_required,
                purpose=purpose,
                price=total_price
            )
            booking.time_slots.set(time_slots)

            first_authority_email = next(iter(booking.approvals_pending.keys()), None)
            if first_authority_email:
                send_approval_email(first_authority_email, booking)

            return redirect('bookings:booking_success')

    else:
        form = BookingForm()

    return render(request, 'bookings/booking_form.html', {'form': form})


@login_required
def get_available_slots(request):
    """Returns available slots for a selected hall and date."""
    hall_id = request.GET.get("lecture_hall")
    date_str = request.GET.get("date")

    if not hall_id or not date_str:
        return JsonResponse([], safe=False)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse([], safe=False)

    occupied_slots = set(
        FixedLecture.objects.filter(hall_id=hall_id, day=date.strftime('%A')).values_list("time_slot", flat=True)
    ) | set(
        Booking.objects.filter(lecture_hall_id=hall_id, date=date)
        .exclude(status="Rejected")
        .values_list("time_slots", flat=True)
    )

    available_slots = TimeSlot.objects.exclude(id__in=occupied_slots).values("id", "start_time", "end_time")

    return JsonResponse(list(available_slots), safe=False)


def approve_booking(request):
    """Approves a booking from the provided token."""
    token = request.GET.get("token")
    if not token:
        return HttpResponse("Invalid or expired approval link.", status=400)

    booking = get_object_or_404(Booking, approval_token=token)

    authority_email = next(
        (email for email, approved in booking.approvals_pending.items() if not approved), 
        None
    )

    if not authority_email:
        return HttpResponse("This booking is already fully approved.", status=400)

    booking.approvals_pending[authority_email] = True
    if all(booking.approvals_pending.values()):  # If all approvals are done
        booking.status = "Approved"
    booking.save()

    next_approver_email = next(
        (email for email, approved in booking.approvals_pending.items() if not approved), 
        None
    )

    if next_approver_email:
        send_approval_email(next_approver_email, booking)
    else:
        send_mail(
            subject="Booking Approved ✅",
            message=f"Your booking for {booking.lecture_hall.name} on {booking.date} "
                    f"({', '.join([ts.start_time.strftime('%H:%M') for ts in booking.time_slots.all()])}) has been fully approved!",
            from_email="noreply@lhcportal.com",
            recipient_list=[booking.user.email],
        )

    return HttpResponse("Booking approved successfully!", status=200)


def reject_booking(request):
    """Rejects a booking from the provided token."""
    token = request.GET.get("token")
    if not token:
        return HttpResponse("Invalid or expired rejection link.", status=400)

    booking = get_object_or_404(Booking, approval_token=token)
    booking.status = "Rejected"
    booking.approvals_pending = {}  
    booking.save()

    return HttpResponse("Booking rejected successfully!", status=200)

@login_required
def pending_approvals(request):
    """Lists bookings requiring approval from the logged-in user."""
    bookings = Booking.objects.filter(status="Pending").extra(
        where=["approvals_pending ->> %s = 'false'"], params=[request.user.email]
    )
    return render(request, 'bookings/pending_approvals.html', {'bookings': bookings})

@login_required
def booking_success(request):
    """Displays the booking success page with the user's latest booking."""
    latest_booking = Booking.objects.filter(user=request.user).order_by('-id').first()
    return render(request, 'bookings/booking_success.html', {'booking': latest_booking})
