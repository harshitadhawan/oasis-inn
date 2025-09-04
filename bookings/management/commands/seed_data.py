
from django.core.management.base import BaseCommand
from bookings.models import RoomType, Room, Booking
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = "Seed database with sample rooms and bookings"

    def handle(self, *args, **kwargs):
        RoomType.objects.all().delete()
        Room.objects.all().delete()
        Booking.objects.all().delete()

        a = RoomType.objects.create(name="Type A", price_per_hour=100)
        b = RoomType.objects.create(name="Type B", price_per_hour=80)
        c = RoomType.objects.create(name="Type C", price_per_hour=50)

        rooms = [
            Room.objects.create(number="A1", room_type=a),
            Room.objects.create(number="A2", room_type=a),
            Room.objects.create(number="B1", room_type=b),
            Room.objects.create(number="B2", room_type=b),
            Room.objects.create(number="B3", room_type=b),
            Room.objects.create(number="C1", room_type=c),
            Room.objects.create(number="C2", room_type=c),
            Room.objects.create(number="C3", room_type=c),
            Room.objects.create(number="C4", room_type=c),
            Room.objects.create(number="C5", room_type=c),
        ]

        def make_booking(email, room, start, hours):
            end = start + timedelta(hours=hours)
            return Booking.objects.create(
                user_email=email,
                room=room,
                start_time=start,
                end_time=end
            )

        base_dates = [
            datetime(2024, 6, 15, 10, 0),
            datetime(2024, 7, 10, 12, 0),
            datetime(2024, 8, 5, 14, 0),
            datetime(2024, 8, 20, 9, 0),
        ]

        for i, base in enumerate(base_dates):
            for r in rooms[:5]:
                make_booking(f"user{i}@example.com", r, base, (i+1) * 2)

        self.stdout.write(self.style.SUCCESS("Seed data created!"))
