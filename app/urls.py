from django.urls import path
from . import views  # Import views from this app

urlpatterns = [
    path('', views.home, name='home'),  # Empty string '' means homepage
]

