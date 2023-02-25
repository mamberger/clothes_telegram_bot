import requests

from data.config import API_CORE, user, password


class APIClient:
    """
    Класс для запросов к API.
    Все функции принимают относительный url
    Маршруты формируются на основе переменной API_CORE
    """

    user = user
    password = password
    base_headers = None

    @classmethod
    def admin_auth(cls, telegram_id):
        token = cls.get_auth_token()
        response = requests.get(url=API_CORE + f'telegram-user/?telegram_id={telegram_id}&is_staff=1',
                                headers={"Authorization": f"Token {token}"})
        if response.status_code == 200:
            return response.json()
        return 0

    @staticmethod
    def get_auth_token():
        data = {
            "username": user,
            "password": password
        }
        response = requests.post(url=API_CORE + 'auth/', data=data)
        result = 0
        if response.status_code == 200:
            result = response.json()['token']
        return result

    @classmethod
    def get_by_query_string(cls, url, filter_data):
        filters = {}
        for key, value in filter_data.items():
            if not value or value == '':
                continue
            filters[key] = value

        url += '?' + '&'.join(
            '{}={}'.format(key, value) for key, value in filters.items()
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

    @classmethod
    def get(cls, url, data=None, headers=None):
        url = API_CORE + url
        headers = cls.get_headers(headers)
        response = requests.get(
            url=url, headers=headers, data=data
        )

        data = response.json()
        return data

    @classmethod
    def patch(cls, url, data=None, headers=None):
        url = API_CORE + url
        headers = cls.get_headers(headers)
        response = requests.patch(url=url, data=data, headers=headers)
        data = response.json()

        return data

    @classmethod
    def get_base_headers(cls):
        if not cls.base_headers:
            token = cls.get_auth_token()

            cls.base_headers = {
                "Authorization": f"Token {token}",
            }
        return cls.base_headers

    @classmethod
    def get_headers(cls, headers: dict):
        try:
            headers.update(**cls.get_base_headers())
        except AttributeError:
            headers = cls.get_base_headers()

        return headers

    @classmethod
    def add_new_admin(cls, telegram_id):
        headers = cls.get_base_headers()
        response = requests.get(url=API_CORE + f"telegram-user/?telegram_id={telegram_id}",
                                headers=headers)
        pk = 0
        if response.status_code == 200:
            if response.json():
                pk = response.json()[0]['id']
        if not pk:
            response = requests.post(url=API_CORE + 'telegram-user/', headers=headers,
                                     data={'telegram_id': telegram_id, "is_staff": True})
            if response.status_code == 201:
                return 1
        else:
            response = requests.patch(url=API_CORE + f"telegram-user/{pk}/",
                                      headers=headers, data={"is_staff": True})
            if response.status_code == 200:
                if response.json()['is_staff']:
                    return 1
        return 0

    @classmethod
    def get_admin_list_text(cls):
        response = requests.get(url=API_CORE + 'telegram-user/?is_staff=1',
                                headers=cls.get_base_headers())
        if response.status_code == 200:
            data = response.json()
            text = 'Список Админов\nID'
            for admin in data:
                text += f"\n{admin['telegram_id']}"
            return text
        return 0

    @classmethod
    def delete_admin(cls, telegram_id):
        headers = cls.get_base_headers()
        url = API_CORE + f'telegram-user/'

        response = requests.get(
            url=url + f'?telegram_id={telegram_id}&is_staff=1',
            headers=headers
        )

        if response.status_code == 200:
            if not response.json():
                return 0
            pk = response.json()[0]['id']

            response = requests.patch(url=url + f'{pk}/',
                                      headers=headers,
                                      data={'is_staff': False})

            if response.status_code == 200:
                if not response.json()['is_staff']:
                    return 1
        return 0

    @classmethod
    def create_telegram_user(cls, telegram_id):
        response = requests.post(
            API_CORE + "telegram-user/",
            headers=cls.get_base_headers(),
            data={"telegram_id": telegram_id}
        )

        if response.status_code == 201:
            return response.json()['id']
        return 0

    @classmethod
    def get_or_create_user(cls, telegram_id):
        headers = cls.get_base_headers()
        url = API_CORE + f"telegram-user/?telegram_id={telegram_id}"

        response = requests.get(url=url, headers=headers)

        if response.status_code == 200:
            if response.json():
                pk = response.json()[0]['id']
            else:
                pk = cls.create_telegram_user(telegram_id)
        else:
            return 0
        return pk
