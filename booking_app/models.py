from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import uuid

class RoomFeature(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва особливості")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Іконка (CSS клас)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Особливість кімнати"
        verbose_name_plural = "Особливості кімнат"

class Room(models.Model):
    name = models.CharField(max_length=200, verbose_name="Назва кімнати")
    description = models.TextField(verbose_name="Опис")
    capacity = models.PositiveIntegerField(verbose_name="Місткість", validators=[MinValueValidator(1)])
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна за годину")
    features = models.ManyToManyField(RoomFeature, blank=True, verbose_name="Особливості")
    image = models.ImageField(upload_to='room_images/', blank=True, null=True, verbose_name="Зображення")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return f"{self.name} (до {self.capacity} осіб)"

    class Meta:
        verbose_name = "Кімната"
        verbose_name_plural = "Кімнати"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('cancelled', 'Скасовано'),
    ]

    user_name = models.CharField(max_length=100, verbose_name="Ім'я клієнта")
    user_email = models.EmailField(verbose_name="Email клієнта")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name="Кімната")
    start_time = models.DateTimeField(verbose_name="Початок бронювання")
    end_time = models.DateTimeField(verbose_name="Кінець бронювання")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    confirmation_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    notes = models.TextField(blank=True, verbose_name="Додаткові побажання")

    def __str__(self):
        return f"Бронювання #{self.id} - {self.room.name} ({self.start_time.strftime('%d.%m.%Y %H:%M')})"

    def is_valid_booking(self):
        overlapping_bookings = Booking.objects.filter(
            room=self.room,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(id=self.id)
        return not overlapping_bookings.exists()

    class Meta:
        verbose_name = "Бронювання"
        verbose_name_plural = "Бронювання"
        ordering = ['start_time']