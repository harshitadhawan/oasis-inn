from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from django.utils.timezone import now
from django.shortcuts import render

from .models import RoomType, Room, Booking
import io
import base64
import matplotlib.pyplot as plt

# ========== MODELS REGISTRATION ==========
@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "price_per_hour")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "room_type")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    readonly_fields = ("price",)
    list_display = ("user_email", "room", "start_time", "end_time", "price")


# Remove Groups from admin
admin.site.unregister(Group)

# Customize User admin
class SimpleUserAdmin(BaseUserAdmin):
    fieldsets = ((None, {"fields": ("username", "email", "password")}),)
    list_display = ("username", "email", "is_active")


admin.site.unregister(User)
admin.site.register(User, SimpleUserAdmin)

# Admin branding
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to Oasis Inn Dashboard"


# ========== REPORTS VIEW ==========
def reports_view(request):
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    # Gather stats per room type
    room_stats = []
    pie_labels = []
    pie_sizes = []

    for rt in RoomType.objects.all():
        rooms = Room.objects.filter(room_type=rt)
        bookings = Booking.objects.filter(room__in=rooms)

        # Apply date filter
        if from_date:
            bookings = bookings.filter(start_time__date__gte=from_date)
        if to_date:
            bookings = bookings.filter(start_time__date__lte=to_date)

        total_booked = bookings.count()
        total_hours = sum((b.end_time - b.start_time).total_seconds() / 3600 for b in bookings)
        money = sum(b.price for b in bookings)

        room_stats.append({
            "type": rt.name,
            "num_rooms": total_booked,
            "total_hours": round(total_hours, 2),
            "earning": money
        })

        pie_labels.append(rt.name)
        pie_sizes.append(total_booked)

    # Generate pie chart
    fig, ax = plt.subplots(figsize=(6,6))
    colors = ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99']
    explode = [0.05]*len(pie_sizes)
    if total_booked>0:
        ax.pie(pie_sizes, labels=pie_labels, autopct="%1.1f%%", startangle=90,
               colors=colors[:len(pie_sizes)], explode=explode, shadow=True, wedgeprops={'edgecolor':'white'})
    ax.axis("equal")
    ax.set_title("Rooms Booked per Type", fontsize=14, fontweight='bold')

    buf = io.BytesIO()
    plt.savefig(buf, format="png", transparent=True)
    plt.close(fig)
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    context = dict(
        admin.site.each_context(request),
        room_stats=room_stats,
        chart_base64=chart_base64,
        from_date=from_date,
        to_date=to_date
    )

    return render(request, "admin/reports.html", context)

#  extend admin.site.get_urls safely
original_get_urls = admin.site.get_urls

def get_urls():
    urls = original_get_urls()
    custom_urls = [
        path("reports/", reports_view, name="reports"),
    ]
    return custom_urls + urls

admin.site.get_urls = get_urls