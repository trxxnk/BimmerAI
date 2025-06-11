import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, 'bmw_prices_150page.csv')
os.makedirs(script_dir, exist_ok=True)
file_headers = ['Модель', 'Год', 'Пробег', 'Цена', 'Описание']
with open(output_path, 'w', encoding='utf-8') as f:
    head = ','.join(file_headers) + '\n' 
    f.write(head)


def clean_price(price_str: str):
    """Очищает цену от лишних символов и преобразует в число"""
    return int(price_str
               .replace('\xa0', '')
               .replace('р.', '')
               .replace(' ', '')
               .replace('$', '')
               .replace('€', '')
               .replace('≈', '')
               .strip())
    
    
def clean_year(year_str: str):
    """Очищает год от лишних символов и преобразует в число"""
    return int(year_str
               .replace(' ', '')
               .replace('г.', '')
               .strip())
    
    
def clean_mileage(mileage_str: str):
    """Очищает пробег от лишних символов и преобразует в число"""
    return int(mileage_str
               .replace('\xa0', '')
               .replace('\u2009', '')
               .replace(' ', '')
               .replace('км', '')
               .strip())

cars_data = []
parsed_pages = []
error_pages = []
n_pages = 120
print(f" === Начинаю парсить страницы ({n_pages} шт.) === ")
for page in [150]:
    print(f" * Парсинг страницы #{page}...")
    url = f"https://cars.av.by/filter?brands[0][brand]=8&page={page}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for card in soup.find_all('div', class_='listing-item'):
            try:
                title = card.find('a', class_='listing-item__link').text.strip()
                price = clean_price(card.find('div', class_='listing-item__priceusd').text)
                
                params = card.find('div', class_='listing-item__params').find_all('div')
                year = clean_year(params[0].text)
                description = params[1].text.strip() if len(params) > 1 else 'N/A'
                mileage = clean_mileage(params[2].text) if len(params) > 2 else 'N/A'
                
                cars_data.append({
                    'Модель': f'"{title}"',
                    'Цена': price,
                    'Год': year,
                    'Описание': f'"{description}"',
                    'Пробег': mileage
                })
            except Exception as e:
                error_pages.append(page)
                print(f"Ошибка в карточке: {e}")
                continue
        
        with open(output_path, 'a', encoding='utf-8') as f:
            for car in cars_data:
                row = ','.join([str(car[param]) for param in file_headers]) + '\n'
                f.write(row)
        parsed_pages.append(page)
                
        print(f" >> Сохранено {len(cars_data)} записей")
        cars_data.clear()
        print(f" $$ Сохранены данные для страниц {parsed_pages}")
        
        sleep(randint(2, 5))  # Задержка между запросами
        
    except requests.RequestException as e:
        error_pages.append(page)
        print(f"Ошибка запроса: {e}")
        continue
    
print(f" // Результат сохранен в {output_path}")
print(f" // Парсинг завершен. Результаты:")
print(f" // - Парсинг прошел успешно для {len(parsed_pages)} страниц")
print(f" // - Ошибки возникли для {len(error_pages)} страниц")
print(f" // - Список ошибок: {error_pages}")
print(f" // Список успешно обработанных страниц: {parsed_pages}")