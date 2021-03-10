from django.urls import path, re_path

from .views import Couriers

urlpatterns = [
    path('couriers', Couriers.as_view(), name='couriers_create'),
]