from rest_framework import serializers
from datetime import datetime

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
        couriers_id = []
        for courier in validated_data['data']:
            Courier.objects.create(**courier)
            couriers_id.append({'id': courier['courier_id']})
        return couriers_id


class CourierGetUpdateSerializer(BaseCourierSerializer):
    class Meta:
        model = Courier
        fields = ('courier_id', 'courier_type', 'regions', 'working_hours',)
        read_only_fields = ('courier_id',)

    def validate(self, data):
        if 'courier_id' in data:
            raise serializers.ValidationError()
        return data
