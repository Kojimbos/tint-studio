from django.db import models

class BodyType(models.Model):
    name = models.CharField('Название', max_length=50, unique=True)
    coefficient = models.DecimalField(
        'Коэффициент сложности',
        max_digits=4, decimal_places=2, default=1.00,
        help_text='Умножается на базовую цену услуги'
    )

    class Meta:
        verbose_name = 'Тип кузова'
        verbose_name_plural = 'Типы кузовов'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} (×{self.coefficient})'

class CarBrand(models.Model):
    name = models.CharField('Название', max_length=100, unique=True)
    country = models.CharField('Страна', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Марка автомобиля'
        verbose_name_plural = 'Марки автомобилей'
        ordering = ['name']

    def __str__(self):
        return self.name

class TintCoefficient(models.Model):
    """Справочник коэффициентов сложности ТОНИРОВКИ."""
    name = models.CharField('Название коэффициента', max_length=200, unique=True)
    coefficient = models.DecimalField('Значение', max_digits=4, decimal_places=2, default=1.00)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Коэффициент сложности тонировки'
        verbose_name_plural = 'Коэффициенты сложности тонировки'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} (×{self.coefficient})'

class ArmorCoefficient(models.Model):
    """Справочник коэффициентов сложности БРОНИРОВАНИЯ."""
    name = models.CharField('Название коэффициента', max_length=200, unique=True)
    coefficient = models.DecimalField('Значение', max_digits=4, decimal_places=2, default=1.00)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Коэффициент сложности бронирования'
        verbose_name_plural = 'Коэффициенты сложности бронирования'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} (×{self.coefficient})'

class CarModel(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name='models', verbose_name='Марка')
    name = models.CharField('Название', max_length=200)
    body_type = models.ForeignKey(BodyType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Тип кузова')
    tint_coefficient = models.ForeignKey(
        TintCoefficient, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Коэффициент тонировки', related_name='car_models_tint'
    )
    armor_coefficient = models.ForeignKey(
        ArmorCoefficient, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Коэффициент бронирования', related_name='car_models_armor'
    )

    class Meta:
        verbose_name = 'Модель автомобиля'
        verbose_name_plural = 'Модели автомобилей'
        ordering = ['brand__name', 'name']
        unique_together = ('brand', 'name')

    def __str__(self):
        return f'{self.brand.name} {self.name}'

class TintService(models.Model):
    """
    УСЛУГА ТОНИРОВКИ.
    Администратор создаёт услуги: «Задняя полусфера», «Полный круг» и т.п.
    """
    name = models.CharField('Название услуги', max_length=200, unique=True)
    description = models.TextField('Описание', blank=True)
    base_price = models.DecimalField('Базовая цена (₽)', max_digits=10, decimal_places=2)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Услуга тонировки'
        verbose_name_plural = 'Услуги тонировки'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} — {self.base_price} ₽'

class TintFilm(models.Model):
    FILM_CHOICES = [
        ('korean', 'Корейская (Spectroll)'),
        ('american', 'Американская (SunControl)'),
        ('athermal', 'Атермальная'),
    ]
    name = models.CharField('Название', max_length=200)
    film_type = models.CharField('Тип', max_length=20, choices=FILM_CHOICES, unique=True)
    country = models.CharField('Страна', max_length=100, blank=True)
    description = models.TextField('Описание', blank=True)

    # КОЭФФИЦИЕНТ МАТЕРИАЛА (ПЛЁНКИ)
    coefficient = models.DecimalField(
        'Коэффициент стоимости плёнки',
        max_digits=4, decimal_places=2, default=1.00,
        help_text='Умножается на базовую цену тонировки. Например: 1.5 для дорогой плёнки.'
    )

    class Meta:
        verbose_name = 'Плёнка для тонировки'
        verbose_name_plural = 'Плёнки для тонировки'
        ordering = ['film_type']

    def __str__(self):
        return f'{self.name} (×{self.coefficient})'

class FilmTintPercent(models.Model):
    film = models.ForeignKey(TintFilm, on_delete=models.CASCADE, related_name='percents', verbose_name='Плёнка')
    percent = models.PositiveSmallIntegerField('Процент светопропускаемости')

    class Meta:
        verbose_name = 'Процент светопропускаемости плёнки'
        verbose_name_plural = 'Проценты светопропускаемости плёнок'
        unique_together = ('film', 'percent')
        ordering = ['film', 'percent']

    def __str__(self):
        return f'{self.film.name} — {self.percent}%'

class ArmorPackage(models.Model):
    PACKAGE_TYPES = [
        ('standard', 'Стандарт'),
        ('standard_plus', 'Стандарт+'),
        ('premium', 'Премиум'),
        ('premium_plus', 'Премиум+'),
    ]
    name = models.CharField('Название', max_length=200)
    package_type = models.CharField('Тип пакета', max_length=20, choices=PACKAGE_TYPES, unique=True)
    description = models.TextField('Состав пакета')
    base_price = models.DecimalField('Базовая цена (₽)', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Пакет бронирования'
        verbose_name_plural = 'Пакеты бронирования'
        ordering = ['base_price']

    def __str__(self):
        return self.name

class ArmorElement(models.Model):
    """
    Отдельная услуга бронирования элемента: бампер, капот и т.п.
    """
    name = models.CharField('Название элемента', max_length=200, unique=True)
    description = models.TextField('Описание', blank=True)
    base_price = models.DecimalField('Базовая цена (₽)', max_digits=10, decimal_places=2)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Услуга бронирования элемента'
        verbose_name_plural = 'Услуги бронирования элементов'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} — {self.base_price} ₽'
