import datetime
import sqlite3
import time

import pandas as pd
import requests
from pycoingecko import CoinGeckoAPI

from utils import DB_FILE


class DataFetcher:

    API_KEY = "KSQ8WYQPVF6ZXZ5G" #for alpha_vantage stocks
    cg = CoinGeckoAPI()

    def __init__( self, sp500_symbol = "SPY", bitcoin_symbol = "BTC"):

        self.sp500_symbol = sp500_symbol
        self.bitcoin_symbol = bitcoin_symbol

    def main(self):

        self.create_table("sp500", "stock")
        self.create_table("bitcoin", "crypto")

        sp500_data_points_count = self.get_data_points_count("sp500")
        bitcoin_data_points_count = self.get_data_points_count("bitcoin")

        #below ensures we fetch exactly 25 at a time for a total of 200 datapoints

        #fetch 25 sp500 datapoints if we do not already have 100 sp500 data points, else fetch none
        if sp500_data_points_count < 100:
            sp500_data_points, sp500_start, sp500_end = self.store_and_update(self.sp500_symbol, "stock", "sp500")
        else:
            sp500_data_points, sp500_start, sp500_end = sp500_data_points_count, None, None

        #fetch 25 bitcoin datapoints if we already have 1000 sp500 data points and we do not already have 100 bitcoin datapoints, else fetch none
        if bitcoin_data_points_count < 100 and sp500_data_points_count >= 100:
            bitcoin_data_points, bitcoin_start, bitcoin_end = self.store_and_update("BTC", "crypto", "bitcoin")
        else:
            bitcoin_data_points, bitcoin_start, bitcoin_end = bitcoin_data_points_count, None, None

        self.print_summary(sp500_data_points, bitcoin_data_points, sp500_start, sp500_end, bitcoin_start, bitcoin_end)


    def create_table(self, table_name, data_type):
        columns = {
            "stock": '''id INTEGER PRIMARY KEY, date TEXT, month INTEGER, close REAL, adjusted_close REAL''',
            "crypto": '''id INTEGER PRIMARY KEY, price REAL, month INTEGER, date TEXT''',
        }
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns[data_type]})")
        conn.commit()
        conn.close()

    def clean_data(self, data, data_type):

        if data_type == "crypto":
            data = data[['price']]
            data.columns = ['price']
        else:
            data = data[['4. close', '5. adjusted close']]
            data.columns = ['close', 'adjusted_close']

        return data

    def get_bitcoin_weekly_data(self, start_date):

        start_date = datetime.date(2020, 1, 1) if start_date is None else start_date
        end_date = datetime.date(2021, 12, 31)

        start_datetime = datetime.datetime.combine(start_date, datetime.time())
        end_datetime = datetime.datetime.combine(end_date, datetime.time())

        data = self.cg.get_coin_market_chart_range_by_id( id = 'bitcoin', vs_currency = 'usd', from_timestamp = start_datetime.timestamp(), to_timestamp = end_datetime.timestamp(), resolution = 'daily')
    
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date

        df['date'] = pd.to_datetime(df['date'])
        weekly_df = df[df['date'].dt.weekday == 0]  #fetch all Mondays in this year (2020 or 2021)

        #skip over already collected data
        if start_date is not None:
            weekly_df = weekly_df[weekly_df['date'] >= pd.to_datetime(start_date)]

        weekly_df = weekly_df.iloc[:25]  #keep only the first 25 points
        weekly_df.set_index('date', inplace=True)
        return weekly_df

    def fetch_and_clean_data(self, symbol, data_type, start_date, end_date):


        if data_type == "crypto" and symbol == "BTC":
            data = self.get_bitcoin_weekly_data(start_date = start_date)
            return self.clean_data(data, data_type)
        else:
            function = "TIME_SERIES_WEEKLY_ADJUSTED"
            key = "Weekly Adjusted Time Series"
            url = f"https://www.alphavantage.co/query?function={function}&symbol={symbol}&apikey={self.API_KEY}"

            response = requests.get(url)
            json_data = response.json()

            if "Error Message" in json_data:
                raise ValueError(f"Error fetching data for {symbol}: {json_data['Error Message']}")

            data = pd.DataFrame(json_data[key]).T
            data.index = pd.to_datetime(data.index)
            data = data.sort_index()
            data = data.loc[start_date:end_date]

            return self.clean_data(data, data_type)

    def fetch_and_clean_data_with_retry(self, symbol, data_type, start_date, end_date):

        retries, max_retries = 0, 3
        while retries < max_retries:
            try:
                data = self.fetch_and_clean_data(symbol, data_type, start_date, end_date)
                return data
            except ValueError as e:
                print(f"Error fetching data: {e}. Retrying... ({retries + 1}/{max_retries})")
                retries += 1
            time.sleep(2)  # wait for 2 seconds before retrying

        if retries == max_retries:
            raise ValueError(f"Failed to fetch data for {symbol} after {max_retries} attempts.")

    def store_data(self, data, table_name, data_type):

        data.index = data.index.astype(str)
        with sqlite3.connect(DB_FILE) as conn:

            cursor = conn.cursor()

            for date_str in data.index:
                data_row = data.loc[date_str]
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

                #column names based on the data_type
                if data_type == "crypto":
                    columns = 'price, month, date'
                else:
                    columns = 'close, adjusted_close, month, date'

                #concise way of writing the SQL command via the join() method
                values = ",".join(str(value) for value in data_row.values)
                month = date.month
                cursor.execute(f"INSERT OR IGNORE INTO {table_name} ({columns}) VALUES ({values}, {month}, '{date_str}')")
            conn.commit()

    def store_and_update(self, symbol, data_type, table_name):

        latest_date = self.get_latest_date(table_name)
        if latest_date is not None:
            #when the database is NOT empty, start at the most recent date (i.e. latest_date)
            latest_date = datetime.datetime.strptime(latest_date, "%Y-%m-%d").date()
            start_date = latest_date + datetime.timedelta(days=1)
            end_date = start_date + datetime.timedelta(days=365)

        else:
            #when the database is EMPTY, start at the beginning of 2020
            start_date = datetime.date(2020, 1, 1)
            end_date = datetime.date(2021, 12, 31)

        data = self.fetch_and_clean_data_with_retry(symbol, data_type, start_date, end_date)

        #limit the data points to 25 total per run
        filtered_data = data.iloc[:25]
        self.store_data(filtered_data, table_name, data_type)

        total_data_points = self.get_data_points_count(table_name)

        return total_data_points, start_date, filtered_data.index[-1] #end_date

    def get_latest_date(self, table_name):

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(f"SELECT MAX(date) FROM {table_name}")
        latest_date = c.fetchone()[0]
        conn.close()
        return str(latest_date) if latest_date else None

    def get_data_points_count(self, table_name):

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_data_points = c.fetchone()[0]
        conn.close()
        return total_data_points

    def print_summary(self, sp500_data_points, bitcoin_data_points, sp500_start, sp500_end, bitcoin_start, bitcoin_end):

        print(f"Total data points for S&P 500 API: {sp500_data_points}")
        print(f"Total data points for Bitcoin API: {bitcoin_data_points}")

        remaining_data_points = 200 - ( sp500_data_points + bitcoin_data_points )
        print(f"Data saved for S&P 500 from {sp500_start} to {sp500_end}")
        print(f"Data saved for Bitcoin from {bitcoin_start} to {bitcoin_end}")

        if remaining_data_points <= 0:
            print("DONE! All data saved, time for the calculation file.")
        else:
            print(f"Remaining data points to collect: {remaining_data_points}")

def main():

    data_fetcher = DataFetcher()
    data_fetcher.main()

if __name__ == "__main__":
    main()