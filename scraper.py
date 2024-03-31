import requests
from bs4 import BeautifulSoup
import json

# Функція для отримання інформації про автора та його цитати
def get_author_info(author_url):
    response = requests.get(author_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    author_name = soup.select_one('.author-title').get_text()
    born_date = soup.select_one('.author-born-date').get_text()
    born_location = soup.select_one('.author-born-location').get_text()
    description = soup.select_one('.author-description').get_text(strip=True)

    author_info = {
        'fullname': author_name,
        'born_date': born_date,
        'born_location': born_location,
        'description': description
    }

    quotes = soup.select('.quote')
    author_quotes = []
    for quote in quotes:
        text = quote.select_one('.text').get_text(strip=True)
        author = quote.select_one('.author').get_text()
        tags = [tag.get_text() for tag in quote.select('.tag')]
        quote_info = {
            'tags': tags,
            'author': author,
            'quote': text
        }
        author_quotes.append(quote_info)

    return author_info, author_quotes

# Функція для скрапінгу цитат зі сторінки та генерації JSON
def scrape_quotes(base_url, pages):
    all_quotes = []
    all_authors_info = {}
    for page in range(1, pages + 1):
        page_url = f'{base_url}/page/{page}/'
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        quotes = soup.select('.quote')

        for quote in quotes:
            quote_text = quote.select_one('.text').get_text(strip=True)
            author_name = quote.select_one('.author').get_text(strip=True)
            tags = [tag.get_text() for tag in quote.select('.tag')]

            quote_info = {
                'tags': tags,
                'quote': quote_text
            }
            all_quotes.append(quote_info)

            # Отримуємо інформацію про автора
            author_url = base_url + quote.find('a')['href']
            if author_url not in all_authors_info:
                author_info, _ = get_author_info(author_url)
                all_authors_info[author_url] = author_info

    return all_quotes, list(all_authors_info.values())

# Основний код для виклику функцій та збереження даних у JSON файл
if __name__ == '__main__':
    base_url = 'http://quotes.toscrape.com'
    pages = 10  # Кількість сторінок для скрапінгу

    # Отримуємо цитати та інформацію про авторів та зберігаємо їх у файли
    quotes, authors_info = scrape_quotes(base_url, pages)
    with open('quotes.json', 'w') as quotes_file:
        json.dump(quotes, quotes_file, indent=2)

    with open('authors.json', 'w') as authors_file:
        json.dump(authors_info, authors_file, indent=2)
