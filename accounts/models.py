from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField('Телефон', max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField('Email', unique=True, blank=True, null=True)
    telegram_id = models.CharField('Telegram ID', max_length=50, blank=True, null=True)
    total_spent_year = models.DecimalField('Сумма заказов за год', max_digits=10, decimal_places=2, default=0.00)
    discount_percent = models.PositiveSmallIntegerField('Текущая скидка (%)', default=0)
    agree_personal_data = models.BooleanField('Согласие на обработку ПД', default=False)
    agree_notifications_email = models.BooleanField('Согласие на уведомления по email', default=False)
    agree_notifications_telegram = models.BooleanField('Согласие на уведомления в Telegram', default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return self.get_full_name() or self.username

    def recalculate_discount(self):
        if self.total_spent_year >= 100000:
            self.discount_percent = 15
        elif self.total_spent_year >= 50000:
            self.discount_percent = 10
        elif self.total_spent_year >= 10000:
            self.discount_percent = 5
        else:
            self.discount_percent = 0
        self.save(update_fields=['discount_percent'])

class UserCar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars', verbose_name='Владелец')
    car_model = models.ForeignKey('services.CarModel', on_delete=models.CASCADE, verbose_name='Модель автомобиля')
    year = models.PositiveSmallIntegerField('Год выпуска', blank=True, null=True)
    license_plate = models.CharField('Госномер', max_length=20, blank=True, null=True)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Добавлен', auto_now_add=True)

    class Meta:
        verbose_name = 'Автомобиль клиента'
        verbose_name_plural = 'Автомобили клиентов'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.car_model} ({self.user})'

    @property
    def car_class(self):
        return self.car_model.car_class

    @property
    def body_type(self):
        return self.car_model.body_type
