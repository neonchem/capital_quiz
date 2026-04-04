"""Views for the capitals quiz application."""

import json
import os
import random
import re

from django.shortcuts import render, redirect

# Путь к файлу с данными
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'capitals.json')


def load_data():
    """Загружает данные из JSON файла"""
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """Сохраняет данные в JSON файл"""
    with open(DATA_PATH, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Главная страница
def home(request):
    """Рендерит главную страницу"""
    return render(request, 'quiz/home.html')

# Страница со списком всех стран и столиц
def country_list(request):
    """Отображает список всех стран и столиц"""
    data = load_data()
    countries = data['countries']
    return render(request, 'quiz/country_list.html', {'countries': countries})

# Страница добавления новой страны
def add_country(request):
    """Добвляет новую страну и столицу вместе с валидацией"""
    errors = {}

    if request.method == 'POST':
        country_name = request.POST.get('country', '').strip()
        capital_name = request.POST.get('capital', '').strip()

        # Валидация
        if country_name and not re.match(r'^[а-яА-ЯёЁa-zA-Z\s\-]+$', country_name):
            errors['country'] = 'Название страны может содержать только буквы, пробелы и дефисы'
        if capital_name and not re.match(r'^[а-яА-ЯёЁa-zA-Z\s\-]+$', capital_name):
            errors['capital'] = 'Название столицы может содержать только буквы, пробелы и дефисы'
        if len(country_name) < 2:
            errors['country'] = 'Название страны должно быть длиннее одного символа'
        if len(capital_name) < 2:
            errors['capital'] = 'Название столицы должно быть длиннее одного символа'

        # Проверка на дубликат
        if not errors:
            data = load_data()
            # Проверяем, нет ли уже такой страны
            exists = any(c['country'].lower() == country_name.lower() for c in data['countries'])
            if exists:
                errors['country'] = 'Такая страна уже есть в списке'
            else:
                data['countries'].append({'country': country_name, 'capital': capital_name})
                save_data(data)
                return redirect('country_list')

    return render(request, 'quiz/add_country.html', {'errors': errors})

# Страница для викторины (теста)
def quiz(request):
    """Display quiz form and process answers."""
    data = load_data()

    if request.method == 'POST':
        # Получаем порядок стран из скрытых полей
        total_questions = int(request.POST.get('total_questions', 0))
        shuffled_countries = []

        for i in range(total_questions):
            country_name = request.POST.get(f'country_{i}', '')
            capital_name = None
            # Находим столицу по названию страны
            for item in data['countries']:
                if item['country'] == country_name:
                    capital_name = item['capital']
                    break
            if capital_name:
                shuffled_countries.append({
                    'country': country_name,
                    'capital': capital_name
                })

        # Проверяем ответы
        score = 0
        total = len(shuffled_countries)
        results = []

        for idx, item in enumerate(shuffled_countries):
            user_answer = request.POST.get(f'q_{idx}', '').strip()
            is_correct = user_answer.lower() == item['capital'].lower()
            if is_correct:
                score += 1
            results.append({
                'country': item['country'],
                'correct_capital': item['capital'],
                'user_answer': user_answer,
                'is_correct': is_correct
            })

        return render(request, 'quiz/quiz_result.html', {
            'score': score,
            'total': total,
            'results': results,
            'percentage': (score / total) * 100
        })

    # GET запрос - показываем форму с перемешанными вопросами
    countries = data['countries']
    shuffled_countries = random.sample(countries, len(countries))

    return render(request, 'quiz/quiz.html', {
        'countries': shuffled_countries,
        'total': len(shuffled_countries)
    })

# Страница редактирования/удаления
def delete_country(request, country_name):
    """Удаляет страну из списка"""
    data = load_data()
    # Находим и удаляем страну
    original_len = len(data['countries'])
    data['countries'] = [c for c in data['countries'] if c['country'] != country_name]

    if len(data['countries']) < original_len:
        save_data(data)

    return redirect('country_list')
