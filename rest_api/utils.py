import tracemalloc
from functools import wraps
from itertools import product

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


def is_intersections(working_hours, delivery_hours):
    """
    Проверка пересечения времени работы курьера и промежутков,
    в которые клиенту удобно принять заказ
    """
    return any([True for (w_start, w_end), (d_start, d_end)
                in product(working_hours, delivery_hours)
                if w_start < d_end and w_end > d_start])


def calculate_rating(quantity, courier_type):
    """Заработок на один тип курьера"""
    return quantity * 500 * EARNINGS_COEFFICIENT[courier_type]


def profile(function_to_decorate):
    """Профилирование по памяти"""
    FILE_CHECK_MEMORY = 'serializer.py'
    tracemalloc.start()

    @wraps(function_to_decorate)
    def wrapper(*args, **kwargs):
        snapshot_start = tracemalloc.take_snapshot()
        result = function_to_decorate(*args, **kwargs)
        snapshot_stop = tracemalloc.take_snapshot()
        stats = snapshot_stop.compare_to(snapshot_start, 'lineno')
        sum_memory = 0
        for stat in stats:
            if stat.traceback[0].filename.find(FILE_CHECK_MEMORY) != -1:
                print(stat)
                sum_memory += stat.size
        print(f'Sum memory: {sum_memory}')
        return result
    return wrapper
