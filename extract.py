import os
import requests
import logging

from bs4 import BeautifulSoup


format = "%(asctime)s - %(levelname)s : %(message)s"
logging.basicConfig(level=logging.INFO, format=format)

URL = "https://www.atptour.com/en/rankings/singles?rankRange=0-250&rankDate=$week_to_extract"
HEADERS = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
USER_AGENT = os.getenv("USER_AGENT")

YEAR_LIMIT = 2005 # collect ATP rankings data from 2005 to current


def clean_string(some_string):
    return some_string.strip()

def get_table_rows(table, row_type):
    return table.find(row_type).find_all('tr')

def get_table_data(soup):
    table = soup.find('table', {'id': 'player-rank-detail-ajax'})
    head = get_table_rows(table, 'thead')
    body = get_table_rows(table, 'tbody')
    return (table, head, body)

def get_rank(row):
    rank_cell = row.find('td', {'class': "rank-cell"})
    rank = rank_cell.get_text()
    return clean_string(rank)

def get_player_name(row):
    player_cell = row.find('td', {'class': "player-cell"})
    player_name = player_cell.find('a').get_text()
    return clean_string(player_name)

def get_move_cell(row):
    move_types = ["move-none", "move-up", "move-down"]
    move_cell = row.find('td', {'class': "move-cell"})
    for move_type in move_types:
        move = move_cell.find('span', {'class': move_type})
        if move != None:
            if move_type == "move-none":
                return None
            else:
                return clean_string(move.get_text())
            
def get_country(row):
    country_cell = row.find('td', {'class': "country-cell"})
    country = country_cell.find('img')['alt']
    return clean_string(country)

def get_age(row):
    age_cell = row.find('td', {'class': "age-cell"})
    age = int(clean_string(age_cell.get_text()))
    return age

def get_points(row):
    points_cell = row.find('td', {'class': "points-cell"})
    points = clean_string(points_cell.find('a').get_text().replace(",", ""))
    return points

def get_tourns_played(row):
    tourn_cell = row.find('td', {'class': 'tourn-cell'})
    tourn = int(clean_string(tourn_cell.find('a').get_text()))
    return tourn

def extract(row):
    rank = get_rank(row)
    name = get_player_name(row)
    age = get_age(row)
    move = get_move_cell(row)
    country = get_country(row)
    points = get_points(row)
    tourns = get_tourns_played(row)
    data = {
        'rank': rank,
        'name': name,
        'age': age,
        'move': move,
        'country': country,
        'points': points,
        'tourns': tourns
    }
    return data

def _process_rank_dates(li_rank_dates):
    rank_dates = []
    for rank_date in li_rank_dates:
        _rank_date = clean_string(rank_date.get_text()).replace(".", "-")
        rank_year = int(_rank_date[:4])
        if rank_year < YEAR_LIMIT:
            break
        rank_dates.append(_rank_date)
    return rank_dates

def get_current_week(soup):
    week_tag = soup.find('ul', {'class': 'dropdown', 'data-value': 'rankDate'})
    current_week = clean_string(week_tag.find('li', {'class': 'current'}).get_text())
    return current_week.replace(".", "_")

def get_rank_dates(current=False):
    url = URL.replace("/$week_to_extract", "")
    response = requests.get(url, headers=HEADERS)
    content = response.content
    soup = BeautifulSoup(content, 'html.parser')
    if current == True:
        current_week = get_current_week(soup)
        return current_week
    ul_rank_dates = soup.find('ul', {'data-value': "rankDate"})
    li_rank_dates = ul_rank_dates.find_all("li")
    rank_dates = _process_rank_dates(li_rank_dates)
    return rank_dates

def scrape_atp_rankings(week_to_extract):
    logging.info(f"Scrapping ATP rankings for {week_to_extract}...")
    url = URL.replace("$week_to_extract", week_to_extract)
    response = requests.get(url, headers=HEADERS)
    content = response.content
    soup = BeautifulSoup(content, 'html.parser')
    _, _, body = get_table_data(soup)
    data = []
    for row in body:
        result = extract(row)
        result.update({'week': week_to_extract})
        data.append(result)
    return data
