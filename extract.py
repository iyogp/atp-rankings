import os
import requests

from dotenv import load_dotenv
from bs4 import BeautifulSoup
# import pandas as pd


load_dotenv()

URL = os.getenv("URL")
TABLE_ID = os.getenv("TABLE_ID")
USER_AGENT = os.getenv("USER_AGENT")


MAPPING = {
    "RANK": "rank-cell", 
    "MOVE": "move-cell", 
    "COUNTRY": "country-cell", 
    "PLAYER": "player-cell", 
    "AGE": "age-cell", 
    "POINTS": "points-cell", 
    "POINTS MOVE": "points-move-cell", 
    "TOURNAMENT_PLAYED": "tourn-cell"
}


def get_table_rows(table, row_type):
    return table.find(row_type).find_all('tr')

def get_table_data(soup):
    table = soup.find('table', {'id': TABLE_ID})
    head = get_table_rows(table, 'thead')
    body = get_table_rows(table, 'tbody')
    return (table, head, body)

def clean_string(some_string):
    return some_string.strip()

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


if __name__ == "__main__":
    headers = {'User-Agent': USER_AGENT}

    response = requests.get(URL, headers=headers)
    content = response.content

    soup = BeautifulSoup(content, 'html.parser')

    table, head, body = get_table_data(soup)

    for row in body:
        name = get_player_name(row)
        move = get_move_cell(row)
        print(name, move)
