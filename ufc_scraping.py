from bs4 import BeautifulSoup
import requests
import pandas as pd
from fake_useragent import UserAgent
import random
import time

ua = UserAgent()

# changes: change var names and restructure functions with a main function

ufc_stats = "http://ufcstats.com/statistics/events/completed?page=all"


def get_headers():
    return {"User-Agent": ua.random}

# === Delay between requests ===
def sleep_polite():
    time.sleep(random.uniform(1.5, 3.5))

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
    for link in card_urls[1:5]:
        # sleep_polite()
        try:
            card = requests.get(link, headers=get_headers())
            card_soup = BeautifulSoup(card.content, 'html.parser')
            fight_element = card_soup.find('tbody', class_='b-fight-details__table-body')
            fight_rows = fight_element.find_all('tr')
            for fights in fight_rows:
                all_fights_links.append(fights['data-link'])
        except Exception as e:
            print(f"Error with card {link}: {e}")
    return all_fights_links


def round_stats(stat_soup, fight_id):
    """
    we extract all the p values from each list, which are the actual stats; 'Brandon Moreno', '11 of 16', ...
    :param stat_soup: List of html jumble for each round
    :param fight_id: Number for every fight to be identifiable
    :return: list of lists, which hold every rounds stats
    """
    all_rounds = []
    for round_no, row in enumerate(stat_soup):
        f1 = [fight_id, round_no]
        f2 = [fight_id, round_no]
        for td in row.find_all('td'):
            p = td.find_all('p')
            if len(p) >= 2:
                f1.append(p[0].get_text(strip=True))
                f2.append(p[1].get_text(strip=True))
        all_rounds.append(f1)
        all_rounds.append(f2)
    return all_rounds

# function which splits stats if they have 'of'
def split_attempted_landed(list_of_rounds_merged):
    """
    splits columns which have 'of' into attempted and landed columns.
    :param list_of_rounds_merged: cleaned list of lists which has all the rounds stats
    :return: new list of lists, except columns have been split if they include an 'of'
    """
    list_of_lists = []
    for row in list_of_rounds_merged:
        new_row = []
        for i, item in enumerate(row):
            if isinstance(item, str) and ' of ' in item:
                attempted, landed = item.split(' of ')
                new_row.extend([int(attempted), int(landed)])
            else:
                new_row.append(item)
        list_of_lists.append(new_row)
    return list_of_lists

def clean_round(totals, sigs):
    """
    removing duplicates, merging sig strikes list with total strikes list
    :param totals: list of lists, where each list represents the total strike stats for each round
    :param sigs: list of lists, where each list represents the sig strike stats from each round
    :return: list of lists, each list represents the sig&total strikes in each round
    """
    # slicing to remove headers of the tables
    totals = totals[2:]
    sigs = sigs[2:]

    # removing duplicated data already in totals
    for sublist in sigs:
        del sublist[:5]

    # adding totals with associated sig str breakdowns
    merged = [sub1 + sub2 for sub1, sub2 in zip(totals, sigs)]

    # splitting stats into attempted and landed
    result = split_attempted_landed(merged)

    return result


# retrieve stats for each round in a fight for every fight
def get_stats(fight_urls):
    processed_data = []
    for fight_ID, url in enumerate(fight_urls):
        try:
            # sleep_polite()
            fight = requests.get(url, headers=get_headers())
            fight_soup = BeautifulSoup(fight.content, 'html.parser')

            # retrieves html for each round
            fight_table = fight_soup.find_all("table", class_="b-fight-details__table")
            totals_round_rows = fight_table[0].find_all("tr", class_="b-fight-details__table-row")
            sig_round_rows = fight_table[1].find_all("tr", class_="b-fight-details__table-row")

            # retrieves raw data from the html
            totals = round_stats(totals_round_rows, fight_ID)
            sigs = round_stats(sig_round_rows, fight_ID)

            # cleaning data
            cleaned_rounds = clean_round(totals, sigs)

            # splitting strings with "of" into 2 different columns
            processed_data.extend(cleaned_rounds)
        except Exception as e:
            print(f"get stats Failed on fight {url}: {e}")

    return processed_data

def create_dataframe(row_entries):
    """
    creates pandas dataframe of every round ever
    :param row_entries: list of lists, each list represents a round
    :return: pd dataframe
    """
    cols = ['fight_id', 'round', 'name', 'kd', 'sig_l', 'sig_a', 'sig_p', 'total_l', 'total_a', 'td_l',
            'td_a', 'td_p', 'sub', 'rev', 'ctrl', 'head_l', 'head_a', 'body_l', 'body_a', 'leg_l', 'leg_a', 'distance_l',
            'distance_a', 'clinch_l', 'clinch_a', 'ground_l', 'ground_a']
    fight_stats_df = pd.DataFrame(row_entries, columns = cols)
    return fight_stats_df


def main():
    fight_cards = card_finder(ufc_stats)
    fight_links = fights(fight_cards)
    fight_stats = get_stats(fight_links)
    fight_df = create_dataframe(fight_stats)
    fight_df.to_csv('round_statistics.csv', index=False)




if __name__ == "__main__":
    main()
