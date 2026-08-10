import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as ss
import random
from alive_progress import alive_bar

import sys

sys.path.insert(0, "../../elo_system")
from calculator import Player, Tournament

sys.path.insert(0, "../../../load_data")
from load import load_stats, load_history

sns.set_theme()

# ---------- Simulation Parameters ----------

players = load_stats()["Tournament Rating"]
players = players.value_counts() / len(players)
extreme = pd.Series(index=[200, 3000], data=[0.5, 0.5])

ITERATIONS = 20000
PLAYERS = 1000
INITIAL_DISTRIBUTION = players
FILE_NAME = f"sim_hist_{ITERATIONS}_{PLAYERS}p_extreme"


# ---------- Tournaments ----------

population = [
    Player(id=i, rating=rating)
    for i, rating in enumerate(
        random.choices(
            INITIAL_DISTRIBUTION.index,
            weights=INITIAL_DISTRIBUTION.values,
            k=PLAYERS,
        )
    )
]


def win_probability(rating_spread, k=121.37092754):
    return 1 / (1 + 10 ** (rating_spread / k))


def simulate_tournament(players_per_tournament=30, matches_per_tournament=10):
    players = random.sample(population, players_per_tournament)
    tournament = Tournament(population)

    for player in players:
        for i in range(matches_per_tournament):
            opponent_rating = random.choices(
                [p.rating for p in players if p != player], k=1
            )[0]

            rating_spread = opponent_rating - player.rating
            win_prob = win_probability(rating_spread)
            lose_prob = 1 - win_prob

            possible_results = ["wins", "losses"]
            result = random.choices(possible_results, weights=[win_prob, lose_prob])[0]

            tournament.all_results[player][result].append(opponent_rating)

    return tournament


# ---------- Run Simulation ----------
simulation_history = [[player.rating for player in population]]
with alive_bar(ITERATIONS) as bar:
    for _ in range(ITERATIONS):
        tournament = simulate_tournament()
        tournament.full_pass()
        simulation_history.append([player.rating for player in population])
        bar()


# ---------- Visualize Results ----------

plt.figure(figsize=(12, 6))
sns.histplot(
    simulation_history[0],
    bins=50,
    kde=True,
    color="blue",
    label="Initial Ratings",
    alpha=0.5,
)
sns.histplot(
    simulation_history[-1],
    bins=50,
    kde=True,
    color="red",
    label="Final Ratings",
    alpha=0.5,
)
plt.legend()
plt.show()
