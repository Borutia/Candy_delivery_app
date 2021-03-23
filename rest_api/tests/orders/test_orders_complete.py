import json

from django.test import TestCase


class OrdersCompleteTestCase(TestCase):
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

    def test_missing_data(self):
        """Обращение к обработчику с пустым телом, проверка статуса 400"""
        response = self.client.post(
            '/orders/complete',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_missing_field(self):
        """Загрузка данных с пропущенным полем, проверка статуса 400"""
        data = {
            "order_id": 5,
            "complete_time": "2121-03-17T09:53:11.649422Z"
        }
        response = self.client.post(
            '/orders/complete',
            data=data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_order_not_assign(self):
        """
        Обращение к обработчику с неназначенным или несуществующим заказом,
        проверка статуса 400
        """
        data = {
            "courier_id": 1,
            "order_id": 500,
            "complete_time": "2121-03-17T09:53:11.649422Z"
        }
        response = self.client.post(
            '/orders/complete',
            data=data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_orders_complete(self):
        """Обращение к обработчику завершения заказов, проверка статуса 200"""
        data = {
            "courier_id": 1,
            "order_id": 3,
            "complete_time": "2121-03-17T09:53:11.649422Z"
        }
        response = self.client.post(
            '/orders/complete',
            data=data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        order = {
            'order_id': 3
        }
        self.assertEqual(response.data, order)

    def test_wrong_time(self):
        """Загрузка данных с невалидным временем, проверка статуса 400"""
        data = {
            "courier_id": 1,
            "order_id": 5,
            "complete_time": "2121-31-17T09:53:11.649422Z"
        }
        response = self.client.post(
            '/orders/complete',
            data=data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_complete_time_less(self):
        """
        Загрузка данных когда время выполненния заказа раньше,
        чем время назначения, проверка статуса 400
        """
        data = {
            "courier_id": 1,
            "order_id": 5,
            "complete_time": "2010-02-17T09:53:11.649422Z"
        }
        response = self.client.post(
            '/orders/complete',
            data=data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_wrong_courier_id(self):
        """
        Обращение к обработчику с неверным courier_id, проверка статуса 400
        """
        data = {
            "courier_id": 10,
            "order_id": 3,
            "complete_time": "2121-03-17T09:53:11.649422Z"
        }
        response = self.client.post(
            '/orders/complete',
            data=data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_idempotence(self):
        """
        Обращение к обработчику, проверка идемпотентности,
        проверка статуса 200
        """
        data = {
            "courier_id": 1,
            "order_id": 5,
            "complete_time": "2121-03-17T09:53:11.649422Z"
        }
        first_response = self.client.post(
            '/orders/complete',
            data=data,
            content_type='application/json'
        )
        self.assertEqual(first_response.status_code, 200)
        second_response = self.client.post(
            '/orders/complete',
            data=data,
            content_type='application/json'
        )
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(first_response.data, second_response.data)
