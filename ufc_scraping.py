from bs4 import BeautifulSoup
import requests
import pandas as pd

ufc_stats = "http://ufcstats.com/statistics/events/completed"

# scraping ufcstats.com to give links to every documented fight card
def card_finder(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.content, 'html.parser')
    s = soup.find('tbody')
    cards = s.find_all('a')
    card_links = []
    for card in cards:
        card_links.append(card['href'])
    return card_links

# retrieving each fight link in each card
def fights(links):
    fights_on_card = []
    for link in links[1:2]:
        fight = requests.get(link)
        card_soup = BeautifulSoup(fight.content, 'html.parser')
        fight_body_html = card_soup.find('tbody', class_='b-fight-details__table-body')
        fight_links = fight_body_html.find_all('tr')
        for fights in fight_links:
            fights_on_card.append(fights['data-link'])
    return fights_on_card


print(fights(card_finder(ufc_stats)))
