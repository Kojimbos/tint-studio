from django import forms
from .models import Booking
from services.models import ArmorPackage

class BookingForm(forms.ModelForm):
    service_type = forms.ChoiceField(
        label='Тип услуги',
        choices=Booking.SERVICE_TYPES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='tint'
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
        fields = ['car', 'service_type', 'tint_film_percent', 'remove_old_tint',
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
        self.fields['remove_old_tint'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['service_type'].choices = Booking.SERVICE_TYPES
