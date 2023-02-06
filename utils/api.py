import requests

from data.config import API_CORE


class API:
    """
    Класс для запросов к API.
    Все функции принимают относительный url
    Маршруты формируются на основе переменной API_CORE
    """

    @staticmethod
    def get(url):
        url = API_CORE + url
        response = requests.get(url=url)
        data = response.json()

        return data

    @classmethod
    def get_by_query_string(cls, url, filter_data):
        url += '?' + '&'.join(
            '{}={}'.format(key, value) for key, value in filter_data.items()
        )

        return cls.get(url)
