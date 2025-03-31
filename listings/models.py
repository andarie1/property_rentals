from django.db import models


class Listing(models.Model):
    HOUSING_TYPES = [
        ('apartment', 'Квартира'),
        ('house', 'Дом'),
        ('studio', 'Студия'),
    ]

    title = models.CharField(max_length=255)  # Заголовок объявления
    description = models.TextField()  # Описание
    location = models.CharField(max_length=255)  # Местоположение
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена
    rooms = models.PositiveIntegerField()  # Количество комнат
    housing_type = models.CharField(max_length=20, choices=HOUSING_TYPES)  # Тип жилья
    is_active = models.BooleanField(default=True)  # Активно/неактивно
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    updated_at = models.DateTimeField(auto_now=True)  # Дата обновления

    class Meta:
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return self.title







