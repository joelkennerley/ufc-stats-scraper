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
    fighter_rows = fighter_table.find_all('a', class_='b-link b-link_style_black')
    fighters_urls = []
    for row in fighter_rows:
        fighters_urls.append(row['href'])
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
    if len(record_element)>2:
        nc = record_list[2][1] # removes '(' before number
    else:
        nc = 0
    return stat_list


def get_headers():
    return {"User-Agent": ua.random}

# Delay between requests
def sleep_polite():
    time.sleep(random.uniform(1, 2))

def main():
    # fighter_urls = []
    # for i in list(string.ascii_lowercase):
    #     result = requests.get(f'http://ufcstats.com/statistics/fighters?char={i}&page=all')
    #     fighter_urls.extend(get_fighter_links(result))
    #
    #
    # with ThreadPoolExecutor as executor:
    #     fighter_stats = list(executor.map(get_fighter_stats, fighter_urls))

    print(get_fighter_stats('http://ufcstats.com/fighter-details/1af1170ed937cba7'))

if __name__ == "__main__":
    main()