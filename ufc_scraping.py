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
def fights(card_urls):
    all_fights_links = []
    for link in card_urls[1:2]:
        card = requests.get(link)
        card_soup = BeautifulSoup(card.content, 'html.parser')
        fight_element = card_soup.find('tbody', class_='b-fight-details__table-body')
        fight_rows = fight_element.find_all('tr')
        for fights in fight_rows:
            all_fights_links.append(fights['data-link'])
    return all_fights_links

# retrieve stats for each round in a fight for every fight
def get_stats(fight_urls):
    for fight_ID, url in enumerate(fight_urls):
        fight = requests.get(url)
        fight_soup = BeautifulSoup(fight.content, 'html.parser')

        # retrieves html for each round
        fight_table = fight_soup.find("table", class_="b-fight-details__table")
        round_rows = fight_table.find_all("tr", class_="b-fight-details__table-row")

        round_stats = {}
        # stats are put into a dict with key=round, and values = name, sig str...
        for round_no, row in enumerate(round_rows):
            f1 = [fight_ID, round_no]
            f2 = [fight_ID, round_no]
            for td in row.find_all('td'):
                p = td.find_all('p')
                if len(p) >= 2:
                    f1.append(p[0].get_text(strip=True))
                    f2.append(p[1].get_text(strip=True))
            round_stats[round_no] = [f1, f2]
        return round_stats

def main():
    fight_cards = card_finder(ufc_stats)
    fight_links = fights(fight_cards)
    fight_stats = get_stats(fight_links)
    print(fight_stats)

if __name__ == "__main__":
    main()
