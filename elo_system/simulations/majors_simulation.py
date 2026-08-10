import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as ss

sns.set_theme()


import sys

sys.path.insert(0, "../../elo_system")
from calculator import Player, Tournament

import random
from alive_progress import alive_bar

import sys

sys.path.insert(0, "../../../load_data")
from load import load_stats, load_history

# ---------- Load Data ----------
aurora_cup = pd.read_csv("../major_tournament_history_data/aurora_cup.csv")[
    "Initial Rating"
]
bttc = pd.read_csv("../major_tournament_history_data/bttc.csv")["Initial Rating"]
edgeball = pd.read_csv("../major_tournament_history_data/edgeball.csv")[
    "Initial Rating"
]
icc = pd.read_csv("../major_tournament_history_data/icc.csv")["Initial Rating"]
la_open = pd.read_csv("../major_tournament_history_data/la_open.csv")["Initial Rating"]
na_teams = pd.read_csv("../major_tournament_history_data/na_teams.csv")[
    "Initial Rating"
]
nationals = pd.read_csv("../major_tournament_history_data/nationals.csv")[
    "Initial Rating"
]
open = pd.read_csv("../major_tournament_history_data/open.csv")["Initial Rating"]
trials = pd.read_csv("../major_tournament_history_data/trials.csv")["Initial Rating"]
westchester = pd.read_csv("../major_tournament_history_data/westchester.csv")[
    "Initial Rating"
]

aurora_cup = aurora_cup.value_counts() / len(aurora_cup)
bttc = bttc.value_counts() / len(bttc)
edgeball = edgeball.value_counts() / len(edgeball)
icc = icc.value_counts() / len(icc)
la_open = la_open.value_counts() / len(la_open)
na_teams = na_teams.value_counts() / len(na_teams)
nationals = nationals.value_counts() / len(nationals)
open = open.value_counts() / len(open)
trials = trials.value_counts() / len(trials)
westchester = westchester.value_counts() / len(westchester)

players = load_stats()["Tournament Rating"]
players = players.value_counts() / len(players)

uniform = pd.Series(index=np.arange(3000), data=1 / 3000)
middle = pd.Series(index=[2250], data=[1])
extreme = pd.Series(index=[200, 3000], data=[0.5, 0.5])

# ---------- Simulation Parameters ----------

ITERATIONS = 18000
YEARS = 50
MATCHES_PER_TOURNAMENT = 10
INITIAL_DISTRIBUTION = extreme
FILE_NAME = f"sim_hist_{ITERATIONS}_{YEARS}y_{MATCHES_PER_TOURNAMENT}m_extreme"

# ---------- Tournaments ----------
schedule = [
    [westchester, bttc],
    [westchester, bttc],
    [westchester, icc, bttc],
    [westchester, bttc],
    [trials, westchester, edgeball, aurora_cup, bttc],
    [westchester, icc, bttc],
    [nationals, westchester, bttc],
    [westchester, la_open, bttc],
    [westchester, bttc],
    [westchester, icc, bttc],
    [westchester, na_teams, bttc],
    [open, westchester, icc, bttc],
]


def win_probability(rating_spread, k=121.37092754):
    return 1 / (1 + 10 ** (rating_spread / k))


def simulate_tournament(player, population):
    tournament = Tournament([player])

    for i in range(MATCHES_PER_TOURNAMENT):
        opponent_rating = random.choices(population.index, weights=population.values)[0]

        rating_spread = opponent_rating - player.rating
        win_prob = win_probability(rating_spread)
        lose_prob = 1 - win_prob

        possible_results = ["wins", "losses"]
        result = random.choices(possible_results, weights=[win_prob, lose_prob])[0]

        tournament.all_results[player][result].append(opponent_rating)

    return tournament


# ---------- Run Simulation ----------

simulation_history = []

with alive_bar(ITERATIONS) as bar:
    for i in range(ITERATIONS):
        initial_rating = random.choices(
            INITIAL_DISTRIBUTION.index, weights=INITIAL_DISTRIBUTION.values
        )[0]

        player = Player(id=i, rating=initial_rating)
        rating_history = [initial_rating]

        for j in range(YEARS):
            for month in range(12):
                # choose tournament to play in given month at random
                population = random.choice(schedule)[0]

                # simulate chosen tournament being played
                tournament = simulate_tournament(player, population)

                # update ratings
                tournament.full_pass()
                player = tournament.players[0]

                # keep track of rating history
                rating_history.append(player.rating)

        simulation_history.append(rating_history)
        bar()

simulation_history_df = pd.DataFrame(
    columns=[f"Month {i}" for i in range(YEARS * 12 + 1)], data=simulation_history
)

simulation_history_df.to_csv(f"./outputs/{FILE_NAME}.csv", index=False)

plt.figure(figsize=(10, 7))

plt.subplot(2, 2, 1)
sns.histplot(data=simulation_history_df, x=f"Month {YEARS * 12}")
plt.xlabel("Rating")

plt.subplot(2, 2, 2)
sns.histplot(data=simulation_history_df, x="Month 0", label="Month 0")
sns.histplot(
    data=simulation_history_df, x=f"Month {YEARS * 12}", label=f"Month {YEARS * 12}"
)
plt.legend()
plt.xlabel("Rating")

plt.subplot(2, 2, 3)
sns.lineplot(data=simulation_history_df.mean(axis=0))
plt.xlabel("Year")
plt.ylabel("Mean")
plt.xticks(np.arange(0, YEARS * 12, 12), np.arange(YEARS))

plt.subplot(2, 2, 4)
sns.lineplot(data=simulation_history_df.std(axis=0))
plt.xlabel("Year")
plt.ylabel("Standard Deviation")
plt.xticks(np.arange(0, YEARS * 12, 12), np.arange(YEARS))

plt.show()
