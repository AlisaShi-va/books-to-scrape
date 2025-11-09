! pip install -q schedule pytest

import time
import requests
import schedule
from bs4 import BeautifulSoup
import re
import json
import os

def get_book_data(book_url: str) -> dict:
   """
   Функция осуществляет сбор информации со страницы каталога Books to Scrape
   на вход (Args): валидный URL страницы каталога
   на выходе (Returns): словарь со следующими данными:
   - 'title' (str): название книги.
   - 'price' (str): стоимость книги (в евро, в формате ЕЕ.ЦЦ - евро, центы)
   - 'rating' (int): рейтинг книги (значение от 1 до 5).
   - 'availability' (int): количество книг в наличии
   - 'description' (str): описание книги
   - 'product_info' (dict): доп. характеристики
   исключения (Raises):
   - requests.RequestException - Не удалось загрузить страницу
   - AttributeError - Структура страницы не соответствует ожидаемой
   """

   # Загрузка html-страницы
   response = requests.get(book_url)
   response.raise_for_status() # Вызов исключения в случае http-ошибки
   response.encoding = 'utf-8'
   soup = BeautifulSoup(response.text, 'html.parser')

   # Извлечение названия книги
   title = soup.find('h1').text.strip()

   # Извлечение стоимости с помощью регулярного выражения (без указания валюты)
   price_element = soup.find('p', class_='price_color')
   if price_element:
      price_text = price_element.text.strip()
      # Поиск числа в формате ЕЕ.ЦЦ
      match = re.search(r'(\d+\.\d+)', price_text)
      price = match.group(1) if match else None
   else:
      price = None

   # Извлечение рейтинга в виде числа
   rating_classes = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
   rating_element = soup.find('p', class_='star-rating')
   rating_text = rating_element['class'][1] if rating_element and len(rating_element['class']) > 1 else None
   rating = rating_classes.get(rating_text, None)

   # Извлечение количества книг в наличии
   availability_element = soup.find('p', class_='instock')
   if availability_element:
      availability_text = availability_element.text.strip()
      # Извлечение числа из строки "In stock (22 available)"
      availability = int(availability_text.split('(')[1].split()[0])
   else:
      availability = None

   # Извлечение описания книги
   description_div = soup.find('div', id='product_description')
   description = description_div.find_next('p').text.strip() if description_div else None

   # Извлечение доп. характеристик
   product_info = {}
   table = soup.find('table', class_='table table-striped')
   if table:
      rows = table.find_all('tr')
      for row in rows:
         key = row.find('th').text.strip()
         value = row.find('td').text.strip()
         # Очищение цен и налогов от символов валюты
         match = re.search(r'(\d+\.\d+)', value)
         if match:
            value = match.group(1)
         product_info[key] = value

   # Формирование результата
   book_data = {
      'title': title,
      'price': price,
      'rating': rating,
      'availability': availability,
      'description': description,
      'product_info': product_info
   }

   return book_data


def scrape_books(is_save: bool = False) -> list[dict]:
    """
    Функция осуществляет парсинг всего каталога Books to Scrape,
    используя функцию get_book_data
    на вход (Args): флаг необходимости сохранять данные в файл (по умолчанию - False)
    на выходе (Returns): список словарей с данными о книгах
    Исключения (Raises): requests.RequestException - Не удалось загрузить страницу
    """

    url = "http://books.toscrape.com/catalogue/"
    books_data = []
    page_num = 1

    while True:
        # Формирование постраничного url внутри каталога 
        page_url = f"{url}page-{page_num}.html"
        response = requests.get(page_url)

        # Если страница не найдена, прерываем цикл
        if response.status_code == 404:
            break

        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск всех ссылок по тегам
        book_links = soup.find_all('h3')
        for h3 in book_links:
            link = h3.find('a')
            if link:
                book_url = url + link['href']
                # Парсинг данных книги
                book_data = get_book_data(book_url)
                books_data.append(book_data)

        page_num += 1

    # Сохранение в файл
    if is_save:
        file_path = os.path.join(os.getcwd(), 'books_data.txt')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(books_data, f, indent=4, ensure_ascii=False)

    return books_data

# Функция запуска скрейпинга
def run_scraping():
    print(f"Запуск сбора данных в {time.strftime('%H:%M:%S')}")
    try:
        scrape_books(is_save=True)
        print("Сбор данных завершен. Данные сохранены в 'books_data.txt'.")
    except Exception as e:
        print(f"Ошибка сбора данных: {e}")

    # Планирование запуска с отменой до наступления следующего дня
    schedule.every().day.at("19:00").do(run_scraping)
    return schedule.CancelJob 

# Настройка расписания на текущий день
schedule.every().day.at("19:00").do(run_scraping)

print("Автоматический сбор осуществляется в 19:00...")
while True:
    schedule.run_pending()
    time.sleep(1)