import json

import matplotlib.pyplot as plt

from balldontlie import CALC_FILE


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
    with open(CALC_FILE, "r", encoding='utf-8') as file:
        data = json.load(file)
    plot(data)


if __name__ == "__main__":
    main()
