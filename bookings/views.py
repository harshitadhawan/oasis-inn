from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Booking
from .forms import BookingForm


def home(request):
    bookings = Booking.objects.all().order_by('start_time')
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})

def booking_list(request):
    bookings = Booking.objects.all().order_by('start_time')
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})

def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm()
    return render(request, 'bookings/booking_form.html', {'form': form})


def booking_edit(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'bookings/booking_form.html', {'form': form, 'booking': booking})


def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    refund = booking.refund_amount()
    if request.method == 'POST':
        booking.delete()
        return redirect('booking_list')
    return render(request, 'bookings/booking_confirm_delete.html', {'booking': booking, 'refund': refund})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # redirect to your home page
        else:
            error = "Invalid username or password"
            return render(request, "login.html", {"error": error})
    return render(request, "login.html")

