import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randint
import os
import argparse
from tqdm import tqdm
import sys

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Parse BMW listings from av.by')
    parser.add_argument('-o', '--output', type=str, default='bmw_test_data.csv',
                        help='Output file name (default: bmw_test_data.csv)')
    parser.add_argument('-p', '--pages', type=int, default=1,
                        help='Number of pages to parse (default: 1)')
    parser.add_argument('-s', '--start-page', type=int, default=1,
                        help='Starting page number (default: 1)')
    return parser.parse_args()

def clean_price(price_str: str):
    """Cleans price string and converts to number"""
    return int(price_str
               .replace('\xa0', '')
               .replace('р.', '')
               .replace(' ', '')
               .replace('$', '')
               .replace('€', '')
               .replace('≈', '')
               .strip())
    
def clean_year(year_str: str):
    """Cleans year string and converts to number"""
    return int(year_str
               .replace(' ', '')
               .replace('г.', '')
               .strip())
    
def clean_mileage(mileage_str: str):
    """Cleans mileage string and converts to number"""
    return int(mileage_str
               .replace('\xa0', '')
               .replace('\u2009', '')
               .replace(' ', '')
               .replace('км', '')
               .strip())

def setup_output_file(output_path:str, headers:list[str]):
    """Initialize output file with headers"""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(','.join(headers) + '\n')

def parse_car_listing(card:BeautifulSoup):
    """Parse a single car listing card"""
    title = card.find('a', class_='listing-item__link').text.strip()
    price = clean_price(card.find('div', class_='listing-item__priceusd').text)
    
    params = card.find('div', class_='listing-item__params').find_all('div')
    year = clean_year(params[0].text)
    description = params[1].text.strip() if len(params) > 1 else 'N/A'
    mileage = clean_mileage(params[2].text) if len(params) > 2 else 'N/A'
    
    return {
        'Модель': f'"{title}"',
        'Цена': price,
        'Год': year,
        'Описание': f'"{description}"',
        'Пробег': mileage
    }

def save_cars_data(cars_data:list[dict], output_path:str, headers:list[str]):
    """Save parsed car data to CSV file"""
    with open(output_path, 'a', encoding='utf-8') as f:
        for car in cars_data:
            row = ','.join([str(car[param]) for param in headers]) + '\n'
            f.write(row)

def parse_page(page_num:int, headers:list[str], session:requests.Session):
    """Parse a single page of car listings"""
    url = f"https://cars.av.by/filter?brands[0][brand]=8&page={page_num}"
    cars_data = []
    
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for card in soup.find_all('div', class_='listing-item'):
            try:
                car_data = parse_car_listing(card)
                cars_data.append(car_data)
            except Exception as e:
                # Just skip problematic cards
                continue
                
        sleep(randint(1, 3))  # Sleep for a random time to avoid being blocked
        return cars_data, None
        
    except requests.RequestException as e:
        return [], str(e)

def main():
    args = parse_arguments()
    
    # Setup
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    file_headers = ['Модель', 'Год', 'Пробег', 'Цена', 'Описание']
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, args.output)
    
    # Initialize output file
    setup_output_file(output_path, file_headers)
    
    # Create a persistent session for better performance
    session = requests.Session()
    session.headers.update(headers)
    
    # Parse pages
    total_cars = 0
    error_pages = []
    start_page = args.start_page
    end_page = start_page + args.pages - 1
    
    print(f"Parsing BMW listings from page {start_page} to {end_page}")
    print(f"Output file: {output_path}")
    
    with tqdm(total=args.pages, desc="Progress", unit="page") as pbar:
        for page in range(start_page, end_page + 1):
            cars_data, error = parse_page(page, file_headers, session)
            
            if error:
                error_pages.append((page, error))
                pbar.set_postfix({"status": f"Error on page {page}"})
            else:
                save_cars_data(cars_data, output_path, file_headers)
                total_cars += len(cars_data)
                pbar.set_postfix({"cars": total_cars, "current page": page})
            
            pbar.update(1)
    
    # Summary
    print(f"\nParsing completed:")
    print(f"- Total cars found: {total_cars}")
    print(f"- Successfully parsed pages: {args.pages - len(error_pages)}/{args.pages} ({(args.pages - len(error_pages))/args.pages*100:.1f}%)")
    
    if error_pages:
        print(f"- Pages with errors ({len(error_pages)}):")
        for page, error in error_pages:
            print(f"  * Page {page}: {error}")
    
    print(f"Results saved to: {output_path}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nParser stopped by user")
        sys.exit(0)