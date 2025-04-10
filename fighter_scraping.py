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
def get_fighter_links(response):
    soup = BeautifulSoup(response.content, 'html.parser')
    fighter_table = soup.find('table', class_='b-statistics__table')
    fighter_rows = fighter_table.find_all('a', class_='b-link b-link_style_black')
    fighters_urls = []
    for row in fighter_rows:
        fighters_urls.append(row['href'])
    return fighters_urls

def get_headers():
    return {"User-Agent": ua.random}

# Delay between requests
def sleep_polite():
    time.sleep(random.uniform(1, 2))

def main():
    fighter_urls = []
    for i in list(string.ascii_lowercase):
        result = requests.get(f'http://ufcstats.com/statistics/fighters?char={i}&page=all')
        fighter_urls.extend(get_fighter_links(result))
    print(len(fighter_urls))

if __name__ == "__main__":
    main()