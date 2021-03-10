from rest_framework import serializers
from datetime import datetime

from .models import Courier, Order
from .const import CourierType


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
        elif len(data) > 3:
            raise serializers.ValidationError('The work schedule can only be divided into 3 intervals')
        #проверку даты добавить
        return data


class CourierCreateSerializer(serializers.ModelSerializer):
    data = BaseCourierSerializer(many=True)

    class Meta:
        model = Courier
        fields = ('data',)

    # def validate(self, data):
    #     from collections import Counter
    #     count = Counter([courier['courier_id'] for courier in data['data']])
    #     if count.most_common(1)[0][1] > 1:
    #         raise serializers.ValidationError('Duplicate courier id')
    #     return data

    def create(self, validated_data):
        couriers_id = []
        for courier in validated_data['data']:
            Courier.objects.create(**courier)
            couriers_id.append({'id': courier['courier_id']})
        return couriers_id
