import json
import sys

from utils import DB_FILE, Connection, fetch_json

NUM_ENTRIES = 25
BASE_URL = "https://www.balldontlie.io/api/v1"
PLAYERS_URL = f"{BASE_URL}/players"
STATS_URL = f"{BASE_URL}/stats"
CALC_FILE = "balldontlie_data.json"


def create_tables(conn: Connection):
    conn.write("""CREATE TABLE IF NOT EXISTS Stat (id INTEGER PRIMARY KEY, player_id INTEGER, team_id INTEGER, game_id INTEGER, ft_pct REAL, fg_pct REAL, fg3_pct REAL)""")
    conn.write("""CREATE TABLE IF NOT EXISTS Player (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, team_id INTEGER, page INTEGER)""")
    conn.write("""CREATE TABLE IF NOT EXISTS Team (id INTEGER PRIMARY KEY, abbreviation TEXT, full_name TEXT)""")
    conn.write("""CREATE TABLE IF NOT EXISTS Game (id INTEGER PRIMARY KEY, date TEXT, season INTEGER, home_team_id INTEGER, home_team_score INTEGER, visitor_team_id INTEGER, visitor_team_score INTEGER)""")


def get_and_update_page(conn: Connection, player_id: int, per_page: int) -> int:
    page = conn.read("SELECT page FROM Player WHERE id = ?",
                     (player_id,))[0][0]
    if page:
        conn.write("UPDATE Player SET page = ? WHERE id = ?",
                   (page + 1, player_id))
        return page
    stats = fetch_json(STATS_URL, {"player_ids[]": player_id, "per_page": per_page})
    page = stats["meta"]["total_pages"] // 2
    conn.write("UPDATE Player SET page = ? WHERE id = ?",
               (page + 1, player_id))
    return page


def get_and_store_player_by_name(conn: Connection, name: str) -> int:
    player = fetch_json(PLAYERS_URL, {"search": name})
    if player["data"] == []:
        raise RuntimeError("Player not found")
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


def store_all_stats_for_player(conn: Connection, per_page: int, player_id: int) -> int:
    count = 0
    page = get_and_update_page(conn, player_id, per_page)
    stats = fetch_json(STATS_URL, {"page": page, "per_page": per_page, "player_ids[]": player_id})
    if stats["data"] == []:
        print(f"No stats found for player {player_id} on page {page}", file=sys.stderr)
        return 0
    stats = stats["data"]
    for stat in stats:
        if any(stat[key] is None for key in ("ft_pct", "fg_pct", "fg3_pct")):
            continue
        store_game(conn, stat["game"])
        store_team(conn, stat["team"])
        store_stat(conn, stat)
        count += 1
    print(f"Stored {count} stats for player {player_id} from page {page}")
    return count


def calculate_avg_pcts(conn: Connection) -> list[tuple]:
    data = conn.read(
        """
        SELECT Player.first_name || " " || Player.last_name, AVG(Stat.ft_pct), AVG(Stat.fg_pct), AVG(Stat.fg3_pct) FROM Stat
        JOIN Player ON Stat.player_id = Player.id
        GROUP BY Player.id
        """
    )
    return data


def write_averages(stats: list[tuple]):
    ave_dict = {"players": {name: {}} for name in {stat[0] for stat in stats}}
    for stat in stats:
        name, ft_pct, fg_pct, fg3_pct = stat
        ft_pct, fg_pct, fg3_pct = round(ft_pct * 100, 2), round(fg_pct * 100, 2), round(fg3_pct * 100, 2)
        ave_dict["players"][name] = {"ave": {"ft_pct": ft_pct, "fg_pct": fg_pct, "fg3_pct": fg3_pct}}

    with open(CALC_FILE, "w", encoding='utf-8') as file:
        json.dump(ave_dict, file)


def calculate_games_played(conn: Connection) -> list[tuple]:
    data = conn.read(
        """
        SELECT Player.first_name || " " || Player.last_name, COUNT(Game.id) FROM Stat
        JOIN Player ON Stat.player_id = Player.id
        JOIN Game ON Stat.game_id = Game.id
        GROUP BY Player.id
        """
    )
    return data


def write_games_played(stats: list[tuple]):
    with open(CALC_FILE, "r", encoding='utf-8') as file:
        json_data = json.load(file)

    json_data["meta"] = json_data.get("meta", {}) | {"total_games": sum(stat[1] for stat in stats)}
    for stat in stats:
        name, games_played = stat
        json_data["players"][name]["games_played"] = games_played

    with open(CALC_FILE, "w", encoding='utf-8') as file:
        json.dump(json_data, file)


def main():
    conn = Connection(DB_FILE)
    players = [
        "LeBron James",
        "Michael Jordan",
        "Kobe Bryant",
    ]

    create_tables(conn)

    ids = [get_and_store_player_by_name(conn, player) for player in players]

    total_stored_this_run = sum(
       store_all_stats_for_player(conn, NUM_ENTRIES // len(players), id)
       for id in ids
    )

    total_count = conn.read("SELECT COUNT(*) FROM Stat")[0][0]

    print(f"Stored {total_stored_this_run} entries into {DB_FILE}")
    print(f"Total entries in {DB_FILE}: {total_count}/100")

    averages = calculate_avg_pcts(conn)
    write_averages(averages)

    games_played = calculate_games_played(conn)
    write_games_played(games_played)

    print(f"Wrote calculated data to {CALC_FILE} cache file")


if __name__ == "__main__":
    main()
