from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

class RoomType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} - ₹{self.price_per_hour}/hr"


class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type.name})"


class Booking(models.Model):
    user_email = models.EmailField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True)

    def clean(self):
        start = self.start_time
        end = self.end_time
        if timezone.is_naive(start):
            start = timezone.make_aware(start, timezone.get_current_timezone())
        if timezone.is_naive(end):
            end = timezone.make_aware(end, timezone.get_current_timezone())

        if start >= end:
            raise ValidationError("End time must be after start time.")
        if start < timezone.now():
            raise ValidationError("Start time cannot be in the past.")
        

        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            room=self.room,
            start_time__lt=end,
            end_time__gt=start
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)
        if overlapping.exists():
            first = overlapping.first()
            raise ValidationError(
                f"Room {self.room.room_number} is already booked from "
                f"{first.start_time.strftime('%Y-%m-%d %H:%M')} to "
                f"{first.end_time.strftime('%Y-%m-%d %H:%M')}."
            )

    def save(self, *args, **kwargs):
        try:
            self.full_clean()  # Validate before saving
        except ValidationError as e:
            # Let Django forms handle the ValidationError gracefully
            if kwargs.get('force_insert') or kwargs.get('force_update'):
                raise
            else:
                raise ValidationError(e)

        # Calculate price
        duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
        self.price = Decimal(duration_hours) * self.room.room_type.price_per_hour
        super().save(*args, **kwargs)

    def refund_amount(self):
        hours_left = (self.start_time - timezone.now()).total_seconds() / 3600
        if hours_left > 48:
            return self.price
        elif 24 <= hours_left <= 48:
            return self.price * Decimal('0.5')
        else:
            return Decimal('0.0')

    def __str__(self):
        return f"{self.user_email} - {self.room} ({self.start_time} to {self.end_time})"
