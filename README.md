# Веб-сервис студии тонировки и бронирования автомобилей

## Быстрый старт на Windows

1. Убедись, что установлен Python 3.10+ (при установке галочка "Add Python to PATH").
2. Распакуй папку tint_studio на Рабочий стол.
3. Открой Командную строку (Win+R → cmd) и выполни:

cd C:\Users\ВАШ_ПОЛЬЗОВАТЕЛЬ\Desktop\tint_studio
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py load_initial_data
python manage.py createsuperuser
python manage.py runserver

4. Сайт: http://127.0.0.1:8000/
5. Админка: http://127.0.0.1:8000/admin/

## Структура проекта
- config/ — настройки Django
- accounts/ — пользователи, личный кабинет, автомобили
- services/ — справочники, цены, пакеты
- bookings/ — записи на услуги
- inventory/ — складской учёт
- templates/ — HTML-шаблоны
- static/ — CSS и JS
- utils/ — отправка уведомлений

## Телефон студии
89921480393
