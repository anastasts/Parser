import requests
from bs4 import BeautifulSoup
import csv
import os #для автоматического открытия файла
import time


URL = 'https://auto.ria.com/newauto/marka-jeep/'
#user-agent: передается название браузера операционной системы
HEADERS = {'user-agent': 'ozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 YaBrowser/20.12.2.105 Yowser/2.5 Safari/537.36',
           'accept': '*/*' } #словарь, в который мы отправим заголовки
HOST = 'https://auto.ria.com' #чтобы можно было перейти по ссылке
FILE = 'cars.csv'


#аргументы: url страницы, с которой необходимо получить контент,
#params - опциональный аргумент, нужен чтобы мы могли передавать дополнительные параметры к адресу URL
#(когда переходим на страницу URL, то джипов мб больше чем на 1 стр, поэтому к ссылке добавляются нове параметры)
def get_html(url, params = None):
    while True:
        r = requests.get(url, headers = HEADERS, params = params)
        return r
        time.sleep(10)


#функция для количества страниц ()узнает сколько их)
#если не автомат, то в URL пишем другой адрес
def get_pages_count(html):
    while True:
        soup = BeautifulSoup(html, 'html.parser')

        pagination = soup.find_all('span', class_ = 'mhide')

        #проверяем есть ли пагинация
        if pagination:
            return int(pagination[-1].get_text()) #индекс последнего элемента
        else:
            return 1
        print(pagination)
        time.sleep(10)


#будем парсить html
def get_content(html):
    while True:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', class_ = 'proposition' ) #парсим "карточки" машин

        cars = []
        for item in items:
            #проверяем есть ли цена в гривнах
            uah_price = item.find('span', class_ = 'grey size13')
            if uah_price: #если объект есть
                uah_price = uah_price.get_text() #.replace('*', '')
            else:
                uah_price = "Цену уточняйте "
            #в список cars будем добавлять словари
            cars.append({
                #обращаемся к объекту item и у него находим 1 элемент
                #strip = True обрезает лишние пробелы
                'title': item.find('div', class_ = 'proposition_title').get_text(strip = True), #можно сделать так, чтобы название не склеивалось с параметрами авто
                'link': HOST + item.find('a').get('href'),
                'usd_price': item.find('span', class_ = 'green').get_text(strip = True),
                'uah_price': uah_price,
                'city': item.find('div', class_='proposition_region').find_next('strong').get_text(strip=True),
            })
        return cars
        time.sleep(10)


#функция, которая сохраняет файл
def save_file(items, path): #путь к файлу куда необходимо сохранять
    with open(path, 'w', newline = '') as file: #w - открываем файл для записи, если файла нет, то он будет создан, если есть, то будет очищен и запишутся новые данные
        writer = csv.writer(file, delimiter = ';') #объект writer переменная также записана, указываем указатель открытого файла file, delimiter - разделитель для csv файлов, чтобы нормально открывались в excel
        writer.writerow(['Марка', 'Ссылка', 'Цена в $', 'Цена в UAh', 'Город'])
        #проходим по коллекции, те берем конкретный автомобиль и записываем его файл csv
        for item in items:
            writer.writerow([item['title'], item['link'], item['usd_price'], item['uah_price'], item['city']])
    #закрывать файл не нужно тк с конструкцией with open .. он будет закрыт автоматически

#показывает исходный код страницы URL
def parse():
    while True:
        URL = input('Введите URL:')
        URL = URL.strip() #для обрезания ссылки
        html = get_html(URL) #for 1 page

        if html.status_code == 200:
            cars = []
            pages_count = get_pages_count(html.text)

            #запускаем цикл, чтобы парсить все страницы сразу
            for page in range(1, pages_count + 1):
                print(f'Парсинг страницы {page} из {pages_count}....')
                html = get_html(URL, params = {'page': page})
                cars.extend(get_content(html.text))
            save_file(cars, FILE) #передаем ей полученные автомобили
            print(f'Получено {len(cars)} автомобилей')
            #os.startfile(FILE) #автоматическое открытие файла
            #cars = get_content(html.text)
        else:
            print('Error')
        time.sleep(10)

parse()