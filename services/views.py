from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import (
    TintFilm, FilmTintPercent, TintService, ArmorPackage,
    ArmorCoefficient, BodyType, CarModel, ArmorElement
)

def price_list(request):
    films = TintFilm.objects.prefetch_related('percents').all()
    packages = ArmorPackage.objects.all()
    elements = ArmorElement.objects.filter(is_active=True)
    tint_services = TintService.objects.filter(is_active=True)
    body_types = BodyType.objects.all()
    context = {
        'films': films,
        'packages': packages,
        'elements': elements,
        'tint_services': tint_services,
        'body_types': body_types,
    }
    return render(request, 'services/price_list.html', context)

@login_required
def calculate_tint_price(request):
    """
    Расчёт тонировки:
    итог = базовая_цена_услуги × коэффициент_модели × коэффициент_кузова × коэффициент_плёнки.
    """
    try:
        car_model_id = request.GET.get('car_model_id')
        tint_service_id = request.GET.get('tint_service_id')
        film_id = request.GET.get('film_id')

        if not all([car_model_id, tint_service_id, film_id]):
            return JsonResponse({'error': 'Не все параметры переданы'}, status=400)

        car_model = CarModel.objects.select_related('tint_coefficient', 'body_type').filter(id=car_model_id).first()
        if not car_model:
            return JsonResponse({'error': 'Автомобиль не найден'}, status=400)

        service = TintService.objects.filter(id=tint_service_id, is_active=True).first()
        if not service:
            return JsonResponse({'error': 'Услуга не найдена'}, status=400)

        film = TintFilm.objects.filter(id=film_id).first()
        if not film:
            return JsonResponse({'error': 'Плёнка не найдена'}, status=400)

        model_coefficient = 1.00
        if car_model.tint_coefficient:
            model_coefficient = float(car_model.tint_coefficient.coefficient)

        body_coefficient = 1.00
        if car_model.body_type:
            body_coefficient = float(car_model.body_type.coefficient)

        film_coefficient = float(film.coefficient or 1.00)

        total_coefficient = model_coefficient * body_coefficient * film_coefficient
        total = service.base_price * total_coefficient

        return JsonResponse({
            'base_price': float(service.base_price),
            'model_coefficient': model_coefficient,
            'body_coefficient': body_coefficient,
            'film_coefficient': film_coefficient,
            'total': float(total),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def calculate_armor_price(request):
    """
    Расчёт бронирования пакетом:
    итог = базовая_цена_пакета × коэффициент_модели × коэффициент_кузова.
    """
    try:
        car_model_id = request.GET.get('car_model_id')
        package_id = request.GET.get('package_id')

        if not all([car_model_id, package_id]):
            return JsonResponse({'error': 'Не все параметры переданы'}, status=400)

        car_model = CarModel.objects.select_related('armor_coefficient', 'body_type').filter(id=car_model_id).first()
        if not car_model:
            return JsonResponse({'error': 'Автомобиль не найден'}, status=400)

        package = get_object_or_404(ArmorPackage, id=package_id)

        model_coefficient = 1.00
        if car_model.armor_coefficient:
            model_coefficient = float(car_model.armor_coefficient.coefficient)

        body_coefficient = 1.00
        if car_model.body_type:
            body_coefficient = float(car_model.body_type.coefficient)

        total_coefficient = model_coefficient * body_coefficient
        total = package.base_price * total_coefficient

        return JsonResponse({
            'base_price': float(package.base_price),
            'model_coefficient': model_coefficient,
            'body_coefficient': body_coefficient,
            'total': float(total),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def calculate_armor_element_price(request):
    """
    Расчёт бронирования элемента:
    итог = базовая_цена_элемента × коэффициент_модели × коэффициент_кузова.
    """
    try:
        car_model_id = request.GET.get('car_model_id')
        element_id = request.GET.get('element_id')

        if not all([car_model_id, element_id]):
            return JsonResponse({'error': 'Не все параметры переданы'}, status=400)

        car_model = CarModel.objects.select_related('armor_coefficient', 'body_type').filter(id=car_model_id).first()
        if not car_model:
            return JsonResponse({'error': 'Автомобиль не найден'}, status=400)

        element = ArmorElement.objects.filter(id=element_id, is_active=True).first()
        if not element:
            return JsonResponse({'error': 'Услуга не найдена'}, status=400)

        model_coefficient = 1.00
        if car_model.armor_coefficient:
            model_coefficient = float(car_model.armor_coefficient.coefficient)

        body_coefficient = 1.00
        if car_model.body_type:
            body_coefficient = float(car_model.body_type.coefficient)

        total_coefficient = model_coefficient * body_coefficient
        total = element.base_price * total_coefficient

        return JsonResponse({
            'base_price': float(element.base_price),
            'model_coefficient': model_coefficient,
            'body_coefficient': body_coefficient,
            'total': float(total),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_film_percents(request):
    film_id = request.GET.get('film_id')
    if film_id:
        percents = FilmTintPercent.objects.filter(film_id=film_id).values('id', 'percent')
        return JsonResponse(list(percents), safe=False)
    else:
        films = TintFilm.objects.prefetch_related('percents').all()
        data = []
        for film in films:
            data.append({
                'id': film.id,
                'name': film.name,
                'film_type': film.film_type,
                'coefficient': float(film.coefficient),
                'percents': [{'id': p.id, 'percent': p.percent} for p in film.percents.all()]
            })
        return JsonResponse(data, safe=False)

@login_required
def get_tint_services(request):
    services = TintService.objects.filter(is_active=True).values('id', 'name', 'base_price')
    return JsonResponse(list(services), safe=False)

@login_required
def get_armor_elements(request):
    elements = ArmorElement.objects.filter(is_active=True).values('id', 'name', 'base_price')
    return JsonResponse(list(elements), safe=False)
