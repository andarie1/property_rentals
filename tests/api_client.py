import requests
import json

with open("config.json") as f:
    config = json.load(f)

BASE_URL = config["base_url"]


class RentalsApi:
    def __init__(self, role):
        self.username = config[role]["username"]
        self.password = config[role]["password"]
        self.token = self.get_token()
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def get_token(self):
        url = f"{BASE_URL}/auth/login/"
        response = requests.post(url, json={
            "username": self.username,
            "password": self.password
        })
        assert response.status_code == 200, response.text
        return response.json()["access"]

    def register(self, username, email, password, password2, role):
        url = f"{BASE_URL}/auth/register/"
        response = requests.post(url, json={
            "username": username,
            "email": email,
            "password": password,
            "password2": password2,
            "role": role
        })
        assert response.status_code == 201, response.text
        return response.json()

    def get_listings(self):
        url = f"{BASE_URL}/listings/"
        response = requests.get(url, headers=self.headers)
        assert response.status_code == 200, response.text
        return response.json()

    def create_listing(self, title, price, location):
        if not self.token:
            raise Exception("❌ Ошибка: отсутствует токен авторизации. Проверь логин!")

        url = f"{BASE_URL}/listings/"
        data = {
            "title": title,
            "price": price,
            "location": location,
            "description": "Test listing",
            "rooms": 1,
            "housing_type": "apartment",
            "contact_info": "email@example.com"
        }
        response = requests.post(url, json=data, headers=self.headers)
        assert response.status_code == 201, f"❌ Ошибка при создании: {response.text}"
        return response.json()
