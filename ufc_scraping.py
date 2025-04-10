from bs4 import BeautifulSoup
import requests
import pandas as pd
from fake_useragent import UserAgent
import random
import time
from concurrent.futures import ThreadPoolExecutor

ua = UserAgent()

ufc_stats = "http://ufcstats.com/statistics/events/completed?page=all"

def get_headers():
    return {"User-Agent": ua.random}

# === Delay between requests ===
def sleep_polite():
    time.sleep(random.uniform(1, 2))

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
def get_fight_links(link):
    sleep_polite()
    card = requests.get(link, headers=get_headers())
    card_soup = BeautifulSoup(card.content, 'html.parser')
    fight_element = card_soup.find('tbody', class_='b-fight-details__table-body')
    fight_rows = fight_element.find_all('tr')
    return [fights['data-link'] for fights in fight_rows]

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
    with ThreadPoolExecutor(max_workers=10) as executor:
        processed_data = list(executor.map(process_fight_data, enumerate(fight_urls)))
    flat_list = flatten(processed_data)
    return flat_list

def process_fight_data(fight_urls):
    fight_ID, url = fight_urls
    sleep_polite()
    fight = requests.get(url, headers=get_headers())
    fight_soup = BeautifulSoup(fight.content, 'html.parser')
    fight_table = fight_soup.find_all("table", class_="b-fight-details__table")
    if len(fight_table) < 2:
        print(f' broken url: {url}')
        return []
    totals_round_rows = fight_table[0].find_all("tr", class_="b-fight-details__table-row")
    sig_round_rows = fight_table[1].find_all("tr", class_="b-fight-details__table-row")
    totals = round_stats(totals_round_rows, fight_ID)
    sigs = round_stats(sig_round_rows, fight_ID)
    cleaned_rounds = clean_round(totals, sigs)
    return cleaned_rounds

def flatten(list_of_lists):
    flattened_list = []
    for nested in list_of_lists:
        flattened_list.extend(nested)
    return flattened_list

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
    start = time.time()
    # Get card links
    fight_cards = card_finder(ufc_stats)[1:-30]

    # Fetch fight links concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        fight_links = list(executor.map(get_fight_links, fight_cards))

    # Flatten the list of lists of fight links
    flat_fight_links = flatten(fight_links)

    # Retrieve stats concurrently
    fight_stats = get_stats(flat_fight_links)

    # Create and save the dataframe
    fight_df = create_dataframe(fight_stats)
    fight_df.to_csv('bound_statistics.csv', index=False)
    end = time.time()
    print(f'Time taken: {end - start:.2f} seconds')


if __name__ == "__main__":
    main()
