import sys

from utils import Connection, fetch_json

BASE_URL = "https://www.balldontlie.io/api/v1"
PLAYERS_URL = f"{BASE_URL}/players"
STATS_URL = f"{BASE_URL}/stats"


def create_tables(conn: Connection):
    conn.write("""CREATE TABLE IF NOT EXISTS Stat (id INTEGER PRIMARY KEY, player_id INTEGER, team_id INTEGER, game_id INTEGER, ft_pct REAL, fg_pct REAL, fg3_pct REAL)""")
    conn.write("""CREATE TABLE IF NOT EXISTS Player (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, team_id INTEGER)""")
    conn.write("""CREATE TABLE IF NOT EXISTS Team (id INTEGER PRIMARY KEY, abbreviation TEXT, full_name TEXT)""")
    conn.write("""CREATE TABLE IF NOT EXISTS Game (id INTEGER PRIMARY KEY, date TEXT, season INTEGER, home_team_id INTEGER, home_team_score INTEGER, visitor_team_id INTEGER, visitor_team_score INTEGER)""")


def get_and_update_page() -> int:
    FILENAME = "balldontlie"
    try:
        with open(FILENAME, "r") as f:
            page = int(f.read())
    except:
        page = 1
    try:
        with open("balldontlie", "w") as f:
            f.write(str(page + 1))
    except:
        raise Exception(f"Error writing to file {FILENAME} with page {page}")
    return page


def get_and_store_player_by_name(conn: Connection, name: str) -> int:
    player = fetch_json(PLAYERS_URL, {"search": name})
    if player["data"] == []:
        raise Exception("Player not found")
    player = player["data"][0]
    conn.write("""INSERT OR IGNORE INTO Player (id, first_name, last_name, team_id) VALUES (?, ?, ?, ?)""",
               (player["id"], player["first_name"], player["last_name"], player["team"]["id"]))
    return player["id"]


def store_stat(conn: Connection, stat: dict):
    conn.write("""INSERT OR IGNORE INTO Stat (id, player_id, team_id, game_id, ft_pct, fg_pct, fg3_pct) VALUES (?, ?, ?, ?, ?, ?, ?)""",
               (stat["id"], stat["player"]["id"], stat["team"]["id"], stat["game"]["id"], stat["ft_pct"], stat["fg_pct"], stat["fg3_pct"]))


def store_team(conn: Connection, team: dict):
    conn.write("""INSERT OR IGNORE INTO Team (id, abbreviation, full_name) VALUES (?, ?, ?)""",
               (team["id"], team["abbreviation"], team["full_name"]))


def store_game(conn: Connection, game: dict):
    conn.write("""INSERT OR IGNORE INTO Game (id, date, season, home_team_id, home_team_score, visitor_team_id, visitor_team_score) VALUES (?, ?, ?, ?, ?, ?, ?)""",
               (game["id"], game["date"], game["season"], game["home_team_id"], game["home_team_score"], game["visitor_team_id"], game["visitor_team_score"]))


def store_all_stats_for_player(conn: Connection, page: int, player_id: int, start_date: str):
    count = 0
    stats = fetch_json(STATS_URL, {"page": page, "per_page": 25, "player_ids[]": player_id, "start_date": start_date})
    if stats["data"] == []:
        print(f"No stats found for player {player_id} on page {page}", file=sys.stderr)
        return
    stats = stats["data"]
    for stat in stats:
        if stat["ft_pct"] is None or stat["fg_pct"] is None or stat["fg3_pct"] is None:
            continue
        store_game(conn, stat["game"])
        store_team(conn, stat["team"])
        store_stat(conn, stat)
        count += 1
    print(f"Stored {count} stats for player {player_id} from page {page}")


def main():
    conn = Connection("database.db")
    LEBRON = "LeBron James"     # id 237    TODO: remove me
    MICHAEL = "Michael Jordan"  # id 2931   TODO: remove me - only has 6 pages after 2000
    KOBE = "Kobe Bryant"        # id 1043   TODO: remove me
    START_DATE = "2000-01-01"
    PAGE = get_and_update_page()

    create_tables(conn)
    ids = [
        get_and_store_player_by_name(conn, LEBRON),
        get_and_store_player_by_name(conn, MICHAEL),
        get_and_store_player_by_name(conn, KOBE),
    ]

    # use a specific (list of) season(s) - probably a bad idea
    for id in ids:
        store_all_stats_for_player(conn, PAGE, id, START_DATE)


if __name__ == "__main__":
    main()
