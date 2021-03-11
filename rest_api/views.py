from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializer import *
from .models import Courier, Order


class Couriers(APIView):
    def post(self, request):
        if not request.data:
            return Response({'validation_error': {'couriers': []}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CourierCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response({'couriers': data}, status=status.HTTP_201_CREATED)
        error_id = [{'id': courier['courier_id']}
                    for error, courier in zip(serializer.errors['data'], serializer.initial_data['data']) if error]
        return Response({'validation_error': {'couriers': error_id}}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, courier_id):
        if not request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        instance = Courier.objects.filter(courier_id=courier_id).first()
        if not instance:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = CourierGetUpdateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
