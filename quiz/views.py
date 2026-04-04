"""Views for the capitals quiz application."""

import json
import os

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
        if not country_name:
            errors['country'] = 'Название страны обязательно'
        if not capital_name:
            errors['capital'] = 'Название столицы обязательно'
        if len(country_name) < 2:
            errors['country'] = 'Название страны должно быть длиннее 2 символов'
        if len(capital_name) < 2:
            errors['capital'] = 'Название столицы должно быть длиннее 2 символов'

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
    """Отображает форму викторины и ответы"""
    data = load_data()
    countries = data['countries']

    if request.method == 'POST':
        # Проверяем ответы
        score = 0
        total = len(countries)
        results = []

        for idx, item in enumerate(countries):
            user_answer = request.POST.get(f'q_{idx}', '').strip()
            is_correct = user_answer.lower() == item['capital'].lower()
            if is_correct:
                score += 1
            results.append({
                'country': item['country'],
                'correct_capital': item['capital'],
                'user_answer': user_answer,
                'is_correct': is_correct,
            })

        return render(request, 'quiz/quiz_result.html', {
            'score': score,
            'total': total,
            'results': results,
            'percentage': (score / total) * 100
        })

    return render(request, 'quiz/quiz.html', {'countries': countries})

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
