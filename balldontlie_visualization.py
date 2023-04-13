import matplotlib.pyplot as plt

from utils import Connection, fetch_json


DB_NAME = "database.db"


def main():
    conn = Connection(DB_NAME)


if __name__ == "__main__":
    main()
