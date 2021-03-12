from datetime import datetime
from decimal import Decimal
from rest_framework import serializers

from .models import Courier, Order
from .const import CourierType, FORMAT_TIME


class BaseCourierSerializer(serializers.ModelSerializer):
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
        for date in data:
            start_work, stop_work = date.split('-')
            try:
                datetime.strptime(start_work, FORMAT_TIME)
                datetime.strptime(stop_work, FORMAT_TIME)
            except ValueError:
                raise serializers.ValidationError('Invalid format time in working hours')
        return data


class CourierCreateSerializer(serializers.ModelSerializer):
    data = BaseCourierSerializer(many=True)

    class Meta:
        model = Courier
        fields = ('data',)

    def create(self, validated_data):
        return [{'id': courier['courier_id']} for courier in validated_data['data']
                if Courier.objects.create(**courier)]


class CourierGetUpdateSerializer(BaseCourierSerializer):
    class Meta:
        model = Courier
        fields = ('courier_id', 'courier_type', 'regions', 'working_hours',)
        read_only_fields = ('courier_id',)

    def validate_courier_id(self, data):
        if data:
            raise serializers.ValidationError()
        return data


class BaseOrderSerializer(serializers.ModelSerializer):
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
        for date in data:
            start_delivery, stop_delivery = date.split('-')
            try:
                datetime.strptime(start_delivery, FORMAT_TIME)
                datetime.strptime(stop_delivery, FORMAT_TIME)
            except ValueError:
                raise serializers.ValidationError('Invalid format time in delivery hours')
        return data


class OrderCreateSerializer(serializers.ModelSerializer):
    data = BaseOrderSerializer(many=True)

    class Meta:
        model = Order
        fields = ('data',)

    def create(self, validated_data):
        return [{'id': order['order_id']} for order in validated_data['data']
                if Order.objects.create(**order)]