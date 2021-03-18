import json

from django.test import TestCase


class CouriersPostTestCase(TestCase):
    def test_couriers_good(self):
        """Загрузка данных, проверка статуса 201"""
        with open('rest_api/tests/couriers/good_couriers.json', 'r',
                  encoding='utf-8') as file:
            self.couriers = json.load(file)
        response = self.client.post(
            '/couriers',
            data=self.couriers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        response_data = {
            "couriers": [
                {"id": 1},
                {"id": 2},
                {"id": 3},
                {"id": 4},
                {"id": 5}
            ]
        }
        self.assertEqual(response.data, response_data)

    def test_couriers_bad(self):
        """Загрузка данных, проверка статуса 400"""
        with open('rest_api/tests/couriers/bad_couriers.json', 'r',
                  encoding='utf-8') as file:
            self.couriers = json.load(file)
        response = self.client.post(
            '/couriers',
            data=self.couriers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "couriers": [
                    {"id": 4},
                    {"id": 6}
                ]
            }
        }
        self.assertEqual(response.data, response_data)

    def test_missing_data(self):
        """Обращение к обработчику с пустым телом, проверка статуса 400"""
        response = self.client.post(
            '/couriers',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_non_unique_id(self):
        """Загрузка данных с неуникальными courier_id, проверка статуса 400"""
        orders = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        }
        self.client.post(
            '/couriers',
            data=orders,
            content_type='application/json'
        )
        response = self.client.post(
            '/couriers',
            data=orders,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "couriers": [
                    {"id": 1}
                ]
            }
        }
        self.assertEqual(response.data, response_data)

    def test_missing_field(self):
        """Загрузка данных с пропущенным полем, проверка статуса 400"""
        couriers = {
            "data": [
                {
                    "courier_id": 4,
                    "courier_type": "foot",
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        }
        response = self.client.post(
            '/couriers',
            data=couriers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "couriers": [
                    {"id": 4}
                ]
            }
        }
        self.assertEqual(response.data, response_data)

    def test_empty_field(self):
        """Загрузка данных с пустым полем, проверка статуса 400"""
        couriers = {
            "data": [
                {
                    "courier_id": 5,
                    "courier_type": "foot",
                    "regions": [],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        }
        response = self.client.post(
            '/couriers',
            data=couriers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "couriers": [
                    {"id": 5}
                ]
            }
        }
        self.assertEqual(response.data, response_data)

    def test_validate_time(self):
        """Загрузка данных с невалидным временем, проверка статуса 400"""
        couriers = {
            "data": [
                {
                    "courier_id": 6,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["31:35-14:05", "09:00-11:00"]
                }
            ]
        }
        response = self.client.post(
            '/couriers',
            data=couriers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "couriers": [
                    {"id": 6}
                ]
            }
        }
        self.assertEqual(response.data, response_data)

    def test_negative_regions(self):
        """Загрузка данных с отрицательным районом, проверка статуса 400"""
        couriers = {
            "data": [
                {
                    "courier_id": 7,
                    "courier_type": "foot",
                    "regions": [1, 12, -22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        }
        response = self.client.post(
            '/couriers',
            data=couriers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "couriers": [
                    {"id": 7}
                ]
            }
        }
        self.assertEqual(response.data, response_data)

    def test_wrong_courier_type(self):
        """Загрузка данных с невалидным типом курьера, проверка статуса 400"""
        couriers = {
            "data": [
                {
                    "courier_id": 8,
                    "courier_type": "bus",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        }
        response = self.client.post(
            '/couriers',
            data=couriers,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response_data = {
            'validation_error': {
                "couriers": [
                    {"id": 8}
                ]
            }
        }
        self.assertEqual(response.data, response_data)
