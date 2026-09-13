from django.db import models
from django.core.exceptions import ValidationError

class Material(models.Model):
    UNIT_CHOICES = [
        ('meter', 'Метр'),
        ('roll', 'Рулон'),
        ('piece', 'Штука'),
        ('liter', 'Литр'),
    ]
    name = models.CharField('Название', max_length=200)
    unit = models.CharField('Единица измерения', max_length=20, choices=UNIT_CHOICES, default='meter')
    current_stock = models.DecimalField('Текущий остаток', max_digits=10, decimal_places=2, default=0)
    min_stock = models.DecimalField('Минимальный запас', max_digits=10, decimal_places=2, default=0)
    price_per_unit = models.DecimalField('Цена за единицу (₽)', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Добавлен', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_unit_display()}) — {self.current_stock}'

    @property
    def is_low_stock(self):
        return self.current_stock <= self.min_stock

class MaterialReceipt(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='receipts', verbose_name='Материал')
    quantity = models.DecimalField('Количество', max_digits=10, decimal_places=2)
    price_total = models.DecimalField('Общая стоимость (₽)', max_digits=10, decimal_places=2, default=0)
    supplier = models.CharField('Поставщик', max_length=200, blank=True)
    note = models.TextField('Примечание', blank=True)
    created_at = models.DateTimeField('Дата прихода', auto_now_add=True)

    class Meta:
        verbose_name = 'Приход материала'
        verbose_name_plural = 'Приходы материалов'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.material.current_stock += self.quantity
            self.material.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Приход: {self.material.name} +{self.quantity} ({self.created_at:%d.%m.%Y})'

class MaterialConsumption(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='consumptions', verbose_name='Материал')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='consumptions', verbose_name='Связанная запись')
    quantity = models.DecimalField('Количество', max_digits=10, decimal_places=2)
    note = models.TextField('Примечание', blank=True)
    created_at = models.DateTimeField('Дата списания', auto_now_add=True)

    class Meta:
        verbose_name = 'Расход материала'
        verbose_name_plural = 'Расходы материалов'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            if self.quantity > self.material.current_stock:
                raise ValidationError(f'Недостаточно материала "{self.material.name}". '
                                      f'Доступно: {self.material.current_stock}, запрошено: {self.quantity}')
            self.material.current_stock -= self.quantity
            self.material.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Расход: {self.material.name} -{self.quantity} ({self.created_at:%d.%m.%Y})'
