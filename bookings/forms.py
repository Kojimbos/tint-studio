from django import forms
from .models import Booking
from services.models import TintService, ArmorPackage

class BookingForm(forms.ModelForm):
    service_type = forms.ChoiceField(
        label='Тип услуги',
        choices=Booking.SERVICE_TYPES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='tint'
    )
    tint_service = forms.ModelChoiceField(
        label='Услуга тонировки',
        queryset=TintService.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Выберите услугу',
        required=False
    )
    armor_package = forms.ModelChoiceField(
        label='Пакет бронирования',
        queryset=ArmorPackage.objects.all(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        empty_label=None,
        required=False
    )

    class Meta:
        model = Booking
        fields = ['car', 'service_type', 'tint_service', 'tint_film_percent', 'remove_old_tint',
                  'armor_package', 'booking_date', 'booking_time']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-control'}),
            'tint_film_percent': forms.Select(attrs={'class': 'form-control'}),
            'booking_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'booking-date'}),
            'booking_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'booking-time'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['car'].queryset = user.cars.filter(is_active=True)
        self.fields['car'].empty_label = 'Выберите автомобиль'
        self.fields['remove_old_tint'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['service_type'].choices = Booking.SERVICE_TYPES
        self.fields['tint_film_percent'].required = False
        self.fields['tint_service'].required = False
        self.fields['armor_package'].required = False

    def clean(self):
        cleaned = super().clean()
        service_type = cleaned.get('service_type')

        if service_type == 'tint':
            if not cleaned.get('tint_service'):
                self.add_error('tint_service', 'Выберите услугу тонировки.')
            if not cleaned.get('tint_film_percent'):
                self.add_error('tint_film_percent', 'Выберите плёнку и процент.')
            # Чистим поля бронирования
            cleaned['armor_package'] = None

        elif service_type == 'armor':
            if not cleaned.get('armor_package'):
                self.add_error('armor_package', 'Выберите пакет бронирования.')
            # Чистим поля тонировки
            cleaned['tint_service'] = None
            cleaned['tint_film_percent'] = None
            cleaned['remove_old_tint'] = False

        return cleaned

