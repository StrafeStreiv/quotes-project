from django.contrib import admin
from .models import Source, Quote

# Простая регистрация модели Source
admin.site.register(Source)

# Регистрация модели Quote с дополнительными настройками
@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'source', 'weight', 'views', 'likes', 'created_at')
    list_filter = ('source', 'created_at')
    search_fields = ('text', 'source__title')
    list_editable = ('weight',)

    # Вспомогательный метод для отображения укороченного текста цитаты
    def text_short(self, obj):
        return f'"{obj.text[:50]}..."' if len(obj.text) > 50 else f'"{obj.text}"'
    text_short.short_description = 'Текст цитаты'