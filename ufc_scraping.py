from bs4 import BeautifulSoup
import requests
import pandas as pd

# changes: change var names and restructure functions with a main function

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
        fight_element = card_soup.find('tbody', class_='b-fight-details__table-body')
        fight_links = fight_element.find_all('tr')
        for fights in fight_links:
            fights_on_card.append(fights['data-link'])
    return fights_on_card

# pretty cooked rn dont know what p is
def get_stats(urls):
    for url in urls:
        fight = requests.get(url)
        fight_soup = BeautifulSoup(fight.content, 'html.parser')
        fight_element = fight_soup.find('table', class_='b-fight-details__table js-fight-table')
        knockdowns = fight_element.find_all('p')
        return knockdowns

something = fights(card_finder(ufc_stats))
print(get_stats(something))
