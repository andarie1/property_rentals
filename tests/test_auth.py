import requests

BASE_URL = "http://localhost:8000/api"  # 🔁 Укажи нужный адрес

# ✅ Базовая обёртка для удобства
class RentalsApi:
    def __init__(self, role):
        self.username = f"test_{role}"
        self.password = "Testpass123!"
        self.role = role
        self.token = None
        self.headers = {}
        self.register_if_needed()
        self.login()

    # 📌 Регистрируем пользователя, если не существует
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
        if response.status_code == 400 and "username" in response.json():
            print(f"ℹ️ Пользователь {self.username} уже существует")
        elif response.status_code == 201:
            print(f"✅ Зарегистрирован новый пользователь: {self.username}")
        else:
            raise Exception(f"❌ Ошибка регистрации: {response.text}")

    # 🔑 Вход и получение JWT токена
    def login(self):
        url = f"{BASE_URL}/auth/login/"
        data = {
            "username": self.username,
            "password": self.password
        }
        response = requests.post(url, json=data)
        assert response.status_code == 200, f"❌ Ошибка входа: {response.text}"
        self.token = response.json().get("access")
        assert self.token, "❌ Токен не получен"
        self.headers = {"Authorization": f"Bearer {self.token}"}
        print(f"✅ Вход выполнен: {self.username}")

    # 🧪 Проверка получения информации о себе
    def get_me(self):
        url = f"{BASE_URL}/auth/me/"
        response = requests.get(url, headers=self.headers)
        assert response.status_code == 200, f"❌ Ошибка доступа к /me/: {response.text}"
        return response.json()


if __name__ == "__main__":
    # 🧪 Проверка для съёмщика (tenant)
    tenant = RentalsApi("tenant")
    me_tenant = tenant.get_me()
    assert me_tenant["role"] == "tenant", "❌ Роль должна быть tenant"
    print(f"🧾 Tenant user verified: {me_tenant['username']}")

    # 🧪 Проверка для арендодателя (landlord)
    landlord = RentalsApi("landlord")
    me_landlord = landlord.get_me()
    assert me_landlord["role"] == "landlord", "❌ Роль должна быть landlord"
    print(f"🧾 Landlord user verified: {me_landlord['username']}")

    print("✅ Тесты авторизации и ролей успешно пройдены")

