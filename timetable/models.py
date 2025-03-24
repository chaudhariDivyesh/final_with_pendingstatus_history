from django.db import models

class LectureHall(models.Model):
    name = models.CharField(max_length=50, unique=True)
    capacity = models.PositiveIntegerField()
    ac_price = models.DecimalField(max_digits=10, decimal_places=2)  # Fixed for 3 hours
    projector_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Only for LHC 18, 19, 20

    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    """Represents a time slot (e.g., 08:00 - 08:30)"""
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"
    
class FixedLecture(models.Model):
    hall = models.ForeignKey(LectureHall, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)
    subject = models.CharField(max_length=100)

    
class WeeklySchedule(models.Model):
    """Fixed weekly lecture schedule (loaded from Excel)"""
    lecture_hall = models.ForeignKey(LectureHall, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)  # Monday, Tuesday, etc.
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, null=True, blank=True)  # Optional

    def __str__(self):
        return f"{self.lecture_hall} - {self.day} - {self.time_slot}"
