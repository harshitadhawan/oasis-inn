from django.contrib import admin
from django.urls import path, include  # include is needed
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('admin/')),  #  Root URL redirects straight to admin
    path('bookings/', include('bookings.urls')),
]