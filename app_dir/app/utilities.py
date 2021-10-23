from datetime import datetime, timedelta


class TimeRange:
    """
    класс имитирует поведение временного отрезка, упрощает работу внутри проекта
    """

    def __init__(self, start, finish):
        self.start = start
        self.finish = finish

    def __repr__(self):
        return f'{self.start} -- {self.finish}'

    # для ф-ии сортировки внутри ф-ии datetime_list_to_dict
    def __lt__(self, other):
        return self.start < other.start

    def __contains__(self, item):
        return self.start <= item <= self.finish

    # два разных in-а, потому что есть классический, для проверки входа точки времени во временной дипазон, а есть
    # специальный, необходимый для определения свободных "временных окон"
    def _in(self, item):
        return self.start < item < self.finish

    def are_ranges_intersect(self, current_range):
        """
        ф-я определяет пересекаются ли два временных промежутка, НЕ ВКЛЮЧАЯ точки входа-выхода
        :param current_range: экземпляр класса TimeRange
        :return: пересекаются ли два временных отрезка - да/нет
        """
        return self._in(current_range.start) or self._in(current_range.finish)


def datetime_list_to_dict(datetime_list):
    """
    :param datetime_list: список из кортежей формата (начало временного отрезка, его конец), всё экземпляры datetime.datetime
    :return: словарь формата {дата1: [список экземпляров TimeRange], дата2: [список экземпляров TimeRange],}
    список экземпляров TimeRange отсортирован по дате начала
    """
    if not datetime_list:
        return {}
    res = {datetime_list[0][0].date(): [TimeRange(datetime_list[0][0].time(), datetime_list[0][1].time())]}
    del datetime_list[0]
    while datetime_list:
        item = datetime_list[0]
        i_date = item[0].date()
        if i_date in res.keys():
            res[i_date].append(TimeRange(item[0].time(), item[1].time()))
            res[i_date].sort()
        else:
            res[i_date] = [TimeRange(item[0].time(), item[1].time())]
        datetime_list.remove(item)

    return res


def is_time_in_range_list(current, range_list):
    """

    :param current: экземпляр datetime.time
    :param range_list: список экземпляров TimeRange
    :return: содержится ли точка времени current любом из отрезков в range_list - да/нет
    """
    return any([current in range_item for range_item in range_list])


def are_ranges_intersect_list(current_range, range_list):
    """

    :param current_range: отрезок времени - экземпляр TimeRange
    :param range_list: список экземпляров TimeRange
    :return: пересекается ли отрезок времени current_range с любым из отрезков в range_list - да/нет
    """
    return any([range_item.are_ranges_intersect(current_range) for range_item in range_list])


def from_str_to_timedelta(str_time):
    tmp = datetime.strptime(str_time, '%H:%M:%S')
    return timedelta(hours=tmp.hour, minutes=tmp.minute)
