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
        fight_element = fight_soup.find('table', class_="b-fight-details__table js-fight-table")

        # retrieves html for each round
        fight_table = fight_soup.find("table", class_="b-fight-details__table")
        fight_rows = fight_table.find_all("tr", class_="b-fight-details__table-row")

        round_stats = {}
        # stats are put into a dict with key=round, and values = name, sig str...
        for i, row in enumerate(fight_rows):
            f1 = []
            f2 = []
            for td in row.find_all('td'):
                p = td.find_all('p')
                if len(p) >= 2:
                    f1.append(p[0].get_text(strip=True))
                    f2.append(p[1].get_text(strip=True))
            round_stats[i] = [f1, f2]
        return round_stats

def main():
    something = fights(card_finder(ufc_stats))
    print(get_stats(something))

if __name__ == "__main__":
    main()
