from django.contrib import admin
from django.urls import path, include  # Импортируем include!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quotes.urls')),  # Подключаем URLs из приложения quotes
]

# Обработчики ошибок
handler404 = 'quotes.views.handler404'
handler500 = 'quotes.views.handler500'
handler403 = 'quotes.views.handler403'