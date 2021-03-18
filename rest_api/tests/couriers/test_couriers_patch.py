import json

from django.test import TestCase


class CouriersPatchTestCase(TestCase):
    def setUp(self):
        """Инициализация данных"""
        couriers = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "bike",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        }
        self.client.post(
            '/couriers',
            data=couriers,
            content_type='application/json'
        )
        with open('rest_api/tests/orders/good_orders.json', 'r',
                  encoding='utf-8') as file:
            self.orders = json.load(file)
        self.client.post(
            '/orders',
            data=self.orders,
            content_type='application/json'
        )

    def test_courier_good(self):
        """Изменение данных, проверка статуса 200"""
        courier = {
            "working_hours": ["09:00-12:00"]
        }
        response = self.client.patch(
            '/couriers/1',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = {
            "courier_id": 1,
            "courier_type": "bike",
            "regions": [1, 12, 22],
            "working_hours": ["09:00-12:00"]
        }
        self.assertEqual(response.data, response_data)

    def test_missing_data(self):
        """Обращение к обработчику с пустым телом, проверка статуса 400"""
        response = self.client.patch(
            '/couriers/1',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_forbidden_courier_id(self):
        """Передача запрещенного поля courier_id, проверка статуса 400"""
        courier = {
            "courier_id": 2
        }
        response = self.client.patch(
            '/couriers/1',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_wrong_courier_id(self):
        """
        Запрос на измение с несуществующим courier_id, проверка статуса 400
        """
        courier = {
            "courier_type": "foot",
        }
        response = self.client.patch(
            '/couriers/2',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_empty_field(self):
        """Запрос на измение с пустым полем, проверка статуса 400"""
        courier = {
            "regions": [],
        }
        response = self.client.patch(
            '/couriers/1',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_change_courier_type(self):
        """
        Обращение к обработчику, назначение заказов, смена типа курьера,
        проверка удаляения не подходящих заказов проверка статуса 200
        """
        courier = {
            "courier_id": 1,
        }
        response = self.client.post(
            '/orders/assign',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_orders = [{"id": 3}, {"id": 4}, {"id": 5}]
        response = sorted(response.data['orders'], key=lambda dct: dct['id'])
        self.assertEqual(response, response_orders)
        courier_type = {
            "courier_type": "foot",
        }
        response = self.client.patch(
            '/couriers/1',
            data=courier_type,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            '/orders/assign',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_orders = [{"id": 3}, {"id": 5}]
        response = sorted(response.data['orders'], key=lambda dct: dct['id'])
        self.assertEqual(response, response_orders)

    def test_change_regions(self):
        """
        Обращение к обработчику, назначение заказов, смена районов,
        проверка удаляения не подходящих заказов проверка статуса 200
        """
        courier = {
            "courier_id": 1,
        }
        response = self.client.post(
            '/orders/assign',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_orders = [{"id": 3}, {"id": 4}, {"id": 5}]
        response = sorted(response.data['orders'], key=lambda dct: dct['id'])
        self.assertEqual(response, response_orders)
        regions = {
            "regions": [1],
        }
        response = self.client.patch(
            '/couriers/1',
            data=regions,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            '/orders/assign',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_orders = [{"id": 4}]
        self.assertEqual(response.data['orders'], response_orders)

    def test_change_working_hours(self):
        """
        Обращение к обработчику, назначение заказов, смена графика работы,
        проверка удаляения не подходящих заказов проверка статуса 200
        """
        courier = {
            "courier_id": 1,
        }
        response = self.client.post(
            '/orders/assign',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_orders = [{"id": 3}, {"id": 4}, {"id": 5}]
        response = sorted(response.data['orders'], key=lambda dct: dct['id'])
        self.assertEqual(response, response_orders)
        regions = {
            "working_hours": ["09:00-14:00"]
        }
        response = self.client.patch(
            '/couriers/1',
            data=regions,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            '/orders/assign',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_orders = [{"id": 4}]
        self.assertEqual(response.data['orders'], response_orders)
