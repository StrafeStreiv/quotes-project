from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Source, Quote, SourceType
from .forms import QuoteForm
import json


class BaseTestCase(TestCase):
    """Базовый класс для тестов с общими настройками"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()

        # Создаем тестовые источники
        self.source_movie = Source.objects.create(
            title="Тестовый фильм",
            type=SourceType.MOVIE,
            quote_count=0
        )

        self.source_book = Source.objects.create(
            title="Тестовая книга",
            type=SourceType.BOOK,
            quote_count=0
        )

        # Создаем тестовые цитаты
        self.quote1 = Quote.objects.create(
            text="Первая тестовая цитата",
            source=self.source_movie,
            weight=5,
            views=10,
            likes=3,
            dislikes=1
        )

        self.quote2 = Quote.objects.create(
            text="Вторая тестовая цитата",
            source=self.source_book,
            weight=3,
            views=5,
            likes=7,
            dislikes=2
        )


class ModelTests(BaseTestCase):
    """Тесты моделей"""

    def test_source_creation(self):
        """Тест создания источника"""
        source = Source.objects.get(title="Тестовый фильм")
        self.assertEqual(source.type, SourceType.MOVIE)
        self.assertEqual(source.quote_count, 1)
        self.assertEqual(str(source), "Фильм: Тестовый фильм")
        self.assertEqual(source.get_type_display(), "Фильм")

    def test_quote_creation(self):
        """Тест создания цитаты"""
        quote = Quote.objects.get(text="Первая тестовая цитата")
        self.assertEqual(quote.source, self.source_movie)
        self.assertEqual(quote.weight, 5)
        self.assertEqual(quote.views, 10)
        self.assertTrue(quote.created_at is not None)

    def test_quote_str_representation(self):
        """Тест строкового представления цитаты"""
        quote = Quote.objects.get(text="Первая тестовая цитата")
        self.assertIn("Первая тестовая цитата", str(quote))
        self.assertIn("Тестовый фильм", str(quote))

    def test_duplicate_quote_validation(self):
        """Тест валидации дубликатов цитат"""
        # Пытаемся создать дубликат
        with self.assertRaises(ValidationError):
            quote = Quote(
                text="Первая тестовая цитата",  # Тот же текст
                source=self.source_movie,  # Тот же источник
                weight=2
            )
            quote.full_clean()  # Вызываем валидацию

    def test_source_quote_limit_validation(self):
        """Тест ограничения в 3 цитаты на источник"""
        # Добавляем еще 2 цитаты к источнику (уже есть 1)
        Quote.objects.create(text="Цитата 2", source=self.source_movie, weight=1)
        Quote.objects.create(text="Цитата 3", source=self.source_movie, weight=1)

        # Обновляем счетчик источника
        self.source_movie.refresh_from_db()

        # Пытаемся добавить 4-ю цитату
        with self.assertRaises(ValidationError) as context:
            quote = Quote(text="Цитата 4", source=self.source_movie, weight=1)
            quote.full_clean()

        # Проверяем, что ошибка именно про лимит цитат
        self.assertIn('цитат', str(context.exception))


class ViewTests(BaseTestCase):
    """Тесты представлений"""

    def test_index_view(self):
        """Тест главной страницы"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quotes/index.html')
        self.assertIn('quote', response.context)

    def test_index_view_increases_views(self):
        """Тест увеличения счетчика просмотров"""
        initial_views = self.quote1.views
        self.client.get(reverse('index'))
        self.quote1.refresh_from_db()
        self.assertEqual(self.quote1.views, initial_views + 1)

    def test_popular_view(self):
        """Тест страницы популярных цитат"""
        response = self.client.get(reverse('popular_quotes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quotes/popular.html')
        self.assertIn('top_quotes', response.context)
        self.assertEqual(len(response.context['top_quotes']), 2)

    def test_dashboard_view(self):
        """Тест дашборда"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quotes/dashboard.html')
        self.assertIn('total_quotes', response.context)
        self.assertEqual(response.context['total_quotes'], 2)

    def test_about_view(self):
        """Тест страницы 'О проекте'"""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quotes/about.html')

    def test_add_quote_view_get(self):
        """Тест GET запроса к форме добавления"""
        response = self.client.get(reverse('add_quote'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quotes/add_quote.html')
        self.assertIsInstance(response.context['form'], QuoteForm)


class FormTests(BaseTestCase):
    """Тесты форм"""

    def test_quote_form_valid(self):
        """Тест валидной формы"""
        form_data = {
            'text': 'Новая тестовая цитата',
            'source': self.source_book.id,
            'weight': 2
        }
        form = QuoteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_quote_form_invalid_weight(self):
        """Тест невалидного веса"""
        form_data = {
            'text': 'Новая цитата',
            'source': self.source_book.id,
            'weight': 0  # Невалидный вес
        }
        form = QuoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('weight', form.errors)

    def test_quote_form_new_source(self):
        """Тест формы с новым источником"""
        form_data = {
            'text': 'Цитата из нового источника',
            'new_source_title': 'Новый тестовый источник',
            'new_source_type': SourceType.MOVIE,
            'weight': 1
        }
        form = QuoteForm(data=form_data)

        # Форма должна быть валидной
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

        # Сохраняем форму - источник должен создаться автоматически
        quote = form.save()
        self.assertEqual(quote.source.title, 'Новый тестовый источник')
        self.assertEqual(quote.source.type, SourceType.MOVIE)


class APITests(BaseTestCase):
    """Тесты API endpoints"""

    def test_like_quote(self):
        """Тест лайка цитаты"""
        initial_likes = self.quote1.likes
        response = self.client.post(
            reverse('like_quote', args=[self.quote1.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

        # Проверяем, что лайки увеличились
        self.quote1.refresh_from_db()
        self.assertEqual(self.quote1.likes, initial_likes + 1)

        # Проверяем JSON response
        response_data = json.loads(response.content)
        self.assertEqual(response_data['likes'], initial_likes + 1)

    def test_dislike_quote(self):
        """Тест дизлайка цитаты"""
        initial_dislikes = self.quote1.dislikes
        response = self.client.post(
            reverse('dislike_quote', args=[self.quote1.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

        self.quote1.refresh_from_db()
        self.assertEqual(self.quote1.dislikes, initial_dislikes + 1)


class EdgeCaseTests(TestCase):
    """Тесты граничных случаев"""

    def test_empty_database(self):
        """Тест пустой базы данных"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['quote'])

    def test_nonexistent_page(self):
        """Тест несуществующей страницы"""
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)

    def test_weighted_random_selection(self):
        """Тест взвешенного случайного выбора"""
        # Создаем источники и цитаты с разными весами
        source = Source.objects.create(title="Test Source", type=SourceType.MOVIE)

        # Цитата с весом 10 должна появляться чаще
        high_weight_quote = Quote.objects.create(
            text="High weight quote",
            source=source,
            weight=10
        )

        low_weight_quote = Quote.objects.create(
            text="Low weight quote",
            source=source,
            weight=1
        )

        # Многократный вызов для проверки распределения
        from .views import get_random_quote
        quotes = []
        for _ in range(100):
            quotes.append(get_random_quote())

        # High weight quote должна появляться значительно чаще
        high_weight_count = quotes.count(high_weight_quote)
        low_weight_count = quotes.count(low_weight_quote)

        self.assertGreater(high_weight_count, low_weight_count)
        self.assertGreater(high_weight_count, 50)  # Должна быть больше половины