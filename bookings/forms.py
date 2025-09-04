from django import forms
from .models import Booking, Room
from decimal import Decimal
from django.utils import timezone
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user_email', 'room', 'start_time', 'end_time', 'price']
        readonly_fields = ('price',)  
        
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable editing for price field
        if 'price' in self.fields:
            self.fields['price'].disabled = True

        self.fields['room'].queryset = Room.objects.all().order_by('room_number')

    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get('room')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if not room or not start_time or not end_time:
            return cleaned_data

        # Make times timezone-aware
        start_utc = timezone.make_aware(start_time, timezone.get_current_timezone()).astimezone(timezone.utc)
        end_utc = timezone.make_aware(end_time, timezone.get_current_timezone()).astimezone(timezone.utc)

        if start_utc >= end_utc:
            self.add_error('end_time', "End time must be after start time.")
            return cleaned_data
        # Prevent past bookings
        if start_utc < timezone.now():
            self.add_error('start_time', "Start time cannot be in the past.")
            return cleaned_data
        

        # Overlap check
        overlapping = Booking.objects.filter(
            room=room,
            start_time__lt=end_utc,
            end_time__gt=start_utc
        )
        if self.instance.pk:
            overlapping = overlapping.exclude(pk=self.instance.pk)

        if overlapping.exists():
            first = overlapping.first()
            # Attach error to the form fields
            msg = f"Room {room.room_number} is already booked from " \
                  f"{first.start_time.strftime('%Y-%m-%d %H:%M')} to " \
                  f"{first.end_time.strftime('%Y-%m-%d %H:%M')}."
            self.add_error('room', msg)
            self.add_error('start_time', msg)
            self.add_error('end_time', msg)
            return cleaned_data  # stop further processing

        # Calculate price
        duration_hours = (end_utc - start_utc).total_seconds() / 3600
        cleaned_data['price'] = Decimal(duration_hours) * room.room_type.price_per_hour

        # Save UTC times back
        cleaned_data['start_time'] = start_utc
        cleaned_data['end_time'] = end_utc

        return cleaned_data
