from django.contrib import admin
from django.utils.html import format_html
from .models import Material, MaterialReceipt, MaterialConsumption

class MaterialReceiptInline(admin.TabularInline):
    model = MaterialReceipt
    extra = 0
    readonly_fields = ('created_at',)

class MaterialConsumptionInline(admin.TabularInline):
    model = MaterialConsumption
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'current_stock', 'min_stock', 'stock_status', 'price_per_unit')
    list_filter = ('unit',)
    search_fields = ('name',)
    inlines = [MaterialReceiptInline, MaterialConsumptionInline]

    def stock_status(self, obj):
        if obj.current_stock <= 0:
            return format_html('<span style="color:red;font-weight:bold;">⚠️ Закончился</span>')
        if obj.is_low_stock:
            return format_html('<span style="color:orange;">Низкий запас</span>')
        return format_html('<span style="color:green;">✓ В норме</span>')
    stock_status.short_description = 'Статус запаса'

@admin.register(MaterialReceipt)
class MaterialReceiptAdmin(admin.ModelAdmin):
    list_display = ('material', 'quantity', 'price_total', 'supplier', 'created_at')
    list_filter = ('material', 'created_at')
    search_fields = ('material__name', 'supplier')
    date_hierarchy = 'created_at'

@admin.register(MaterialConsumption)
class MaterialConsumptionAdmin(admin.ModelAdmin):
    list_display = ('material', 'quantity', 'booking_link', 'created_at')
    list_filter = ('material', 'created_at')
    search_fields = ('material__name',)
    date_hierarchy = 'created_at'

    def booking_link(self, obj):
        if obj.booking:
            return format_html('<a href="/admin/bookings/booking/{}/change/">Запись #{}</a>',
                               obj.booking_id, obj.booking_id)
        return '—'
    booking_link.short_description = 'Запись'
