from django.urls import path, re_path

from .views import Couriers

urlpatterns = [
    path('couriers', Couriers.as_view(), name='couriers_create'),
    path('couriers/<int:courier_id>', Couriers.as_view(), name='courier_update'),
]