from .const import EARNINGS_COEFFICIENT


def parse_time(time):
    """Парсер одного периода времени"""
    start, stop = time.split('-')
    return start, stop


def get_correct_hours(list_hours):
    """Разделение времени на начало и конец"""
    time = []
    for current_time in list_hours:
        start, stop = parse_time(current_time)
        time.append({
            'start_time': start,
            'stop_time': stop
        })
    return time


def get_regions(regions):
    """Преобразование районов для сериализатора"""
    return [
        {
            'region': region
        } for region in regions
    ]


def check_cross_of_time(working_hours, delivery_hours):
    """
    Проверка пересечения времени работы курьера и промежутков,
    в которые клиенту удобно принять заказ
    """
    for delivery_time in delivery_hours:
        for working_time in working_hours:
            working_start, working_stop = working_time
            delivery_start, delivery_stop = delivery_time
            if (working_start <= delivery_start < working_stop) \
                    or (delivery_start <= working_start < delivery_stop):
                return True
    return False


def calculate_rating(quantity, courier_type):
    """Заработок на один тип курьера"""
    return quantity * 500 * EARNINGS_COEFFICIENT[courier_type]
