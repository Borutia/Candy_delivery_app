import json

from django.test import TestCase


class OrdersPostTestCase(TestCase):
    def test_orders_good(self):
        """Загрузка данных, проверка статуса 201"""
        with open('rest_api/tests/orders/good_orders.json', 'r',
                  encoding='utf-8') as file:
            self.orders = json.load(file)
        response = self.client.post(
            '/orders',
            data=self.orders,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        response_data = {
            "orders": [
                {"id": 1},
                {"id": 2},
                {"id": 3},
                {"id": 4},
                {"id": 5},
                {"id": 6},
                {"id": 7}
            ]
        }
        self.assertEqual(response.data, response_data)

    def test_orders_bad(self):
        """Загрузка данных, проверка статуса 400"""
        with open('rest_api/tests/orders/bad_orders.json', 'r',
                  encoding='utf-8') as file:
            self.orders = json.load(file)
        response = self.client.post(
            '/orders',
            data=self.orders,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "orders": [
                    {"id": 4},
                    {"id": 6}
                ]
            }
        }
        self.assertEqual(response.data, response_data)

    def test_missing_data(self):
        """Обращение к обработчику с пустым телом, проверка статуса 400"""
        response = self.client.post(
            '/orders',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_non_unique_id(self):
        """Загрузка данных с неуникальными order_id, проверка статуса 400"""
        orders = {
            "data": [
                {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": [
                        "09:00-18:00"
                    ]
                }
            ]
        }
        self.client.post(
            '/orders',
            data=orders,
            content_type='application/json'
        )
        response = self.client.post(
            '/orders',
            data=orders,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "orders": [
                    {"id": 1}
                ]
            }
        }
        self.assertEqual(response.data, response_data)

    def test_missing_field(self):
        """Загрузка данных с пропущенным полем, проверка статуса 400"""
        orders = {
            "data": [
                {
                    "order_id": 4,
                    "weight": 0.23,
                    "delivery_hours": [
                        "09:00-18:00"
                    ]
                }
            ]
        }
        response = self.client.post(
            '/orders',
            data=orders,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "orders": [
                    {"id": 4}
                ]
            }
        }
        self.assertEqual(response.data, response_data)

    def test_empty_field(self):
        """Загрузка данных с пустым delivery_hours, проверка статуса 400"""
        orders = {
            "data": [
                {
                    "order_id": 5,
                    "weight": 15,
                    "region": 1,
                    "delivery_hours": []
                }
            ]
        }
        response = self.client.post(
            '/orders',
            data=orders,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "orders": [
                    {"id": 5}
                ]
            }
        }
        self.assertEqual(response.data, response_data)

    def test_validate_time(self):
        """Загрузка данных с невалидным временем, проверка статуса 400"""
        orders = {
            "data": [
                {
                    "order_id": 6,
                    "weight": 15,
                    "region": 1,
                    "delivery_hours": [
                        "09:00-25:00"
                    ]
                }
            ]
        }
        response = self.client.post(
            '/orders',
            data=orders,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "orders": [
                    {"id": 6}
                ]
            }
        }
        self.assertEqual(response.data, response_data)

    def test_negative_regions(self):
        """Загрузка данных с отрицательным районом, проверка статуса 400"""
        orders = {
            "data": [
                {
                    "order_id": 7,
                    "weight": 15,
                    "region": -1,
                    "delivery_hours": [
                        "09:00-15:00"
                    ]
                }
            ]
        }
        response = self.client.post(
            '/orders',
            data=orders,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "orders": [
                    {"id": 7}
                ]
            }
        }
        self.assertEqual(response.data, response_data)

    def test_wrong_weight(self):
        """Загрузка данных с невалидным весом, проверка статуса 400"""
        orders = {
            "data": [
                {
                    "order_id": 8,
                    "weight": 0,
                    "region": 1,
                    "delivery_hours": [
                        "09:00-15:00"
                    ]
                },
                {
                    "order_id": 9,
                    "weight": 50,
                    "region": 2,
                    "delivery_hours": [
                        "09:00-18:00"
                    ]
                },
                {
                    "order_id": 10,
                    "weight": 50.1,
                    "region": 3,
                    "delivery_hours": [
                        "09:00-18:00"
                    ]
                },
                {
                    "order_id": 11,
                    "weight": 0.01,
                    "region": 3,
                    "delivery_hours": [
                        "09:00-18:00"
                    ]
                },
                {
                    "order_id": 12,
                    "weight": -1,
                    "region": 3,
                    "delivery_hours": [
                        "09:00-18:00"
                    ]
                }
            ]
        }
        response = self.client.post(
            '/orders',
            data=orders,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "orders": [
                    {"id": 8},
                    {"id": 10},
                    {"id": 12}
                ]
            }
        }
        self.assertEqual(response.data, response_data)
