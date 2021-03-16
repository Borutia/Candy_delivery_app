from django.urls import path

from .views import Couriers, Orders, OrdersAssign, OrdersComplete

urlpatterns = [
    path('couriers', Couriers.as_view(), name='couriers_create'),
    path('couriers/<int:courier_id>', Couriers.as_view(), name='courier_update'),
    path('orders', Orders.as_view(), name='orders_create'),
    path('orders/assign', OrdersAssign.as_view(), name='orders_assign'),
    path('orders/complete', OrdersComplete.as_view(), name='orders_complete'),
]
