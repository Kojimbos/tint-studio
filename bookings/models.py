from django.db import models
from django.conf import settings
from utils.notifications import notify_client_about_booking, notify_admin_about_booking

class Booking(models.Model):
    SERVICE_TYPES = [
        ('tint', 'Тонировка'),
        ('armor', 'Бронирование'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждена'),
        ('completed', 'Выполнена'),
        ('cancelled', 'Отменена'),
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='bookings', verbose_name='Клиент')
    car = models.ForeignKey('accounts.UserCar', on_delete=models.SET_NULL, null=True,
                            related_name='bookings', verbose_name='Автомобиль')
    service_type = models.CharField('Тип услуги', max_length=10, choices=SERVICE_TYPES)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    tint_film_percent = models.ForeignKey('services.FilmTintPercent', on_delete=models.SET_NULL,
                                          null=True, blank=True, verbose_name='Плёнка и процент')
    remove_old_tint = models.BooleanField('Снять старую тонировку', default=False)
    armor_package = models.ForeignKey('services.ArmorPackage', on_delete=models.SET_NULL,
                                      null=True, blank=True, verbose_name='Пакет бронирования')
    booking_date = models.DateField('Дата')
    booking_time = models.TimeField('Время')
    base_price = models.DecimalField('Базовая цена', max_digits=10, decimal_places=2, default=0)
    discount_applied = models.DecimalField('Применённая скидка (%)', max_digits=3, decimal_places=0, default=0)
    final_price = models.DecimalField('Итоговая цена', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)
    admin_note = models.TextField('Заметка администратора', blank=True)

    _notifications_sent = False

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-booking_date', '-booking_time']
        indexes = [
            models.Index(fields=['booking_date', 'booking_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        service = 'Тонировка' if self.service_type == 'tint' else 'Бронирование'
        return f'#{self.id} — {self.client} — {service} — {self.booking_date} {self.booking_time}'

    @property
    def service_name(self):
        return 'Тонировка' if self.service_type == 'tint' else 'Бронирование'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            old_instance = Booking.objects.filter(pk=self.pk).first()
            if old_instance:
                old_status = old_instance.status

        super().save(*args, **kwargs)

        if is_new and not self._notifications_sent:
            self._notifications_sent = True
            notify_client_about_booking(self)
            notify_admin_about_booking(self)
        elif old_status and old_status != self.status and not self._notifications_sent:
            self._notifications_sent = True
            notify_client_about_booking(self)
