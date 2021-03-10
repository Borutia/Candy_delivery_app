from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializer import *


class Couriers(APIView):
    def post(self, request):
        serializer = CourierCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            return Response({'couriers': data}, status=status.HTTP_201_CREATED)
        error_id = [{'id': courier['courier_id']}
                    for error, courier in zip(serializer.errors['data'], serializer.initial_data['data']) if error]
        return Response({'validation_error': {'couriers': error_id}}, status=status.HTTP_400_BAD_REQUEST)
