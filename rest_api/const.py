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


# Грузоподъемность курьера
LIFTING_CAPACITY = {
    'foot': 10,
    'bike': 15,
    'car': 50
}

# Формат времени
FORMAT_TIME = '%H:%M'
