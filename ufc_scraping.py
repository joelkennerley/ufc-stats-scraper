from bs4 import BeautifulSoup
import requests

ufc_stats = "http://ufcstats.com/statistics/events/completed"

result = requests.get(ufc_stats)
soup = BeautifulSoup(result.content, 'html.parser')

# scraping ufcstats.com to give links to every documented fight card
s = soup.find('tbody')
cards = s.find_all('a')
links = []
for card in cards:
    links.append(card['href'])



