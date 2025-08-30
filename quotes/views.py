from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from random import randint
from .models import Quote


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
