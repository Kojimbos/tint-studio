import requests
from django.core.mail import send_mail
from django.conf import settings

STUDIO_PHONE = '+7 (992) 148-03-93'

def send_telegram_notification(chat_id, message):
    """Отправляет сообщение в Telegram через бота."""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or not chat_id:
        return False
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    try:
        response = requests.post(url, json={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }, timeout=10)
        return response.ok
    except Exception:
        return False

def send_email_notification(to_email, subject, message):
    """Отправляет email-уведомление."""
    if not to_email:
        return False
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False

def notify_client_about_booking(booking):
    """Уведомление клиента о создании/изменении записи."""
    client = booking.client
    msg = (
        f'📋 Запись №{booking.id}\n'
        f'Услуга: {booking.service_name}\n'
        f'Дата: {booking.booking_date}\n'
        f'Время: {booking.booking_time}\n'
        f'Цена: {booking.final_price} ₽\n'
        f'Статус: {booking.get_status_display()}\n'
    )
    if booking.remove_old_tint:
        msg += (
            f'\n⚠️ Вы выбрали снятие старой плёнки.\n'
            f'Цена и гарантия обсуждаются индивидуально — '
            f'мы свяжемся с вами или уточним при встрече.\n'
        )
    msg += (
        f'\nСтудия тонировки и бронирования\n'
        f'Телефон: {STUDIO_PHONE}'
    )

    if client.email and client.agree_notifications_email:
        send_email_notification(
            to_email=client.email,
            subject=f'Запись №{booking.id} - {booking.get_status_display()}',
            message=msg
        )
    if client.telegram_id and client.agree_notifications_telegram:
        send_telegram_notification(chat_id=client.telegram_id, message=msg)

def notify_admin_about_booking(booking):
    """Уведомление администратора о новой записи."""
    admin_msg = (
        f'🆕 Новая запись!\n'
        f'Клиент: {booking.client.get_full_name() or booking.client.username}\n'
        f'Телефон: {booking.client.phone or "—"}\n'
        f'Услуга: {booking.service_name}\n'
        f'Дата: {booking.booking_date} в {booking.booking_time}\n'
        f'Цена: {booking.final_price} ₽\n'
        f'Статус: {booking.get_status_display()}'
    )
    if booking.remove_old_tint:
        admin_msg += '\n\n⚠️ ТРЕБУЕТСЯ СНЯТИЕ СТАРОЙ ПЛЁНКИ — уточнить цену с клиентом!'

    admin_email = getattr(settings, 'ADMIN_EMAIL', None)
    if admin_email:
        send_email_notification(
            to_email=admin_email,
            subject=f'Новая запись №{booking.id}',
            message=admin_msg
        )
    admin_chat_id = settings.TELEGRAM_CHAT_ID
    if admin_chat_id:
        send_telegram_notification(chat_id=admin_chat_id, message=admin_msg)

