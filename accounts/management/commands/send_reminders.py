from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking
from utils.notifications import send_email_notification, send_telegram_notification

class Command(BaseCommand):
    help = 'Отправляет напоминания клиентам о записях на завтра'

    def handle(self, *args, **options):
        tomorrow = timezone.now().date() + timedelta(days=1)
        bookings = Booking.objects.filter(
            booking_date=tomorrow,
            status__in=['pending', 'confirmed']
        ).select_related('client')

        count = 0
        for booking in bookings:
            client = booking.client
            message = (
                f'🔔 Напоминание!\n'
                f'У вас запись на {booking.booking_date} в {booking.booking_time}.\n'
                f'Услуга: {booking.service_name}\n'
                f'Цена: {booking.final_price} ₽\n'
                f'Статус: {booking.get_status_display()}\n\n'
                f'Студия тонировки и бронирования\n'
                f'Телефон: +7 (999) 214-80-39'
            )
            if client.email and client.agree_notifications_email:
                send_email_notification(client.email, 'Напоминание о записи', message)
                count += 1
            if client.telegram_id and client.agree_notifications_telegram:
                send_telegram_notification(client.telegram_id, message)
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Отправлено напоминаний: {count}'))
