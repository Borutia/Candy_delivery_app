FORMAT_TIME = '%H:%M'


class CourierType:
    FOOT = 'foot'
    BIKE = 'bike'
    CAR = 'car'
    choices = (
        (FOOT, 'Пеший курьер'),
        (BIKE, 'Велокурьер'),
        (CAR, 'Курьер на автомобиле'),
    )
