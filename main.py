import requests
import re
from bs4 import BeautifulSoup as bs
import csv

def get_html(url):
    r = requests.get(url=url).text
    soup = bs(r, 'lxml' )
    return soup




    


def get_data(url):
    soc = []
    data = {}
    #url = 'https://www.loft2rent.ru/loft/5581/31343/'
    html_ = get_html(f'https://www.loft2rent.ru{url}')
    try:
        data['nazvanie'] = html_.find('h1', class_:='h1loft').text.strip()
    except:
        data['nazvanie'] = None
    try:
        data['adres'] = html_.find('div', class_:='col-12 col-md-6').find_all('li')[0].text.strip()
    except:
        data['adres'] = None
    try:
        data['metro'] = html_.find('div', class_:='col-12 col-md-6').find_all('li')[1].text.strip().split(' ')[0]
    except:
        data['metro'] = None
    try:
        data['tel'] = re.findall(r'\S\d \S\d{3}\S \d{3}\S\d{2}\S\d{2}', html_.find('div', class_:='col-12 col-md-6').find_all('li')[2].text)[0]
    except:
        data['tel'] = None
    try:
        data['mail'] = html_.find('div', class_:='col-12 col-md-6').find_all('li')[3].text.strip()
    except:
        data['mail'] = None
    try:
        data['web'] = html_.find('div', class_:='col-12 col-md-6').find_all('li')[4].text.strip()
    except:
        data['web'] = None
    try:    
        for i in html_.find('div', class_:='col-12 col-md-6').find('div', class_:='social').find_all('a'):
            soc.append(i.get('href'))
        data['Soc seti'] = soc
    except:
        data['Soc seti'] = None
    return data

def write_data_to_csv(data):
    # Открываем CSV файл для записи
    with open('result.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        
        # Если текущая позиция в файле равна нулю, это означает, что файл пуст
        if csvfile.tell() == 0:
            writer.writeheader()
        
        # Записываем данные из словаря в CSV
        writer.writerow(data)
    

def main():
    
    url = 'https://www.loft2rent.ru/loft/?city=65322&page=1'
    html = get_html(url)
    all_loft = (int(html.find('div', class_:='row my-3').find('div', class_:='col-md-4 col-6').text.strip().split('\xa0')[0].split(' ')[1]) // 100) + 1
    
    for i in range(1, all_loft + 1):
        
        html = get_html(f'https://www.loft2rent.ru/loft/?city=65322&page={i}')

        links = html.find_all('a', class_:='card-title')
        for link in links:
            write_data_to_csv(get_data(link.get('href')))

if __name__ == '__main__':
    main()