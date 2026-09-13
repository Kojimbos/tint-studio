from django.contrib import admin
from django.utils.html import format_html
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_link', 'service_type_display', 'car_info',
                    'booking_date', 'booking_time', 'final_price', 'status_display')
    list_filter = ('status', 'service_type', 'booking_date')
    search_fields = ('client__username', 'client__phone', 'client__email', 'car__license_plate')
    date_hierarchy = 'booking_date'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Клиент и автомобиль', {'fields': ('client', 'car')}),
        ('Услуга', {'fields': ('service_type', 'tint_film_percent', 'remove_old_tint', 'armor_package')}),
        ('Дата и время', {'fields': ('booking_date', 'booking_time')}),
        ('Цена', {'fields': ('base_price', 'discount_applied', 'final_price')}),
        ('Статус', {'fields': ('status', 'admin_note')}),
        ('Служебное', {'fields': ('created_at', 'updated_at')}),
    )
    actions = ['mark_completed', 'mark_cancelled']

    def client_link(self, obj):
        return format_html('<a href="/admin/accounts/user/{}/change/">{}</a>', obj.client_id, obj.client)
    client_link.short_description = 'Клиент'

    def service_type_display(self, obj):
        return 'Тонировка' if obj.service_type == 'tint' else 'Бронирование'
    service_type_display.short_description = 'Услуга'

    def car_info(self, obj):
        return str(obj.car) if obj.car else '—'
    car_info.short_description = 'Автомобиль'

    def status_display(self, obj):
        colors = {'pending': 'orange', 'confirmed': 'blue', 'completed': 'green', 'cancelled': 'red'}
        return format_html('<span style="color:{};font-weight:bold;">{}</span>',
                           colors.get(obj.status, 'black'), obj.get_status_display())
    status_display.short_description = 'Статус'

    @admin.action(description='Отметить как выполненные')
    def mark_completed(self, request, queryset):
        for booking in queryset:
            if booking.status not in ['completed', 'cancelled']:
                booking.status = 'completed'
                booking.save()
                client = booking.client
                client.total_spent_year += booking.final_price
                client.save()
                client.recalculate_discount()
        self.message_user(request, f'Отмечено выполненных: {queryset.count()}')

    @admin.action(description='Отменить записи')
    def mark_cancelled(self, request, queryset):
        updated = queryset.exclude(status__in=['completed', 'cancelled']).update(status='cancelled')
        self.message_user(request, f'Отменено записей: {updated}')
