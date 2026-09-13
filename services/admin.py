from django.contrib import admin
from .models import (
    BodyType, CarBrand, CarModel,
    TintFilm, FilmTintPercent, TintService,
    ArmorPackage, ArmorElement,
    TintCoefficient, ArmorCoefficient
)

class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 0

class FilmTintPercentInline(admin.TabularInline):
    model = FilmTintPercent
    extra = 1

@admin.register(BodyType)
class BodyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'coefficient')
    search_fields = ('name',)
    list_editable = ('coefficient',)

@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name',)
    inlines = [CarModelInline]

@admin.register(TintCoefficient)
class TintCoefficientAdmin(admin.ModelAdmin):
    list_display = ('name', 'coefficient')
    search_fields = ('name',)
    list_editable = ('coefficient',)

@admin.register(ArmorCoefficient)
class ArmorCoefficientAdmin(admin.ModelAdmin):
    list_display = ('name', 'coefficient')
    search_fields = ('name',)
    list_editable = ('coefficient',)

@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'body_type', 'tint_coefficient', 'armor_coefficient')
    list_filter = ('body_type', 'brand', 'tint_coefficient', 'armor_coefficient')
    search_fields = ('name', 'brand__name')

@admin.register(TintService)
class TintServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('base_price', 'is_active')

@admin.register(TintFilm)
class TintFilmAdmin(admin.ModelAdmin):
    list_display = ('name', 'film_type', 'country', 'coefficient')
    list_editable = ('coefficient',)
    inlines = [FilmTintPercentInline]

@admin.register(ArmorPackage)
class ArmorPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'package_type', 'base_price')

@admin.register(ArmorElement)
class ArmorElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('base_price', 'is_active')
