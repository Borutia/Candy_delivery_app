from decimal import Decimal


class CourierType:
    """Тип курьера"""
    FOOT = 'foot'
    BIKE = 'bike'
    CAR = 'car'
    choices = (
        (FOOT, 'Пеший курьер'),
        (BIKE, 'Велокурьер'),
        (CAR, 'Курьер на автомобиле'),
    )


class StatusOrder:
    """Статус заказа"""
    NEW = 'N'
    IN_PROCESS = 'I'
    COMPLETE = 'C'
    choices = (
        (NEW, 'Новый'),
        (IN_PROCESS, 'В обработке'),
        (COMPLETE, 'Доставлен'),
    )


class StatusCourier:
    """Статус курьера"""
    FREE = 'F'
    BUSY = 'B'
    choices = (
        (FREE, 'Свободен'),
        (BUSY, 'Занят'),
    )


class ErrorMessage:
    """Ответы на ошибку когда экземпляр не найден"""
    INSTANCE_NOT_FOUND = 'Instance not found'
    DATA_NOT_FOUND = 'Data not found'


# Грузоподъемность курьера
LIFTING_CAPACITY = {
    'foot': Decimal(10),
    'bike': Decimal(15),
    'car': Decimal(50)
}

# Коэффициент заработка
EARNINGS_COEFFICIENT = {
    'foot': 2,
    'bike': 5,
    'car': 9
}

# Формат времени
FORMAT_TIME = '%H:%M'
