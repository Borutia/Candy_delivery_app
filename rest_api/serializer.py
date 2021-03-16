from decimal import Decimal
from rest_framework import serializers
from django.utils import timezone

from .models import Courier, Order
from .const import CourierType, LIFTING_CAPACITY, StatusCourier, StatusOrder
from .utils import parse_time, check_cross_of_time


class BaseCourierSerializer(serializers.ModelSerializer):
    """Serializer for couriers"""
    courier_id = serializers.IntegerField(min_value=1)
    courier_type = serializers.ChoiceField(choices=CourierType.choices)
    regions = serializers.ListField(child=serializers.IntegerField(min_value=1))
    working_hours = serializers.ListField(child=serializers.CharField(max_length=11))

    class Meta:
        model = Courier
        fields = ('courier_id', 'courier_type', 'regions', 'working_hours',)

    def validate_courier_id(self, data):
        if Courier.objects.filter(courier_id=data).first():
            raise serializers.ValidationError('Courier id already exist')
        return data

    def validate_regions(self, data):
        if not data:
            raise serializers.ValidationError('Regions is empty')
        return data

    def validate_working_hours(self, data):
        if not data:
            raise serializers.ValidationError('Working hours is empty')
        for time in data:
            try:
                parse_time(time)
            except Exception:
                raise serializers.ValidationError('Invalid format time in working hours')
        return data


class CourierCreateSerializer(serializers.ModelSerializer):
    """Serializer for create couriers"""
    data = BaseCourierSerializer(many=True)

    class Meta:
        model = Courier
        fields = ('data',)

    def create(self, validated_data):
        couriers_id = []
        for courier in validated_data['data']:
            courier['lifting_capacity'] = LIFTING_CAPACITY[courier['courier_type']]
            Courier.objects.create(**courier)
            couriers_id.append({'id': courier['courier_id']})
        return couriers_id


class CourierGetUpdateSerializer(BaseCourierSerializer):
    """Serializer for get/update couriers"""
    class Meta:
        model = Courier
        fields = ('courier_id', 'courier_type', 'regions', 'working_hours',)
        read_only_fields = ('courier_id',)

    def validate_courier_id(self, data):
        if data:
            raise serializers.ValidationError('Wrong field')
        return data

    def validate(self, data):
        if not data:
            raise serializers.ValidationError('Data is empty')
        if data.get('courier_type'):
            data['lifting_capacity'] = LIFTING_CAPACITY[data['courier_type']]
        return data


class BaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""
    order_id = serializers.IntegerField(min_value=1)
    weight = serializers.DecimalField(max_digits=4, decimal_places=2,
                                      min_value=Decimal('0.01'), max_value=Decimal('50'))
    region = serializers.IntegerField(min_value=1)
    delivery_hours = serializers.ListField(child=serializers.CharField(max_length=11))

    class Meta:
        model = Order
        fields = ('order_id', 'weight', 'region', 'delivery_hours',)

    def validate_order_id(self, data):
        if Order.objects.filter(order_id=data).first():
            raise serializers.ValidationError('Order id already exist')
        return data

    def validate_delivery_hours(self, data):
        if not data:
            raise serializers.ValidationError('Delivery hours is empty')
        for time in data:
            try:
                parse_time(time)
            except Exception:
                raise serializers.ValidationError('Invalid format time in delivery hours')
        return data


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for create orders"""
    data = BaseOrderSerializer(many=True)

    class Meta:
        model = Order
        fields = ('data',)

    def create(self, validated_data):
        return [{'id': order['order_id']} for order in validated_data['data']
                if Order.objects.create(**order)]


class OrdersAssignSerializer(serializers.ModelSerializer):
    """Serializer for assign orders"""
    courier_id = serializers.IntegerField(min_value=1)

    class Meta:
        model = Courier
        fields = ('courier_id',)
        read_only_fields = ('courier_id',)

    def validate(self, validated_data):
        response = {}
        if self.instance.status_courier == StatusCourier.FREE:
            new_orders = Order.objects.filter(status_order=StatusOrder.NEW, region__in=self.instance.regions,
                                              weight__lte=self.instance.lifting_capacity).order_by('weight')
            if new_orders:
                orders_id = []
                assign_time = timezone.now()
                current_weight = 0
                for order in new_orders:
                    if current_weight + order.weight > self.instance.lifting_capacity:
                        break
                    if check_cross_of_time(self.instance.working_hours, order.delivery_hours):
                        order.assign_time = assign_time
                        order.status_order = StatusOrder.IN_PROCESS
                        order.courier_id = self.instance
                        orders_id.append(order.order_id)
                        order.save()
                        current_weight += order.weight
                if orders_id:
                    self.instance.last_complete_time = assign_time
                    self.instance.assign_time = assign_time
                    self.instance.orders_id = orders_id
                    self.instance.status_courier = StatusCourier.BUSY
                    response['assign_time'] = assign_time
                response['orders'] = [{'id': order_id} for order_id in orders_id]
            else:
                response['orders'] = []
                return response
        else:
            response['orders'] = [{'id': order_id} for order_id in self.instance.orders_id]
            response['assign_time'] = self.instance.assign_time
        return response


class OrdersCompleteSerializer(serializers.ModelSerializer):
    """Serializer for orders complete"""
    order_id = serializers.IntegerField(min_value=1)
    courier_id = serializers.IntegerField(min_value=1)
    complete_time = serializers.DateTimeField()

    class Meta:
        model = Order
        fields = ('order_id', 'complete_time', 'courier_id',)

    def validate(self, validated_data):
        return validated_data
