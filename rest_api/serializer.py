from decimal import Decimal

from rest_framework import serializers
from django.utils import timezone

from .models import WorkingHours, QuantityOrders, Courier, Order, \
    DeliveryHours, Regions
from .const import CourierType, LIFTING_CAPACITY, StatusCourier, StatusOrder
from .utils import parse_time, is_intersections, get_correct_hours, \
    get_regions


class WorkingHoursSerializer(serializers.ModelSerializer):
    """Serializer for working hours"""
    class Meta:
        model = WorkingHours
        fields = ('start_time', 'stop_time',)


class RegionsSerializer(serializers.ModelSerializer):
    """Serializer for regions"""
    class Meta:
        model = Regions
        fields = ('region',)


class BaseCourierSerializer(serializers.ModelSerializer):
    """Serializer for couriers"""
    courier_id = serializers.IntegerField(min_value=1)
    courier_type = serializers.ChoiceField(choices=CourierType.choices)
    regions = RegionsSerializer(many=True)
    working_hours = WorkingHoursSerializer(many=True)

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
            working_hours = courier.pop('working_hours')
            regions = courier.pop('regions')
            quantity_orders = QuantityOrders.objects.create()
            courier['lifting_capacity'] = LIFTING_CAPACITY[
                courier['courier_type']
            ]
            courier['quantity_orders'] = quantity_orders
            instance = Courier.objects.create(**courier)
            for hours in working_hours:
                instance.workinghours_set.create(**hours)
            for region in regions:
                instance.regions_set.create(**region)
            couriers_id.append({'id': courier['courier_id']})
        return couriers_id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for current_courier in self.initial_data['data']:
            if current_courier.get('working_hours'):
                current_courier['working_hours'] = get_correct_hours(
                    current_courier['working_hours']
                )
            if current_courier.get('regions'):
                current_courier['regions'] = get_regions(
                    current_courier['regions']
                )


class CourierUpdateSerializer(BaseCourierSerializer):
    """Serializer for update couriers"""
    class Meta:
        model = Courier
        fields = ('courier_id', 'courier_type', 'regions', 'working_hours',)
        read_only_fields = ('courier_id',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'working_hours' in self.initial_data:
            self.initial_data['working_hours'] = get_correct_hours(
                self.initial_data['working_hours']
            )
        if 'regions' in self.initial_data:
            self.initial_data['regions'] = get_regions(
                self.initial_data['regions']
            )

    def validate_courier_id(self, data):
        if data:
            raise serializers.ValidationError('Wrong field courier_id')
        return data

    def to_representation(self, instance):
        data = {
            'courier_id': self.instance.courier_id,
            'courier_type': self.instance.courier_type,
            'regions': Regions.get_regions(self.instance.courier_id),
            'working_hours': [
                str(hours) for hours in WorkingHours.objects.filter(
                    courier_id=self.instance.courier_id)
            ]
        }
        return data

    def update(self, instance, validated_data):
        if self.initial_data.get('courier_type'):
            self.instance.lifting_capacity = LIFTING_CAPACITY[
                validated_data['courier_type']
            ]
            self.instance.courier_type = validated_data['courier_type']
            if self.instance.status_courier == StatusCourier.BUSY:
                if self.instance.current_weight_orders > \
                        self.instance.lifting_capacity:
                    for order in Order.objects.filter(
                        courier_id=self.instance.courier_id,
                        status_order=StatusOrder.IN_PROCESS,
                    ).order_by('-weight'):
                        order.status_order = StatusOrder.NEW
                        order.courier = None
                        order.assign_time = None
                        self.instance.current_weight_orders -= order.weight
                        if self.instance.current_weight_orders <= \
                                self.instance.lifting_capacity:
                            order.save()
                            break
                        order.save()
        if self.initial_data.get('working_hours'):
            WorkingHours.objects.filter(
                courier_id=self.instance.courier_id
            ).delete()
            for time in self.initial_data['working_hours']:
                self.instance.workinghours_set.create(**time)
            if self.instance.status_courier == StatusCourier.BUSY:
                for order in Order.objects.filter(
                    courier_id=self.instance.courier_id,
                    status_order=StatusOrder.IN_PROCESS
                ):
                    working_hours = WorkingHours.get_working_hours(
                        self.instance.courier_id
                    )
                    delivery_hours = DeliveryHours.get_delivery_hours(
                        order.order_id
                    )
                    if not is_intersections(working_hours, delivery_hours):
                        order.status_order = StatusOrder.NEW
                        order.courier = None
                        order.assign_time = None
                        self.instance.current_weight_orders -= order.weight
                        order.save()
        if self.initial_data.get('regions'):
            Regions.objects.filter(
                courier_id=self.instance.courier_id
            ).delete()
            for region in self.initial_data['regions']:
                self.instance.regions_set.create(**region)
            if self.instance.status_courier == StatusCourier.BUSY:
                regions = Regions.get_regions(self.instance.courier_id)
                for order in Order.objects.exclude(
                    region__in=regions
                ).filter(
                    courier_id=self.instance.courier_id,
                    status_order=StatusOrder.IN_PROCESS,
                ):
                    order.status_order = StatusOrder.NEW
                    order.courier = None
                    order.assign_time = None
                    self.instance.current_weight_orders -= order.weight
                    order.save()
        if self.instance.status_courier == StatusCourier.BUSY:
            if not Order.objects.filter(
                    courier_id=self.instance.courier_id,
                    status_order=StatusOrder.IN_PROCESS
            ).first():
                self.instance.status_courier = StatusCourier.FREE
                self.instance.assign_time = None
                self.instance.last_complete_time = None
                if self.instance.complete_order_in_delivery != 0:
                    self.instance.complete_order_in_delivery = 0
                    self.instance.current_weight_orders = Decimal(0)
                    if self.instance.courier_type_in_delivery \
                            == CourierType.FOOT:
                        self.instance.quantity_orders.foot += 1
                    elif self.instance.courier_type_in_delivery \
                            == CourierType.BIKE:
                        self.instance.quantity_orders.bike += 1
                    else:
                        self.instance.quantity_orders.car += 1
                    self.instance.quantity_orders.save()
                    self.instance.courier_type_in_delivery = None
        self.instance.save()
        return self.instance


class DeliveryHoursSerializer(serializers.ModelSerializer):
    """Serializer for delivery hours"""
    class Meta:
        model = DeliveryHours
        fields = ('start_time', 'stop_time',)


class BaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""
    order_id = serializers.IntegerField(min_value=1)
    weight = serializers.DecimalField(max_digits=4,
                                      decimal_places=2,
                                      min_value=Decimal('0.01'),
                                      max_value=Decimal('50'))
    region = serializers.IntegerField(min_value=1)
    delivery_hours = DeliveryHoursSerializer(many=True)

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
        return data


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for create orders"""
    data = BaseOrderSerializer(many=True)

    class Meta:
        model = Order
        fields = ('data',)

    def create(self, validated_data):
        orders_id = []
        for order in validated_data['data']:
            delivery_hours = order.pop('delivery_hours')
            instance = Order.objects.create(**order)
            for hours in delivery_hours:
                instance.deliveryhours_set.create(**hours)
            orders_id.append(
                {
                    'id': order['order_id']
                }
            )
        return orders_id

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for current_order in self.initial_data['data']:
            time = []
            for current_time in current_order['delivery_hours']:
                start, stop = parse_time(current_time)
                time.append({
                    'start_time': start,
                    'stop_time': stop
                })
            current_order['delivery_hours'] = time


class OrdersAssignSerializer(serializers.ModelSerializer):
    """Serializer for assign orders"""
    courier_id = serializers.IntegerField(min_value=1)

    class Meta:
        model = Courier
        fields = ('courier_id',)
        read_only_fields = ('courier_id',)

    def validate(self, validated_data):
        response = {}
        if self.instance.status_courier == StatusCourier.BUSY:
            response['orders'] = [
                {
                    'id': order.order_id
                } for order in Order.objects.filter(
                    courier_id=self.instance.courier_id,
                    status_order=StatusOrder.IN_PROCESS
                )
            ]
            response['assign_time'] = self.instance.assign_time
            return response
        regions = Regions.get_regions(self.instance.courier_id)
        new_orders = Order.objects.filter(
            status_order=StatusOrder.NEW,
            region__in=regions,
            weight__lte=self.instance.lifting_capacity
        ).order_by('weight')
        if new_orders:
            orders_id = []
            assign_time = timezone.now()
            current_weight = Decimal(0)
            working_hours = WorkingHours.get_working_hours(
                self.instance.courier_id
            )
            for order in new_orders:
                if current_weight + order.weight > \
                        self.instance.lifting_capacity:
                    break
                delivery_hours = DeliveryHours.get_delivery_hours(
                    order.order_id
                )
                if is_intersections(working_hours, delivery_hours):
                    order.assign_time = assign_time
                    order.status_order = StatusOrder.IN_PROCESS
                    order.courier_id = self.instance
                    orders_id.append(order.order_id)
                    order.save()
                    current_weight += order.weight
            if orders_id:
                self.instance.last_complete_time = assign_time
                self.instance.assign_time = assign_time
                self.instance.current_weight_orders = current_weight
                self.instance.status_courier = StatusCourier.BUSY
                self.instance.courier_type_in_delivery = \
                    self.instance.courier_type
                response['assign_time'] = assign_time
                response['orders'] = [
                    {
                        'id': order_id
                    } for order_id in orders_id
                ]
            else:
                response['orders'] = []
        else:
            response['orders'] = []
        return response


class OrdersCompleteSerializer(serializers.ModelSerializer):
    """Serializer for orders complete"""
    order_id = serializers.IntegerField(min_value=1)
    courier_id = serializers.IntegerField(min_value=1)
    complete_time = serializers.DateTimeField()

    class Meta:
        model = Order
        fields = ('order_id', 'complete_time', 'courier_id',)

    def validate_courier_id(self, data):
        if not self.instance.courier:
            raise serializers.ValidationError('Order is not assigned')
        elif self.instance.courier_id != data:
            raise serializers.ValidationError(
                'Order is assigned to a different courier'
            )
        return data

    def validate_complete_time(self, data):
        if self.instance.assign_time:
            if data < self.instance.assign_time:
                raise serializers.ValidationError(
                    'Complete time is less than assign time'
                )
        return data

    def validate(self, validated_data):
        if self.instance.status_order == StatusOrder.IN_PROCESS:
            self.instance.status_order = StatusOrder.COMPLETE
            self.instance.complete_time = validated_data['complete_time']
            self.instance.delivery_time = (
                    validated_data['complete_time']
                    - self.instance.courier.last_complete_time
            ).seconds
            self.instance.courier.last_complete_time = \
                validated_data['complete_time']
            self.instance.courier.complete_order_in_delivery += 1
            self.instance.courier.current_weight_orders -= self.instance.weight
            if not Order.objects.exclude(
                    order_id=validated_data['order_id']
            ).filter(
                courier_id=validated_data['courier_id'],
                status_order=StatusOrder.IN_PROCESS
            ).first():
                self.instance.courier.status_courier = StatusCourier.FREE
                self.instance.courier.current_weight_orders = Decimal(0)
                self.instance.courier.complete_order_in_delivery = 0
                self.instance.courier.last_complete_time = None
                self.instance.courier.assign_time = None
                if self.instance.courier.courier_type_in_delivery \
                        == CourierType.FOOT:
                    self.instance.courier.quantity_orders.foot += 1
                elif self.instance.courier.courier_type_in_delivery \
                        == CourierType.BIKE:
                    self.instance.courier.quantity_orders.bike += 1
                else:
                    self.instance.courier.quantity_orders.car += 1
                self.instance.courier.quantity_orders.save()
                self.instance.courier_type_in_delivery = None
            self.instance.courier.save()
        return validated_data


class CouriersGetSerializer(serializers.ModelSerializer):
    """Serializer for get information about courier"""
    data = serializers.SerializerMethodField()
    working_hours = serializers.SerializerMethodField()
    regions = serializers.SerializerMethodField()

    class Meta:
        model = Courier
        fields = ('data', 'courier_id', 'courier_type',
                  'regions', 'working_hours',)

    def get_data(self, instance):
        statistics = {}
        if instance.quantity_orders.foot != 0 \
                or instance.quantity_orders.bike != 0 \
                or instance.quantity_orders.car != 0:
            statistics['rating'] = Courier.get_rating(self.instance.courier_id)
            statistics['earnings'] = Courier.get_earnings(
                self.instance.quantity_orders.foot,
                self.instance.quantity_orders.bike,
                self.instance.quantity_orders.car
            )
        else:
            statistics['earnings'] = 0
        return statistics

    def get_working_hours(self, data):
        return [str(hours) for hours in WorkingHours.objects.filter(
            courier_id=self.instance.courier_id)]

    def get_regions(self, data):
        return Regions.get_regions(self.instance.courier_id)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        response = {}
        response.update(representation['data'])
        representation.pop('data')
        response.update(representation)
        return response
