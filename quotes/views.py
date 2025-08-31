from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Sum, F
from django.contrib import messages
from random import randint
from .models import Quote, Source
from .forms import QuoteForm

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
    if request.method == 'POST':
        quote = get_object_or_404(Quote, id=quote_id)
        quote.likes = F('likes') + 1
        quote.save()
        quote.refresh_from_db()  # Обновляем объект из БД
        return JsonResponse({'likes': quote.likes, 'dislikes': quote.dislikes})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def dislike_quote(request, quote_id):
    """Обработчик дизлайка (AJAX)"""
    if request.method == 'POST':
        quote = get_object_or_404(Quote, id=quote_id)
        quote.dislikes = F('dislikes') + 1
        quote.save()
        quote.refresh_from_db()
        return JsonResponse({'likes': quote.likes, 'dislikes': quote.dislikes})
    return JsonResponse({'error': 'Invalid request'}, status=400)
