import json

from django.test import TestCase


class CouriersGetTestCase(TestCase):
    def setUp(self):
        """Инициализация данных"""
        with open('rest_api/tests/orders/good_orders.json', 'r',
                  encoding='utf-8') as file:
            self.orders = json.load(file)
        self.client.post(
            '/orders',
            data=self.orders,
            content_type='application/json'
        )
        with open('rest_api/tests/couriers/good_couriers.json', 'r',
                  encoding='utf-8') as file:
            self.couriers = json.load(file)
        self.client.post(
            '/couriers',
            data=self.couriers,
            content_type='application/json'
        )
        courier = {
            "courier_id": 1,
        }
        self.client.post(
            '/orders/assign',
            data=courier,
            content_type='application/json'
        )
        data = {
            "courier_id": 1,
            "order_id": 3,
            "complete_time": "2121-03-17T09:53:11.649422Z"
        }
        self.client.post(
            '/orders/complete',
            data=data,
            content_type='application/json'
        )

    def test_wrong_courier_id(self):
        """Запрос с несуществующим courier_id, проверка статуса 400"""
        response = self.client.get(
            '/couriers/10',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
