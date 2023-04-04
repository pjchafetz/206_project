from utils import Connection, fetch_json


def main():
    conn = Connection("database.db")
    print(fetch_json("https://catfact.ninja/fact"))


if __name__ == "__main__":
    main()
