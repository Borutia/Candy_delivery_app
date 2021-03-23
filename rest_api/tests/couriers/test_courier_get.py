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
        self.courier = 1
        courier = {
            "courier_id": 1,
        }
        self.client.post(
            '/orders/assign',
            data=courier,
            content_type='application/json'
        )
        data = {
            "courier_id": self.courier,
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
            '/couriers/100',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_information_courier_rating(self):
        """
        Обращение к обработчику, проверка информации о курьере
        без рейтинга и с 0 заработком,
        проверка статуса 200
        """
        response = self.client.get(
            f'/couriers/{self.courier}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'earnings')
        self.assertNotContains(response, 'rating')
        self.assertEqual(response.data['earnings'], 0)

    def test_information_courier_earnings(self):
        """
        Обращение к обработчику, проверка информации о курьере
        c рейтингом и заработком,
        проверка статуса 200
        """
        data = {
            "courier_id": self.courier,
            "order_id": 5,
            "complete_time": "2121-03-17T09:53:11.649422Z"
        }
        self.client.post(
            '/orders/complete',
            data=data,
            content_type='application/json'
        )
        response = self.client.get(
            f'/couriers/{self.courier}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'earnings')
        self.assertContains(response, 'rating')
        self.assertEqual(response.data['earnings'], 1000)

    def test_earnings_after_change_courier_type(self):
        """
        Обращение к обработчику, проверка информации о курьере
        c рейтингом и заработком после смены типа курьера,
        проверка статуса 200
        """
        courier = {
            "courier_type": "car",
        }
        self.client.patch(
            f'/couriers/{self.courier}',
            data=courier,
            content_type='application/json'
        )
        data = {
            "courier_id": self.courier,
            "order_id": 5,
            "complete_time": "2121-03-17T09:53:11.649422Z"
        }
        self.client.post(
            '/orders/complete',
            data=data,
            content_type='application/json'
        )
        response = self.client.get(
            f'/couriers/{self.courier}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'earnings')
        self.assertContains(response, 'rating')
        self.assertEqual(response.data['earnings'], 1000)
