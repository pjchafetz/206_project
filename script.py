import json
import requests
import sqlite3


class Connection:
    def __init__(self, filename: str) -> None:
        self.conn = sqlite3.connect(filename)
        self.cur = self.conn.cursor()

    def __del__(self) -> None:
        self.conn.close()

    def read(self, query: str, inputs: tuple) -> list:
        self.cur.execute(query, inputs)
        return self.cur.fetchall()

    def write(self, query: str, inputs: tuple) -> None:
        self.cur.execute(query, inputs)
        self.conn.commit()


def fetch(url: str, params: dict = None):
    response = requests.get(url, params)
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code} - {response.reason}")
    return response.json()


def main():
    conn = Connection("database.db")
    print(fetch("https://catfact.ninja/fact"))


if __name__ == "__main__":
    main()
