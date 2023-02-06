import requests

from data.config import API_CORE


class API:
    """
    Класс для запросов к API.
    Все функции принимают относительный url
    Маршруты формируются на основе переменной API_CORE
    """

    @classmethod
    def get_by_query_string(cls, url, filter_data):
        url += '?' + '&'.join(
            '{}={}'.format(key, value) for key, value in filter_data.items()
        )

        return cls.get(url)

    @classmethod
    def update_model(cls, data: dict):
        data_dict = {data['field']: data['value']}
        response = cls.patch(
            f"{data['model']}/{data['id']}/",
            data_dict
        )
        valid = cls.validate_response(response, data['field'], data['value'])
        if valid:
            return 1

        return 0

    @staticmethod
    def validate_response(response, field, value):
        try:
            if str(response[field]) == str(value):
                return 1
            elif str(response[field]) == str([value]):
                return 1
            elif float(response[field]) == float(value):
                return 1
        except TypeError:
            pass
        return 0

    @staticmethod
    def get(url):
        url = API_CORE + url
        response = requests.get(url=url)
        data = response.json()

        return data

    @staticmethod
    def patch(url, data):
        url = API_CORE + url
        response = requests.patch(url=url, data=data)
        data = response.json()

        return data
