import json

from django.test import TestCase


class OrdersAssignTestCase(TestCase):
    def setUp(self):
        """Инициализация данных"""
        with open('rest_api/tests/orders/good_orders.json', 'r', encoding='utf-8') as file:
            self.orders = json.load(file)
        self.client.post('/orders', data=self.orders, content_type='application/json')
        with open('rest_api/tests/couriers/good_couriers.json', 'r', encoding='utf-8') as file:
            self.couriers = json.load(file)
        self.client.post('/couriers', data=self.couriers, content_type='application/json')

    def test_missing_data(self):
        """Обращение к обработчику с пустым телом, проверка статуса 400"""
        response = self.client.post('/orders/assign', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_wrong_courier_id(self):
        """Обращение к обработчику с несуществующим courier_id, проверка статуса 400"""
        courier = {
            "courier_id": 100,
        }
        response = self.client.post('/orders/assign', data=courier, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_orders_assign(self):
        """Обращение к обработчику, проверка назначения заказов, проверка статуса 200"""
        courier = {
            "courier_id": 1,
        }
        response = self.client.post('/orders/assign', data=courier, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_orders = [{"id": 3}, {"id": 5}]
        self.assertContains(response, 'assign_time')
        self.assertEqual(response.data['orders'], response_orders)

    def test_idempotence(self):
        """Обращение к обработчику, проверка идемпотентности, проверка статуса 200"""
        courier = {
            "courier_id": 1,
        }
        first_response = self.client.post('/orders/assign', data=courier, content_type='application/json')
        self.assertEqual(first_response.status_code, 200)
        courier = {
            "courier_id": 1,
        }
        second_response = self.client.post('/orders/assign', data=courier, content_type='application/json')
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(first_response.data, second_response.data)

    def test_no_order(self):
        """Обращение к обработчику, проверка когда не удалось найти подходящих заказов, проверка статуса 200"""
        courier = {
            "courier_id": 4,
        }
        response = self.client.post('/orders/assign', data=courier, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = {"orders": []}
        self.assertEqual(response.data, response_data)

    def test_available_to_another(self):
        """
        Обращение к обработчику, проверка заказов, выданные одному курьеру,
        не должны быть доступны для выдачи другому
        """
        courier_1 = {
            "courier_id": 1,
        }
        first_response = self.client.post('/orders/assign', data=courier_1, content_type='application/json')
        courier_2 = {
            "courier_id": 5,
        }
        second_response = self.client.post('/orders/assign', data=courier_2, content_type='application/json')
        self.assertNotEquals(first_response, second_response)
        response_date = [{'id': 4}]
        self.assertEqual(second_response.data['orders'], response_date)
        first_orders = [order_id['id'] for order_id in first_response.data['orders']]
        second_orders = [order_id['id'] for order_id in second_response.data['orders']]
        self.assertEqual(list(set(first_orders) & set(second_orders)), [])
