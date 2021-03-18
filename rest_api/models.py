from django.db import models
from django.contrib.postgres.fields import ArrayField

from .const import CourierType, StatusOrder, StatusCourier
from decimal import Decimal


class QuantityOrders(models.Model):
    foot = models.PositiveIntegerField('Пеший курьер', default=0)
    bike = models.PositiveIntegerField('Велокурьер', default=0)
    car = models.PositiveIntegerField('Курьер на автомобиле', default=0)


class Courier(models.Model):
    courier_id = models.PositiveIntegerField('id курьера', primary_key=True)
    courier_type = models.CharField('Тип курьера', max_length=4,
                                    choices=CourierType.choices)
    regions = ArrayField(models.PositiveIntegerField(), verbose_name='Районы')
    working_hours = ArrayField(models.CharField(max_length=11),
                               verbose_name='График работы')
    lifting_capacity = models.DecimalField(
        'Грузоподъемность курьера',
        max_digits=4, decimal_places=2, default=Decimal(0)
    )
    current_weight_orders = models.DecimalField(
        'Текущий вес назначенных заказов',
        max_digits=4, decimal_places=2, default=Decimal(0)
    )
    assign_time = models.DateTimeField('Время назначения', null=True)
    last_complete_time = models.DateTimeField('Время последней доставки',
                                              null=True)
    status_courier = models.CharField('Статус курьера',
                                      max_length=1,
                                      choices=StatusCourier.choices,
                                      default=StatusCourier.FREE)
    quantity_order = models.ForeignKey(QuantityOrders, on_delete=models.CASCADE)


class Order(models.Model):
    order_id = models.PositiveIntegerField('id заказа', primary_key=True)
    weight = models.DecimalField('Вес', max_digits=4, decimal_places=2)
    region = models.PositiveIntegerField('Район')
    delivery_hours = ArrayField(models.CharField(max_length=11),
                                verbose_name='Промежутки для доставки')
    status_order = models.CharField('Статус заказа',
                                    max_length=1,
                                    choices=StatusOrder.choices,
                                    default=StatusOrder.NEW)
    assign_time = models.DateTimeField('Время назначения', null=True)
    complete_time = models.DateTimeField('Время выполнения', null=True)
    delivery_time = models.PositiveIntegerField('Время доставки в секундах',
                                                null=True)
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, null=True)
