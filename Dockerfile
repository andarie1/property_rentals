FROM python:3.12-slim

# Рабочая директория в контейнере
WORKDIR /app

# Копируем зависимости и код
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Команда для запуска Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# andarie1/rental_system - DockerHub