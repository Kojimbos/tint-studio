from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, UserCar

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label='Email', required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}))
    phone = forms.CharField(label='Телефон', max_length=20, required=True,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'}))
    first_name = forms.CharField(label='Имя', max_length=30, required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    telegram_id = forms.CharField(label='Telegram ID (необязательно)', max_length=50, required=False,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username или числовой ID'}))
    agree_personal_data = forms.BooleanField(label='Я согласен на обработку персональных данных', required=True,
                                             widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    agree_notifications_email = forms.BooleanField(label='Согласен получать уведомления на email', required=False,
                                                   widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    agree_notifications_telegram = forms.BooleanField(label='Согласен получать уведомления в Telegram', required=False,
                                                      widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    website = forms.CharField(required=False, widget=forms.HiddenInput(), label='')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'phone', 'telegram_id',
                  'password1', 'password2',
                  'agree_personal_data', 'agree_notifications_email', 'agree_notifications_telegram',
                  'website')
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_website(self):
        website = self.cleaned_data.get('website', '')
        if website:
            raise forms.ValidationError('Бот обнаружен.')
        return website

class LoginForm(AuthenticationForm):
    """Форма входа."""
    username = forms.CharField(label='Логин или Email',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Логин или email'}))
    password = forms.CharField(label='Пароль',
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Логин или email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'telegram_id',
                  'agree_notifications_email', 'agree_notifications_telegram')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'telegram_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '@username или числовой ID'}),
            'agree_notifications_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'agree_notifications_telegram': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserCarForm(forms.ModelForm):
    class Meta:
        model = UserCar
        fields = ('car_model', 'year', 'license_plate')
        widgets = {
            'car_model': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2024'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'А123БВ 777'}),
        }
