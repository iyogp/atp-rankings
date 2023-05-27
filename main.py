import os
import logging
from concurrent.futures import ThreadPoolExecutor

from extract import get_rank_dates, scrape_atp_rankings
import pandas as pd

format = "%(asctime)s - %(levelname)s : %(message)s"
logging.basicConfig(level=logging.INFO, format=format)


COLUMNS = ['week', 'rank', 'name', 'age', 'move', 'country', 'points', 'tourns']


def append(df, data, data_type="records"):
    if data_type == "dataframe":
        return pd.concat([df, data])
    elif data_type == "records":
        return pd.concat([df, pd.DataFrame.from_records(data)])
    else:
        raise Exception(f"Unknown data_type: {data_type}")

def main(rank_dates):
    '''wrapper for scrapping atp rankings on a set of rank dates'''
    df1 = pd.DataFrame(columns=COLUMNS)
    for rank_date in rank_dates:
        data = scrape_atp_rankings(rank_date)
        df1 = append(df1, data, data_type="records")
    return df1

if __name__ == "__main__":
    logging.info(">>> ATP Ranking Scrapper Started <<<")
    rank_dates = get_rank_dates()
    chunk_rank_dates = []
    chunk_size = 100
    for i in range(0, len(rank_dates), chunk_size):
        chunk_rank_dates.append(rank_dates[i:i+chunk_size])
    with ThreadPoolExecutor() as executor:
        results = executor.map(main, chunk_rank_dates)
    df = pd.DataFrame(columns=COLUMNS)
    for result in results:
        df = append(df, result, data_type="dataframe")
    cwd = os.getcwd() # get absolute path of cwd
    output_path = os.path.join(cwd, "data", "atp_rankings.csv") # ~/atp-rankings/data/atp_rankings.csv
    df.to_csv(output_path)
    logging.info("<<< ATP Ranking Scrapper Finished >>>")