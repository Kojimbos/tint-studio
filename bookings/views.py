import json
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Booking
from .forms import BookingForm
from services.models import TintService, ArmorPackage, ArmorElement, FilmTintPercent, TintFilm

@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.client = request.user
            booking.discount_applied = request.user.discount_percent
            booking.base_price = _calculate_price(booking)
            if booking.discount_applied > 0:
                booking.final_price = booking.base_price * (1 - booking.discount_applied / 100)
            else:
                booking.final_price = booking.base_price
            booking.save()

            # Если выбрано снятие старой плёнки — предупреждаем клиента в сообщении
            if booking.remove_old_tint:
                messages.warning(request,
                    f'⚠️ Заявка на снятие старой плёнки принята. '
                    f'Цена и гарантия будут уточнены по телефону +7 (992) 148-03-93 или при встрече.'
                )

            messages.success(request,
                f'Запись создана! Дата: {booking.booking_date}, время: {booking.booking_time}. '
                f'Предварительная стоимость: {booking.final_price:.0f} ₽'
            )
            return redirect('booking_history')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = BookingForm(user=request.user)

    films = TintFilm.objects.prefetch_related('percents').all()
    films_json = []
    for film in films:
        films_json.append({
            'id': film.id,
            'name': film.name,
            'film_type': film.film_type,
            'coefficient': float(film.coefficient),
            'percents': [{'id': p.id, 'percent': p.percent} for p in film.percents.all()]
        })

    tint_services = TintService.objects.filter(is_active=True)
    tint_services_json = [
        {'id': s.id, 'name': s.name, 'base_price': float(s.base_price)}
        for s in tint_services
    ]

    packages = ArmorPackage.objects.all()
    packages_json = [
        {'id': p.id, 'name': p.name, 'package_type': p.package_type, 'base_price': float(p.base_price)}
        for p in packages
    ]

    cars_data = []
    for car in request.user.cars.filter(is_active=True).select_related(
            'car_model', 'car_model__body_type',
            'car_model__tint_coefficient', 'car_model__armor_coefficient'):
        cm = car.car_model
        cars_data.append({
            'id': car.id,
            'name': str(cm),
            'car_model_id': cm.id,
            'body_type_id': cm.body_type_id,
            'tint_coefficient': float(cm.tint_coefficient.coefficient) if cm.tint_coefficient else 1.0,
            'armor_coefficient': float(cm.armor_coefficient.coefficient) if cm.armor_coefficient else 1.0,
            'body_coefficient': float(cm.body_type.coefficient) if cm.body_type else 1.0,
        })

    context = {
        'form': form,
        'films_json': json.dumps(films_json, ensure_ascii=False),
        'tint_services_json': json.dumps(tint_services_json, ensure_ascii=False),
        'packages_json': json.dumps(packages_json, ensure_ascii=False),
        'cars_json': json.dumps(cars_data, ensure_ascii=False),
        'user_discount': request.user.discount_percent,
    }
    return render(request, 'bookings/create.html', context)

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.client != request.user and not request.user.is_staff:
        messages.error(request, 'Доступ запрещён.')
        return redirect('profile')
    return render(request, 'bookings/detail.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, client=request.user)
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Запись отменена.')
    else:
        messages.error(request, 'Невозможно отменить эту запись.')
    return redirect('booking_history')

@login_required
def get_available_slots(request):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Дата не указана'}, status=400)

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Неверный формат даты'}, status=400)

    if date < timezone.now().date():
        return JsonResponse({'error': 'Нельзя выбрать прошедшую дату', 'slots': []})

    booked = Booking.objects.filter(booking_date=date).exclude(status='cancelled').values_list('booking_time', flat=True)
    booked_times = [t.strftime('%H:%M') for t in booked]

    all_slots = []
    hour = 9
    while hour < 19:
        t = f'{hour:02d}:00'
        all_slots.append({'time': t, 'available': t not in booked_times})
        hour += 1

    return JsonResponse({'date': date_str, 'slots': all_slots})

def _calculate_price(booking):
    """
    Предварительная цена (без снятия старой плёнки):
      Тонировка:    base_price(TintService) × коэф_модели × коэф_кузова × коэф_плёнки
      Бронирование: base_price(ArmorPackage) × коэф_модели × коэф_кузова

    ⚠️ Снятие старой плёнки в расчёт НЕ входит — цена и гарантия обсуждаются
       индивидуально по телефону или при встрече.
    """
    car = booking.car
    if not car:
        return 0
    car_model = car.car_model
    if not car_model:
        return 0

    if booking.service_type == 'tint':
        if not booking.tint_service:
            return 0
        model_coefficient = float(car_model.tint_coefficient.coefficient) if car_model.tint_coefficient else 1.0
        body_coefficient = float(car_model.body_type.coefficient) if car_model.body_type else 1.0
        film_coefficient = 1.0
        if booking.tint_film_percent and booking.tint_film_percent.film:
            film_coefficient = float(booking.tint_film_percent.film.coefficient)

        return float(booking.tint_service.base_price) * model_coefficient * body_coefficient * film_coefficient

    if booking.service_type == 'armor':
        if not booking.armor_package:
            return 0
        model_coefficient = float(car_model.armor_coefficient.coefficient) if car_model.armor_coefficient else 1.0
        body_coefficient = float(car_model.body_type.coefficient) if car_model.body_type else 1.0
        return float(booking.armor_package.base_price) * model_coefficient * body_coefficient

    return 0

