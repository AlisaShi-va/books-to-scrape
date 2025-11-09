import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ..scraper import get_book_data, scrape_books

# Тест 1: Проверка, что get_book_data возвращает список словарей с корректными атрибутами
def test_get_book_data_returns():
    # Используем реальный URL первой страницы (может измениться)
    page = "http://books.toscrape.com/catalogue/page-1.html"
    result = get_book_data(page)
    
    assert isinstance(result, list)
    assert len(result) > 0  # Проверка, что книги найдены
    for book in result:
        assert isinstance(book, dict)
        assert 'title' in book and isinstance(book['title'], str)
        assert 'price' in book and isinstance(book['price'], str)
        assert 'rating' in book and isinstance(book['rating'], str)

# Тест 2: Проверка количества книг в scrape_books
def test_scrape_books_collects_count():
    result = scrape_books(save_to_file=False)
    
    assert isinstance(result, list)
    assert len(result) > 0  # Должно быть хотя бы несколько книг
    # Проверка элементов внутри словаря
    for book in result[:10]:  # Проверка первых 10 книг (для скорости)
        assert isinstance(book, dict)
        assert set(book.keys()) == {'title', 'price', 'rating'}

# Тест 3: Проверка корректности полей
def test_scrape_books_correct():
    result = scrape_books(save_to_file=False)
    
    assert len(result) > 0
    # Проверяем случайную книгу (например, первую)
    book = result[0]
    assert 'title' in book and len(book['title']) > 0  # Заголовок не пустой
    assert 'price' in book and book['price'].startswith('£')  # Цена начинается с £
    assert 'rating' in book and book['rating'] in ['One', 'Two', 'Three', 'Four', 'Five']