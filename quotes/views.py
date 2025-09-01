from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Sum, F, Count
from django.contrib import messages
from random import randint
from .models import Quote, Source
from .forms import QuoteForm
from django.utils import timezone
from datetime import timedelta

def get_random_quote():
    quotes = Quote.objects.filter(weight__gte=1)
    if not quotes.exists():
        return None

    total_weight = quotes.aggregate(Sum('weight'))['weight__sum']

    random_num = randint(1, total_weight)

    current_weight = 0
    for quote in quotes:
        current_weight += quote.weight
        if random_num <= current_weight:
            return quote


def index(request):
    random_quote = get_random_quote()

    if random_quote:
        random_quote.views += 1
        random_quote.save()

    context = {'quote': random_quote}
    return render(request, 'quotes/index.html', context)


def add_quote(request):
    """Страница добавления новой цитаты"""
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save()
            messages.success(request, 'Цитата успешно добавлена!')
            return redirect('index')
    else:
        form = QuoteForm()

    return render(request, 'quotes/add_quote.html', {'form': form})


def like_quote(request, quote_id):
    """Обработчик лайка (AJAX)"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            quote = get_object_or_404(Quote, id=quote_id)
            quote.likes += 1
            quote.save()

            # Получаем следующую случайную цитату
            next_quote = get_random_quote()
            if next_quote:
                next_quote.views += 1
                next_quote.save()

            return JsonResponse({
                'likes': quote.likes,
                'dislikes': quote.dislikes,
                'status': 'success',
                'next_quote_id': next_quote.id if next_quote else None,
                'next_quote_text': next_quote.text if next_quote else None,
                'next_quote_source': str(next_quote.source) if next_quote else None,
                'next_quote_views': next_quote.views if next_quote else 0,
                'next_quote_likes': next_quote.likes if next_quote else 0,
                'next_quote_dislikes': next_quote.dislikes if next_quote else 0,
                'next_quote_weight': next_quote.weight if next_quote else 1,
            })
        except Exception as e:
            return JsonResponse({'error': str(e), 'status': 'error'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)


def dislike_quote(request, quote_id):
    """Обработчик дизлайка (AJAX)"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            quote = get_object_or_404(Quote, id=quote_id)
            quote.dislikes += 1
            quote.save()

            # Получаем следующую случайную цитату
            next_quote = get_random_quote()
            if next_quote:
                next_quote.views += 1
                next_quote.save()

            return JsonResponse({
                'likes': quote.likes,
                'dislikes': quote.dislikes,
                'status': 'success',
                'next_quote_id': next_quote.id if next_quote else None,
                'next_quote_text': next_quote.text if next_quote else None,
                'next_quote_source': str(next_quote.source) if next_quote else None,
                'next_quote_views': next_quote.views if next_quote else 0,
                'next_quote_likes': next_quote.likes if next_quote else 0,
                'next_quote_dislikes': next_quote.dislikes if next_quote else 0,
                'next_quote_weight': next_quote.weight if next_quote else 1,
            })
        except Exception as e:
            return JsonResponse({'error': str(e), 'status': 'error'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)


def popular_quotes(request):
    """Страница с популярными цитатами"""
    top_quotes = Quote.objects.annotate(
        popularity=F('likes') - F('dislikes')
    ).order_by('-popularity', '-created_at')[:10]

    # Дополнительные выборки
    most_viewed = Quote.objects.order_by('-views')[:5]
    recent_quotes = Quote.objects.order_by('-created_at')[:5]

    context = {
        'top_quotes': top_quotes,
        'most_viewed': most_viewed,
        'recent_quotes': recent_quotes,
        'active_tab': 'popular'
    }
    return render(request, 'quotes/popular.html', context)


def dashboard(request):
    """Дашборд со статистикой"""
    total_quotes = Quote.objects.count()
    total_sources = Source.objects.count()
    total_views = Quote.objects.aggregate(Sum('views'))['views__sum'] or 0
    total_likes = Quote.objects.aggregate(Sum('likes'))['likes__sum'] or 0

    # Статистика по типам источников
    sources_by_type = Source.objects.values('type').annotate(
        count=Count('id'),
        quote_count=Sum('quote_count')
    ).order_by('-count')

    # Недавняя активность
    last_week = timezone.now() - timedelta(days=7)
    recent_activity = Quote.objects.filter(
        created_at__gte=last_week
    ).order_by('-created_at')[:10]

    # Цитаты с лучшим соотношением лайков/дизлайков
    best_ratio = Quote.objects.annotate(
        ratio=F('likes') / (F('dislikes'))  # +1 чтобы избежать деления на 0
    ).filter(likes__gt=0).order_by('-ratio')[:5]

    context = {
        'total_quotes': total_quotes,
        'total_sources': total_sources,
        'total_views': total_views,
        'total_likes': total_likes,
        'sources_by_type': sources_by_type,
        'recent_activity': recent_activity,
        'best_ratio': best_ratio,
        'active_tab': 'dashboard'
    }
    return render(request, 'quotes/dashboard.html', context)

def about(request):
    """Страница о проекте"""
    context = {
        'active_tab': 'about'
    }
    return render(request, 'quotes/about.html', context)

def handler404(request, exception):
    """Обработчик 404 ошибки"""
    return render(request, 'quotes/404.html', status=404)

def handler500(request):
    """Обработчик 500 ошибки"""
    return render(request, 'quotes/500.html', status=500)

def handler403(request, exception):
    """Обработчик 403 ошибки"""
    return render(request, 'quotes/403.html', status=403)