from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import User, UserCar
from .forms import SignUpForm, LoginForm, UserUpdateForm, UserCarForm

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Регистрация успешна! Добро пожаловать.')
        return response

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'С возвращением, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный логин или пароль.')
        else:
            messages.error(request, 'Проверьте правильность заполнения формы.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')

@login_required
def profile_view(request):
    user = request.user
    cars = user.cars.filter(is_active=True)
    bookings = user.bookings.all().order_by('-booking_date', '-booking_time')[:10]

    context = {
        'user': user,
        'cars': cars,
        'bookings': bookings,
        'car_form': UserCarForm(),
        'profile_form': UserUpdateForm(instance=user),
        'discount_info': {
            'total_spent': user.total_spent_year,
            'discount': user.discount_percent,
            'next_threshold': _get_next_threshold(user.total_spent_year),
        }
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('profile')
    return redirect('profile')

@login_required
def add_car(request):
    if request.method == 'POST':
        form = UserCarForm(request.POST)
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            car.save()
            messages.success(request, 'Автомобиль добавлен.')
    return redirect('profile')

@login_required
def delete_car(request, car_id):
    car = get_object_or_404(UserCar, id=car_id, user=request.user)
    car.is_active = False
    car.save()
    messages.success(request, 'Автомобиль удалён.')
    return redirect('profile')

@login_required
def booking_history(request):
    bookings = request.user.bookings.all().order_by('-booking_date', '-booking_time')
    return render(request, 'accounts/booking_history.html', {'bookings': bookings})

def _get_next_threshold(total):
    if total < 10000:
        return {'next_percent': 5, 'need': 10000 - total, 'threshold': 10000}
    elif total < 50000:
        return {'next_percent': 10, 'need': 50000 - total, 'threshold': 50000}
    elif total < 100000:
        return {'next_percent': 15, 'need': 100000 - total, 'threshold': 100000}
    return None
