import pytest
from scraper import get_book_data, scrape_books

# Тест 1. Проверка структуры словаря get_book_data
def test_get_book_data_returns():
  # Использование url из каталога для теста
  book_url = "http://books.toscrape.com/catalogue/how-music-works_979/index.html"
  result = get_book_data(book_url)

  # Проверка формата результата
  assert isinstance(result, dict)

  # Проверка обязательных ключей
  required_keys = ['title', 'price', 'rating', 'availability', 'description']
  assert all(key in result for key in required_keys)

  # Проверка на заполненность значений
  for key in required_keys:
    assert result[key] != '', f"Ключ '{key}' пустой"

# Тест 2. Проверка количества книг, собранных scrape_books
def test_scrape_books_count():
  # Вызов scrape_books без сохранения в файл
  books_data = scrape_books(is_save=False)

  # Проверка формата результата
  assert isinstance(books_data, list)

  # Проверка на количество - собрано >= 20 книг 
  assert len(books_data) >= 20, f"Собрано {len(books_data)} книг, ожидалось >= 20"

  # Проверка на содержание - внутри элемента словарь с информацией о книге
  for book in books_data:
    assert isinstance(book, dict)
    assert 'title' in book

# Тест 3. Проверка на корректность и заполненность title
def test_book_data_correct():
  book_url = "http://books.toscrape.com/catalogue/how-music-works_979/index.html"
  result = get_book_data(book_url)

  assert 'title' in result
  assert result['title'] != ''
  assert 'Light' in result['title'], f"Title '{result['title']} не содержит 'Light'"
