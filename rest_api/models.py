from decimal import Decimal

from django.db import models
from django.db.models import Avg, Min

from .const import CourierType, StatusOrder, StatusCourier, FORMAT_TIME
from .utils import calculate_rating


class QuantityOrders(models.Model):
    foot = models.PositiveIntegerField('Пеший курьер', default=0)
    bike = models.PositiveIntegerField('Велокурьер', default=0)
    car = models.PositiveIntegerField('Курьер на автомобиле', default=0)


class Courier(models.Model):
    courier_id = models.PositiveIntegerField('id курьера', primary_key=True)
    courier_type = models.CharField('Тип курьера', max_length=4,
                                    choices=CourierType.choices)
    courier_type_in_delivery = models.CharField(
        'Тип курьера на момент формирования развоза',
        max_length=4, choices=CourierType.choices, null=True
    )
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
    complete_order_in_delivery = models.PositiveIntegerField(
        'Количество доставленных заказов в текущем развозе',
        default=0
    )
    quantity_orders = models.ForeignKey(QuantityOrders,
                                        on_delete=models.CASCADE)

    @staticmethod
    def get_rating(courier_id):
        query_min_of_average = Order.objects.filter(
            courier_id=courier_id,
            status_order=StatusOrder.COMPLETE
        ).values('region').annotate(
            Avg('delivery_time')
        ).aggregate(Min('delivery_time__avg'))
        min_of_average = Decimal(
            query_min_of_average['delivery_time__avg__min']
        )
        rating = Decimal(
            (60 * 60 - min(min_of_average, 60 * 60)) / (60 * 60) * 5
        ).quantize(Decimal('1.11'))
        return rating

    @staticmethod
    def get_earnings(foot, bike, car):
        return calculate_rating(foot, 'foot') \
               + calculate_rating(bike, 'bike') \
               + calculate_rating(car, 'car')


class WorkingHours(models.Model):
    start_time = models.TimeField('Начало работы')
    stop_time = models.TimeField('Конец работы')
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE)

    def __str__(self):
        return '{}-{}'.format(
            self.start_time.strftime(FORMAT_TIME),
            self.stop_time.strftime(FORMAT_TIME)
        )

    @staticmethod
    def get_working_hours(courier_id):
        return [(hours.start_time, hours.stop_time)
                for hours in WorkingHours.objects.filter(
                courier_id=courier_id)]


class Regions(models.Model):
    region = models.PositiveIntegerField('Район')
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE)

    @staticmethod
    def get_regions(courier_id):
        return [obj.region for obj in Regions.objects.filter(
            courier_id=courier_id)]


class Order(models.Model):
    order_id = models.PositiveIntegerField('id заказа', primary_key=True)
    weight = models.DecimalField('Вес', max_digits=4, decimal_places=2)
    region = models.PositiveIntegerField('Район')
    status_order = models.CharField('Статус заказа',
                                    max_length=1,
                                    choices=StatusOrder.choices,
                                    default=StatusOrder.NEW)
    assign_time = models.DateTimeField('Время назначения', null=True)
    complete_time = models.DateTimeField('Время выполнения', null=True)
    delivery_time = models.PositiveIntegerField('Время доставки в секундах',
                                                null=True)
    courier = models.ForeignKey(Courier, on_delete=models.CASCADE, null=True)


class DeliveryHours(models.Model):
    start_time = models.TimeField('Начало для доставки')
    stop_time = models.TimeField('Конец для доставки')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    @staticmethod
    def get_delivery_hours(order_id):
        return [(hours.start_time, hours.stop_time)
                for hours in DeliveryHours.objects.filter(
                order_id=order_id)]
