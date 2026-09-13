from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserCar

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone', 'first_name', 'last_name',
                    'total_spent_year', 'discount_percent', 'is_active')
    list_filter = ('discount_percent', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('phone', 'telegram_id', 'total_spent_year', 'discount_percent',
                       'agree_personal_data', 'agree_notifications_email', 'agree_notifications_telegram')
        }),
    )

@admin.register(UserCar)
class UserCarAdmin(admin.ModelAdmin):
    list_display = ('user', 'car_model', 'year', 'license_plate', 'is_active', 'created_at')
    list_filter = ('is_active', 'car_model__body_type')
    search_fields = ('user__username', 'user__phone', 'car_model__name', 'license_plate')
    raw_id_fields = ('user', 'car_model')
