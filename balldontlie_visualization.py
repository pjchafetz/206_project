import json

import matplotlib.pyplot as plt

CALC_FILE = "bdl_data.json"


def plot(data: dict[str, dict]):
    _, axes = plt.subplots(1, 4, figsize=(19, 6))

    titles = [
        "Average Free Throw Percentage",
        "Average Field Goal Percentage",
        "Average 3-Point Field Goal Percentage",
        "Games Played in This Dataset"
    ]
    
    for index, ax in enumerate(axes):
        ax.set_title(titles[index])
        if index == len(axes) - 1:
            ax.set_ylabel("Games Played")
        else:
            ax.set_ylabel("Percentage")
            ax.set_ylim(0, 100)

    for player in data["players"]:
        for ax, stat in zip(axes, data["players"][player]["ave"]):
            bar = ax.bar(player, data["players"][player]["ave"][stat])
            ax.bar_label(bar)
        bar = axes[-1].bar(player, data["players"][player]["games_played"])
        axes[-1].bar_label(bar)

    plt.show()


def main():

    with open(CALC_FILE, "r") as f:
        data = json.load(f)
    plot(data)


if __name__ == "__main__":
    main()
