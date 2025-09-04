from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/new/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/edit/', views.booking_edit, name='booking_edit'),
    path('bookings/<int:pk>/delete/', views.booking_delete, name='booking_delete'),
    path('login/', views.login_view, name='login'),  #  new route
]
