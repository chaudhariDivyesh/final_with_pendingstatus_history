from django.urls import path
from . import views
from .views import booking_form,approve_booking,reject_booking
from .views import get_available_slots

app_name = "bookings"  # ✅ Fix NoReverseMatch by adding namespace

urlpatterns = [
    path("new/", views.booking_form, name="new_booking"),
    #path("approve/<int:booking_id>/", views.approve_booking, name="approve_booking"),
    #path("reject/<int:booking_id>/", views.reject_booking, name="reject_booking"),
    path("pending/", views.pending_approvals, name="pending_approvals"),
    path("form/", booking_form, name="booking_form"),# Ensure this path exists
   # path("pending/", pending_approvals, name="pending_approvals"),
    path("approve/", views.approve_booking, name="approve_booking"),
    path("reject/", views.reject_booking, name="reject_booking"),
    path("get_pricing/", views.get_pricing, name="get_pricing"),
    path("success/", views.booking_success, name="booking_success"),  # ✅ Fix
    path('get_available_slots/', get_available_slots, name='get_available_slots'),
]
