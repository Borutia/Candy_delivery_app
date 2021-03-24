from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import *
from .models import Courier, Order
from .const import ErrorMessage


class Couriers(APIView):
    def get(self, request, courier_id):
        """API GET /couriers/$courier_id"""
        instance = Courier.objects.filter(courier_id=courier_id).first()
        if not instance:
            return Response(
                {
                    'courier_id': ErrorMessage.INSTANCE_NOT_FOUND
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CouriersGetSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """API POST /couriers"""
        if not request.data or not request.data.get('data'):
            return Response(
                {
                    'validation_error': {
                        'couriers': []
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CourierCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response({'couriers': data}, status=status.HTTP_201_CREATED)
        error_id = [{'id': courier['courier_id']}
                    for error, courier in zip(serializer.errors['data'],
                                              serializer.initial_data['data']
                                              ) if error]
        return Response(
            {
                'validation_error': {
                    'couriers': error_id
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, courier_id):
        """API PATCH /couriers/$courier_id"""
        if not request.data:
            return Response(
                {
                    'data': ErrorMessage.DATA_NOT_FOUND
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        instance = Courier.objects.filter(courier_id=courier_id).first()
        if not instance:
            return Response(
                {
                    'courier_id': ErrorMessage.INSTANCE_NOT_FOUND
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CourierUpdateSerializer(
            instance,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Orders(APIView):
    def post(self, request):
        """API POST /orders"""
        if not request.data or not request.data.get('data'):
            return Response(
                {
                    'validation_error': {
                        'orders': []
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response(
                {
                    'orders': data
                },
                status=status.HTTP_201_CREATED
            )
        error_id = [{'id': order['order_id']}
                    for error, order in zip(serializer.errors['data'],
                                            serializer.initial_data['data']
                                            ) if error]
        return Response(
            {
                'validation_error': {
                    'orders': error_id
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class OrdersAssign(APIView):
    def post(self, request):
        """API POST /orders/assign"""
        if not request.data:
            return Response(
                {
                    'data': ErrorMessage.DATA_NOT_FOUND
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            instance = Courier.objects.filter(
                courier_id=request.data['courier_id']
            ).first()
        except Exception as e:
            return Response(
                {
                    'courier_id': ErrorMessage.ERROR_DATA,
                    'error': e
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if not instance:
            return Response(
                {
                    'courier_id': ErrorMessage.INSTANCE_NOT_FOUND
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = OrdersAssignSerializer(
            instance,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.validated_data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrdersComplete(APIView):
    def post(self, request):
        """API POST /orders/complete"""
        if not request.data:
            return Response(
                {
                    'data': ErrorMessage.DATA_NOT_FOUND
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            instance = Order.objects.filter(
                order_id=request.data['order_id']
            ).first()
        except Exception as e:
            return Response(
                {
                    'order_id': ErrorMessage.ERROR_DATA,
                    'error': e
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if not instance:
            return Response(
                {
                    'order_id': ErrorMessage.INSTANCE_NOT_FOUND
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = OrdersCompleteSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    'order_id': serializer.validated_data['order_id']
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
