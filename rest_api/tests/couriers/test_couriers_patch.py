from django.test import TestCase


class CouriersPatchTestCase(TestCase):
    def setUp(self):
        """Инициализация данных"""
        couriers = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        }
        self.client.post('/couriers', data=couriers, content_type='application/json')

    def test_courier_good(self):
        """Изменение данных, проверка статуса 200"""
        courier = {
            "working_hours": ["09:00-12:00"]
        }
        response = self.client.patch('/couriers/1', data=courier, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["09:00-12:00"]
        }
        self.assertEqual(response.data, response_data)

    def test_missing_data(self):
        """Обращение к обработчику с пустым телом, проверка статуса 400"""
        response = self.client.patch('/couriers/1', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_with_courier_id(self):
        """Передача запрещенного поля courier_id, проверка статуса 400"""
        courier = {
            "courier_id": 2
        }
        response = self.client.patch('/couriers/1', data=courier, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_wrong_courier_id(self):
        """Запрос на измение с несуществующим courier_id, проверка статуса 400"""
        courier = {
            "courier_type": "foot",
        }
        response = self.client.patch('/couriers/2', data=courier, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_empty_field(self):
        """Запрос на измение с пустым полем, проверка статуса 400"""
        courier = {
            "regions": [],
        }
        response = self.client.patch('/couriers/1', data=courier, content_type='application/json')
        self.assertEqual(response.status_code, 400)
