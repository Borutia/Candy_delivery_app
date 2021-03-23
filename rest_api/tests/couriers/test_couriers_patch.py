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
                },
                {
                    "courier_id": 7,
                    "courier_type": "foot",
                    "regions": [
                        50,
                        51
                    ],
                    "working_hours": [
                        "09:00-18:00"
                    ]
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
            "working_hours": ["09:00-12:00"],
            "courier_type": "foot",
            "regions": [1, 22],
        }
        response = self.client.patch(
            '/couriers/1',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 22],
            "working_hours": ["09:00-12:00"]
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code, 200)

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
        Запрос на изменение с несуществующим courier_id, проверка статуса 400
        """
        courier = {
            "courier_type": "foot",
        }
        response = self.client.patch(
            '/couriers/100',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_validate_time(self):
        """Запрос на изменение с невалидным временем, проверка статуса 400"""
        courier = {
            "working_hours": ["31:35-14:05"],
        }
        response = self.client.patch(
            '/couriers/1',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_negative_region(self):
        """Запрос на изменение с отрицательным районом, проверка статуса 400"""
        courier = {
            "regions": [-10, 5],
        }
        response = self.client.patch(
            '/couriers/1',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_empty_regions(self):
        """Запрос на изменение с пустым regions, проверка статуса 400"""
        courier = {
            "regions": [],
        }
        response = self.client.patch(
            '/couriers/1',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_empty_working_hours(self):
        """Запрос на изменение с пустым working_hours, проверка статуса 400"""
        courier = {
            "working_hours": [],
        }
        response = self.client.patch(
            '/couriers/1',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_wrong_courier_type(self):
        """Загрузка данных с невалидным типом курьера, проверка статуса 400"""
        courier = {
            "courier_type": "bus",
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
        проверка удаления не подходящих заказов, проверка статуса 200
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
        self.assertEqual(
            response.data['courier_type'], courier_type['courier_type']
        )
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
        проверка удаления не подходящих заказов, проверка статуса 200
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
        self.assertEqual(
            response.data['regions'], regions['regions']
        )
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
        проверка удаления не подходящих заказов, проверка статуса 200
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
        working_hours = {
            "working_hours": ["09:00-14:00"]
        }
        response = self.client.patch(
            '/couriers/1',
            data=working_hours,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['working_hours'], working_hours['working_hours']
        )
        response = self.client.post(
            '/orders/assign',
            data=courier,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_orders = [{"id": 4}]
        self.assertEqual(response.data['orders'], response_orders)

    def test_delivery_delete_all_orders(self):
        """
        Обращение к обработчику, назначение заказов, смена района,
        удаления все активных заказов, проверка заработной платы
        """
        courier = {
            "courier_id": 1,
        }
        self.client.post(
            '/orders/assign',
            data=courier,
            content_type='application/json'
        )
        regions = {
            "regions": [100],
        }
        self.client.patch(
            '/couriers/1',
            data=regions,
            content_type='application/json'
        )
        response = self.client.get(
            f'/couriers/1',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'earnings')
        self.assertNotContains(response, 'rating')
        self.assertEqual(response.data['earnings'], 0)

    def test_delivery_complete_one_order(self):
        """
        Обращение к обработчику, назначение заказов, смена района,
        оставить один активных заказов, подтвержить его,
        проверка заработной платы и наличие рейтинга
        """
        courier = {
            "courier_id": 7,
        }
        self.client.post(
            '/orders/assign',
            data=courier,
            content_type='application/json'
        )
        data = {
            "courier_id": 7,
            "order_id": 6,
            "complete_time": "2121-03-17T09:53:11.649422Z"
        }
        self.client.post(
            '/orders/complete',
            data=data,
            content_type='application/json'
        )
        regions = {
            "regions": [50],
        }
        self.client.patch(
            '/couriers/7',
            data=regions,
            content_type='application/json'
        )
        response = self.client.get(
            f'/couriers/7',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'earnings')
        self.assertContains(response, 'rating')
        self.assertEqual(response.data['earnings'], 1000)
