# Quotes Project

Django веб-приложение для отображения случайных цитат из фильмов и книг с системой рейтингов.

## Возможности

- Случайный показ цитат с учетом веса (вероятности показа)
- Добавление новых цитат через форму с валидацией
- Система лайков/дизлайков (AJAX без перезагрузки)
- Защита от дубликатов цитат
- Ограничение: не более 3 цитат у одного источника
- Страница с топ-10 популярных цитат
- Дашборд со статистикой
- Адаптивный дизайн на Bootstrap 5

## Технологии

- Python 3.9
- Django 4.2
- SQLite
- Bootstrap 5
- JavaScript (AJAX)

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/StrafeStreiv/quotes-project.git
cd quotes-project
```
2.Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate   # Windows
```
3. Установите зависимости
```bash
pip install -r requirements.txt
```
4.Примените миграции
```bash
python manage.py migrate
```
5.Создайте суперпользователя
```bash
python manage.py createsuperuser
```
6.Запустите сервер
```bash
python manage.py runserver
```
7.Откройте в браузере:
http://127.0.0.1:8000 - главная страница
http://127.0.0.1:8000/admin - админка

## Деплой
- Проект развернут на PythonAnywhere:
- Демо: https://strafestreiv.pythonanywhere.com
- Использованы: Python 3.9, Django 4.2, SQLite

## Особенности реализации
- Алгоритм взвешенного случайного выбора цитат
- AJAX-голосование без перезагрузки страницы
- Валидация форм на стороне клиента и сервера
- Автоматическая смена цитаты после голосования
- Система рейтингов и статистики

## API endpoints
- GET / - случайная цитата
- POST /like/<id>/ - лайк цитаты
- POST /dislike/<id>/ - дизлайк цитаты
- GET /popular/ - популярные цитаты
- GET /dashboard/ - статистика
- GET /add/ - форма добавления цитаты

## Автор
StrafeStreiv

## Лицензия
MIT License
