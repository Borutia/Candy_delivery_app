from datetime import datetime

from .const import FORMAT_TIME


def parse_time(time):
    """Парсер одного периода времени"""
    start, stop = time.split('-')
    start = datetime.strptime(start, FORMAT_TIME)
    stop = datetime.strptime(stop, FORMAT_TIME)
    return start, stop


def check_cross_of_time(working_hours, delivery_hours):
    """
    Проверка пересечения времени работы курьера и промежутков,
    в которые клиенту удобно принять заказ
    """
    for delivery_time in delivery_hours:
        for working_time in working_hours:
            working_start, working_stop = parse_time(working_time)
            delivery_start, delivery_stop = parse_time(delivery_time)
            if (working_start <= delivery_start < working_stop) or (delivery_start <= working_start < delivery_stop):
                return True
    return False
