from django.core.management.base import BaseCommand
from services.models import (
    BodyType, CarBrand, CarModel,
    TintFilm, FilmTintPercent, TintService,
    ArmorPackage, ArmorElement,
    TintCoefficient, ArmorCoefficient
)

class Command(BaseCommand):
    help = 'Загрузка начальных справочных данных'

    def handle(self, *args, **options):
        self.stdout.write('Загрузка начальных данных...')

        # Типы кузовов
        body_data = [
            ('Седан', 1.00),
            ('Универсал', 1.10),
            ('Хэтчбек', 0.90),
            ('Лифтбек', 1.00),
            ('Купе', 0.95),
            ('Кроссовер', 1.30),
            ('Внедорожник', 1.50),
        ]
        body_types = {}
        for name, coeff in body_data:
            obj, _ = BodyType.objects.get_or_create(name=name, defaults={'coefficient': coeff})
            body_types[name] = obj

        # Коэффициенты тонировки
        tint_coeffs_data = [
            ('Стандарт', 1.00, 'Обычный кузов'),
            ('Сложный кузов', 1.30, 'Изогнутые стёкла, сложный доступ'),
            ('Внедорожник', 1.70, 'Большие стёкла, высокая посадка'),
            ('Минивэн', 1.50, 'Много стёкол, сложная форма'),
        ]
        tint_coeffs = {}
        for name, coeff, desc in tint_coeffs_data:
            obj, _ = TintCoefficient.objects.get_or_create(
                name=name, defaults={'coefficient': coeff, 'description': desc}
            )
            tint_coeffs[name] = obj

        # Коэффициенты бронирования
        armor_coeffs_data = [
            ('Стандарт', 1.00, 'Обычный кузов'),
            ('Сложный кузов', 1.40, 'Много изогнутых элементов'),
            ('Внедорожник', 1.80, 'Большая площадь покрытия'),
            ('Спорткар', 1.60, 'Сложная геометрия кузова'),
        ]
        armor_coeffs = {}
        for name, coeff, desc in armor_coeffs_data:
            obj, _ = ArmorCoefficient.objects.get_or_create(
                name=name, defaults={'coefficient': coeff, 'description': desc}
            )
            armor_coeffs[name] = obj

        # Марки и модели
        brands_data = {
            'Lada': ['Granta', 'Vesta', 'Niva'],
            'Volkswagen': ['Polo', 'Passat', 'Tiguan'],
            'Skoda': ['Octavia', 'Rapid', 'Kodiaq'],
            'Toyota': ['Camry', 'RAV4', 'Corolla'],
            'BMW': ['3 Series', '5 Series', 'X5'],
        }
        for brand_name, models in brands_data.items():
            brand, _ = CarBrand.objects.get_or_create(name=brand_name, defaults={'country': '—'})
            for model_name in models:
                CarModel.objects.get_or_create(
                    brand=brand,
                    name=model_name,
                    defaults={
                        'body_type': body_types.get('Седан'),
                        'tint_coefficient': tint_coeffs.get('Стандарт'),
                        'armor_coefficient': armor_coeffs.get('Стандарт'),
                    }
                )

        # Плёнки
        films_data = [
            {'name': 'Spectroll (Корея)', 'film_type': 'korean', 'country': 'Корея',
             'percents': [5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70]},
            {'name': 'SunControl (США)', 'film_type': 'american', 'country': 'США',
             'percents': [5, 15, 20, 35, 50]},
            {'name': 'Атермальная плёнка', 'film_type': 'athermal', 'country': '—',
             'percents': [80]},
        ]
        for fd in films_data:
            film, _ = TintFilm.objects.get_or_create(
                film_type=fd['film_type'],
                defaults={'name': fd['name'], 'country': fd['country']}
            )
            for pct in fd['percents']:
                FilmTintPercent.objects.get_or_create(film=film, percent=pct)

        # УСЛУГИ ТОНИРОВКИ (новая таблица)
        tint_services_data = [
            ('Задняя полусфера', 'Тонировка задней полусферы', 3000),
            ('Полный круг', 'Тонировка всех стёкол по кругу', 5000),
            ('Лобовое стекло', 'Тонировка лобового стекла', 2500),
            ('Передняя полусфера', 'Тонировка передней полусферы', 3500),
        ]
        for name, desc, price in tint_services_data:
            TintService.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'base_price': price}
            )

        # Пакеты бронирования
        packages_data = [
            ('standard', 'Стандарт', 'Полоса на капот, полоса на крышу, фары', 5000),
            ('standard_plus', 'Стандарт+', 'Капот полностью, полоса на крышу, зона под ручками', 9000),
            ('premium', 'Премиум', 'Капот полностью, полоса на крышу, крылья полностью, зона под ручками, зона погрузки, внутренние пороги', 15000),
            ('premium_plus', 'Премиум+', 'Все зоны Премиум + зеркала и передний бампер', 22000),
        ]
        for ptype, pname, pdesc, pprice in packages_data:
            ArmorPackage.objects.get_or_create(
                package_type=ptype,
                defaults={'name': pname, 'description': pdesc, 'base_price': pprice}
            )

        # Отдельные услуги бронирования
        elements_data = [
            ('Бампер передний', 'Защита переднего бампера', 8000),
            ('Бампер задний', 'Защита заднего бампера', 7000),
            ('Капот', 'Полное покрытие капота', 6000),
            ('Крылья', 'Защита передних крыльев', 5000),
            ('Зеркала', 'Защита зеркал', 2000),
        ]
        for name, desc, price in elements_data:
            ArmorElement.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'base_price': price}
            )

        self.stdout.write(self.style.SUCCESS('Начальные данные успешно загружены!'))
