import requests

BASE_URL = "http://localhost:8000/api"


class RentalsApi:
    def __init__(self, role):
        self.username = f"test_{role}"
        self.password = "Testpass123!"
        self.role = role
        self.token = None
        self.headers = {}
        self.register_if_needed()
        self.login()

    def register_if_needed(self):
        url = f"{BASE_URL}/auth/register/"
        data = {
            "username": self.username,
            "email": f"{self.username}@example.com",
            "password": self.password,
            "password2": self.password,
            "role": self.role
        }
        response = requests.post(url, json=data)
        if response.status_code not in (201, 400):
            raise Exception(f"❌ Ошибка регистрации: {response.text}")

    def login(self):
        url = f"{BASE_URL}/auth/login/"
        data = {
            "username": self.username,
            "password": self.password
        }
        response = requests.post(url, json=data)
        assert response.status_code == 200, f"❌ Ошибка входа: {response.text}"
        self.token = response.json().get("access")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    # 📌 Создание объявления
    def create_listing(self, title, price, location):
        url = f"{BASE_URL}/listings/"
        data = {
            "title": title,
            "price": price,
            "location": location,
            "description": "Test description",
            "rooms": 2,
            "housing_type": "apartment",
            "contact_info": "landlord@example.com"
        }
        response = requests.post(url, json=data, headers=self.headers)
        assert response.status_code == 201, f"❌ Ошибка создания объявления: {response.text}"
        return response.json()

    # Получение всех объявлений
    def get_listings(self):
        url = f"{BASE_URL}/listings/"
        response = requests.get(url, headers=self.headers)
        assert response.status_code == 200, f"❌ Ошибка получения объявлений: {response.text}"
        return response.json()


if __name__ == "__main__":
    # Только landlord может создавать объявления
    landlord = RentalsApi("landlord")
    new_listing = landlord.create_listing("Cozy Flat", 1800, "Amsterdam West")
    print(f"✅ Создано объявление: {new_listing['title']}")

    # Tenant может просматривать объявления
    tenant = RentalsApi("tenant")
    listings = tenant.get_listings()
    print(f"📄 Всего объявлений доступно арендаторам: {len(listings)}")
    assert any(l["title"] == "Cozy Flat" for l in listings), "❌ Объявление не найдено"

    print("✅ Тесты объявлений успешно пройдены")
