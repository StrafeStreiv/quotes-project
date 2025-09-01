from django.contrib import admin
from .models import Source, Quote





@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    # Поля только для чтения
    readonly_fields = ('quote_count',)
    # Поля в списке
    list_display = ('title', 'type', 'quote_count')
    list_filter = ('type',)
    search_fields = ('title',)


# Регистрация модели Quote с дополнительными настройками
@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'source', 'weight', 'views', 'likes', 'created_at')
    list_filter = ('source', 'created_at')
    search_fields = ('text', 'source__title')
    list_editable = ('weight',)
    readonly_fields = ('views', 'likes', 'dislikes', 'created_at')

    # Вспомогательный метод для отображения укороченного текста цитаты
    def text_short(self, obj):
        return f'"{obj.text[:50]}..."' if len(obj.text) > 50 else f'"{obj.text}"'

    text_short.short_description = 'Текст цитаты'