from django.db import models
from django.contrib.postgres.fields import ArrayField

from .const import CourierType


class Courier(models.Model):
    courier_id = models.PositiveIntegerField(primary_key=True)
    courier_type = models.CharField(max_length=4, choices=CourierType.choices)
    regions = ArrayField(models.PositiveIntegerField())
    working_hours = ArrayField(models.CharField(max_length=11))


class Order(models.Model):
    order_id = models.PositiveIntegerField(primary_key=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2)
    region = models.PositiveIntegerField()
    delivery_hours = ArrayField(models.CharField(max_length=11))
