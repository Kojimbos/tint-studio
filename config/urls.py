from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

admin.site.site_header = "Управление студией тонировки"
admin.site.site_title = "Админка"
admin.site.index_title = "Панель управления"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('services/', include('services.urls')),
    path('bookings/', include('bookings.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
