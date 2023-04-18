import json

import matplotlib.pyplot as plt

from balldontlie import CALC_FILE, DB_FILE
from utils import Connection


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
        ave_dict["players"][name] = {
            "ave": {"ft_pct": ft_pct, "fg_pct": fg_pct, "fg3_pct": fg3_pct}}

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


def plot(data: dict[str, dict]):
    _, axes = plt.subplots(1, 4, figsize=(19, 6))

    titles = [
        "Average Free Throw Percentage",
        "Average Field Goal Percentage",
        "Average 3-Point Field Goal Percentage",
        "Games Played in This Dataset"
    ]

    for index, axis in enumerate(axes):
        axis.set_title(titles[index])
        if index == len(axes) - 1:
            axis.set_ylabel("Games Played")
        else:
            axis.set_ylabel("Percentage")
            axis.set_ylim(0, 100)

    for player in data["players"]:
        for axis, stat in zip(axes, data["players"][player]["ave"]):
            bar_container = axis.bar(player, data["players"][player]["ave"][stat])
            axis.bar_label(bar_container)
        bar_container = axes[-1].bar(player, data["players"][player]["games_played"])
        axes[-1].bar_label(bar_container)

    plt.show()


def main():
    conn = Connection(DB_FILE)

    averages = calculate_avg_pcts(conn)
    write_averages(averages)

    games_played = calculate_games_played(conn)
    write_games_played(games_played)

    print(f"Wrote calculated data to {CALC_FILE} cache file")

    with open(CALC_FILE, "r", encoding='utf-8') as file:
        data = json.load(file)
    plot(data)


if __name__ == "__main__":
    main()
