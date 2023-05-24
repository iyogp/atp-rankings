import os
import requests
import logging

from bs4 import BeautifulSoup
import pandas as pd


format = "%(asctime)s - %(levelname)s : %(message)s"
logging.basicConfig(level=logging.INFO, format=format)


URL = "https://www.atptour.com/en/rankings/singles?rankRange=0-250"
USER_AGENT = os.getenv("USER_AGENT")


def clean_string(some_string):
    return some_string.strip()

def get_table_rows(table, row_type):
    return table.find(row_type).find_all('tr')

def get_table_data(soup):
    table = soup.find('table', {'id': 'player-rank-detail-ajax'})
    head = get_table_rows(table, 'thead')
    body = get_table_rows(table, 'tbody')
    return (table, head, body)

def get_current_week(soup):
    week_tag = soup.find('ul', {'class': 'dropdown', 'data-value': 'rankDate'})
    current_week = clean_string(week_tag.find('li', {'class': 'current'}).get_text())
    return current_week.replace(".", "_")

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

def transform(row):
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
    

if __name__ == "__main__":
    logging.info("-"*50)
    logging.info(">>> Started ATP Rankings Scrapper")

    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    response = requests.get(URL, headers=headers)
    content = response.content

    soup = BeautifulSoup(content, 'html.parser')

    current_week = get_current_week(soup)

    logging.info("-"*50)
    logging.info(f"Scrapping ATP rankings for week: {current_week}")

    _, _, body = get_table_data(soup)

    data = []
    for row in body:
        result = transform(row)
        data.append(result)
    
    df = pd.DataFrame.from_records(data)
    
    cwd = os.getcwd()
    filename = f"rankings-{current_week.lower()}.csv"
    output_path = os.path.join(cwd, "data", filename)

    df.to_csv(output_path)

    logging.info(f"Output File: {output_path}")
    logging.info("-"*50)

    logging.info(">>> Finished ATP Rankings Scrapper")
    logging.info("-"*50)
