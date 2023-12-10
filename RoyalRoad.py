import requests
from bs4 import BeautifulSoup
from Audiobook import Audiobook

url = "https://www.royalroad.com/fiction/41477/truth-seeker-a-litrpg-timeloop"


def parser(url):
    return BeautifulSoup(requests.get(url).content, 'html.parser')


def text_from_page(page):
    content = page.find_all('div', class_='chapter-content')[0]
    lines = [paragraph.text for paragraph in content.find_all('p')]
    return lines


def chapters(main_page):
    # main_page = BeautifulSoup(requests.get('').content, 'html-parser')
    name = main_page.find('h1', property='name').text
    print(name)
    table = main_page.find('table', id='chapters').find_all('tbody')[0]
    links = table.find_all('tr')
    chaps = list()
    for link in links:
        full_link = 'https://www.royalroad.com' + link['data-url']
        # print(full_link)
        chaps.append(text_from_page(parser(full_link)))
    return chaps, name


if __name__ == '__main__':
    chaps, name = chapters(parser(url))
    a = Audiobook()
    a.put_chapters(chaps)
    a.save(name)
