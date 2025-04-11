from bs4 import BeautifulSoup
import requests
import pandas as pd
from fake_useragent import UserAgent
import random
import time
from concurrent.futures import ThreadPoolExecutor
import string
ua = UserAgent()

ufc_fighters = 'http://ufcstats.com/statistics/fighters?char=a&page=all'

# retrieves links to fighters stats page
# maybe add multithreading??? but only 26 requests so really not too bad
def get_fighter_links(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    fighter_table = soup.find('table', class_='b-statistics__table')
    fighter_rows = fighter_table.find_all('tr', class_='b-statistics__table-row')
    fighter_rows = fighter_rows[2:] # removing header element and empty element without href
    fighters_urls = []
    for row in fighter_rows:
        hyperlink = row.find('a', class_='b-link b-link_style_black')
        fighters_urls.append(hyperlink['href'])
    return fighters_urls

def get_fighter_stats(fighter_url):
    # sleep_polite()
    stat_list = []
    response = requests.get(fighter_url, headers=get_headers())
    soup = BeautifulSoup(response.content, 'html.parser')
    name = soup.find('span', class_='b-content__title-highlight').get_text(strip=True)
    record_element = soup.find('span', class_='b-content__title-record').get_text(strip=True)
    # record element looks smth like: record: 11-1-1 (1 NC)
    # record list: ['record:', '11-1-1', '(1', 'NC)']
    record_list = record_element.split()
    wins, losses, draws = record_list[1].split('-')
    if len(record_list)>2:
        nc = record_list[2][1] # removes '(' before number
    else:
        nc = 0

    stat_list.extend([name, wins, losses, draws, nc])

    div_element = soup.find('div', class_='b-fight-details b-fight-details_margin-top')
    li_elements = div_element.find_all('li', class_='b-list__box-list-item b-list__box-list-item_type_block')
    for li in li_elements:
        full_text = li.get_text(strip=True)
        value = full_text.split(":", 1)[-1].strip()  # Split at the first colon and take the part after it
        stat_list.append(value)
    stat_list.pop(-5) # deleting because theres an extra li element in every stats table
    return stat_list

def get_headers():
    return {"User-Agent": ua.random}

# Delay between requests
def sleep_polite():
    time.sleep(random.uniform(1, 2))

def main():
    fighter_urls = []
    for i in list(string.ascii_lowercase):
        result = requests.get(f'http://ufcstats.com/statistics/fighters?char={i}&page=all', headers=get_headers())
        fighter_urls.extend(get_fighter_links(result))

    with ThreadPoolExecutor(max_workers=10) as executor:
        fighter_stats = list(executor.map(get_fighter_stats, fighter_urls[:5]))

    print(fighter_stats)

if __name__ == "__main__":
    main()