from django.urls import path
from .views import timetable_home, timetable_view  # ✅ Correct (matches function names in views.py)

urlpatterns = [
    path("", timetable_home, name="timetable_home"),
    path("<int:hall_id>/", timetable_view, name="timetable_view"),  # ✅ Correct
]
