from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse


class SourceType(models.TextChoices):
    MOVIE = 'movie', 'Фильм'
    BOOK = 'book', 'Книга'
    SERIES = 'series', 'Сериал'
    GAME = 'game', 'Игра'
    OTHER = 'other', 'Другое'


class Source(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название источника")

    type = models.CharField(
        max_length=10,
        choices=SourceType.choices,
        default=SourceType.MOVIE,
        verbose_name="Тип источника"
    )

    # Счетчик цитат. Нужен для проверки ограничения "не больше 3 цитат на источник".
    quote_count = models.PositiveIntegerField(default=0, verbose_name="Количество цитат")

    class Meta:
        verbose_name = "Источник"
        verbose_name_plural = "Источники"

    def __str__(self):
        return f"{self.get_type_display()}: {self.title}"

    def can_add_quote(self):
        return self.quote_count < 3


class Quote(models.Model):
    text = models.TextField(verbose_name="Текст цитаты")

    # on_delete=models.CASCADE означает, что при удалении источника все его цитаты тоже удалятся.
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        related_name='quotes',  # Позволит обращаться к цитатам источника через source.quotes.all()
        verbose_name="Источник"
    )


    weight = models.PositiveIntegerField(
        default=1,
        verbose_name="Вес",
        help_text="Чем выше вес, тем больше шанс показа цитаты. Минимальное значение: 1"
    )

    # Счетчики
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    likes = models.PositiveIntegerField(default=0, verbose_name="Лайки")
    dislikes = models.PositiveIntegerField(default=0, verbose_name="Дизлайки")


    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Цитата"
        verbose_name_plural = "Цитаты"
        # Запрещаем дубликаты: не может быть двух цитат с одинаковым текстом И источником
        unique_together = ['text', 'source']

    def __str__(self):
        # Берем первые 50 символов цитаты для отображения
        return f'"{self.text[:50]}..." из {self.source}'


    def clean(self):
        if not self.pk and self.source.quote_count >= 3:
            raise ValidationError(
                f'Нельзя добавить более 3 цитат для одного источника. '
                f'У источника "{self.source}" уже {self.source.quote_count} цитат(ы).'
            )

        if self.weight < 1:
            raise ValidationError({'weight': 'Вес не может быть меньше 1.'})

    def save(self, *args, **kwargs):
        is_new = not self.pk


        self.full_clean()


        super().save(*args, **kwargs)


        if is_new:
            Source.objects.filter(pk=self.source_id).update(quote_count=models.F('quote_count') + 1)


    def get_absolute_url(self):
        return reverse('quote_detail', kwargs={'pk': self.pk})
