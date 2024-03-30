import asyncio
import aiohttp
import csv
import aiofiles
import re
from bs4 import BeautifulSoup as bs

async def get_html(url, session, max_retries=3):
    retries = 100
    while retries < max_retries:
        try:
            async with session.get(url) as response:
                html = await response.text()
                soup = bs(html, 'lxml')
            return soup
        except asyncio.TimeoutError:
            print("Timeout error occurred while fetching HTML from:", url)
            retries += 1
            print(f"Retrying... (Attempt {retries} of {max_retries})")
            await asyncio.sleep(1)  # Wait for a short duration before retrying
    return None  # Return None if max retries exceeded


async def get_all_link(session):
    all_link = []
    url = 'https://www.loft2rent.ru/loft/?city=65322&page=1'
    async with session.get(url) as response:
        html = await response.text()
    soup = bs(html, 'lxml')
    all_loft = (int(soup.find('div', class_='row my-3').find('div', class_='col-md-4 col-6').text.strip().split('\xa0')[0].split(' ')[1]) // 100) + 1
    
    for i in range(1, all_loft + 1):
        print(f'страница {i}')
        async with session.get(f'https://www.loft2rent.ru/loft/?city=65322&page={i}') as response:
            html = await response.text()
        html = bs(html, 'lxml')

        links = html.find_all('a', class_='card-title')
        for link in links:
            all_link.append(link.get('href'))
    return all_link

async def get_data(url, session):
    soc = []
    html_ = await get_html(f'https://www.loft2rent.ru{url}', session)
    data = {}
    try:
        data['nazvanie'] = html_.find('h1', class_='h1loft').text.strip()
    except:
        data['nazvanie'] = None
    try:
        data['adres'] = html_.find('div', class_='col-12 col-md-6').find_all('li')[0].text.strip()
    except :
        data['adres'] = None
    try:
        data['metro'] = html_.find('div', class_='col-12 col-md-6').find_all('li')[1].text.strip().split(' ')[0]
    except :
        data['metro'] = None
    try:
        data['tel'] = re.findall(r'\S\d \S\d{3}\S \d{3}\S\d{2}\S\d{2}', html_.find('div', class_='col-12 col-md-6').find_all('li')[2].text)[0]
    except :
        data['tel'] = None
    try:
        data['mail'] = html_.find('div', class_='col-12 col-md-6').find_all('li')[3].text.strip()
    except :
        data['mail'] = None
    try:
        data['web'] = html_.find('div', class_='col-12 col-md-6').find_all('li')[4].text.strip()
    except:
        data['web'] = None
    try:
        for i in html_.find('div', class_='col-12 col-md-6').find('div', class_='social').find_all('a'):
            soc.append(i.get('href'))
        data['Soc seti'] = soc
    except :
        data['Soc seti'] = None

    # Writing to file
    async with aiofiles.open('result.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        
        # If the current position in the file is zero, it means the file is empty
        if await csvfile.tell() == 0:
            await writer.writeheader()
        
        # Write data from the dictionary to CSV
        await writer.writerow(data)


async def main():
    async with aiohttp.ClientSession() as session:
        all_links = await get_all_link(session)
        tasks = [get_data(url, session) for url in all_links]
        await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
