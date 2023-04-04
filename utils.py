import sqlite3

import requests


class Connection:
    def __init__(self, filename: str) -> None:
        self._filename = filename
        self.conn = sqlite3.connect(self._filename)
        self.cur = self.conn.cursor()

    def __del__(self) -> None:
        self.conn.close()
        
    def __str__(self) -> None:
        return f"Database connection to {self._filename}"

    def read(self, query: str, inputs: tuple) -> list:
        self.cur.execute(query, inputs)
        return self.cur.fetchall()

    def write(self, query: str, inputs: tuple) -> None:
        self.cur.execute(query, inputs)
        self.conn.commit()


def fetch_json(url: str, params: dict = None):
    response = requests.get(url, params)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.reason}")
    return response.json()
