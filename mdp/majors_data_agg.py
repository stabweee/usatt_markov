import numpy as np
import pandas as pd

import sys

sys.path.insert(0, "data")
from load import load_stats, load_history

pd.options.mode.chained_assignment = None

history = load_history()


def list_to_regex_str(arr):
    res = ""
    for name in arr:
        res += name + "|"

    return res[:-1]


def tournament_to_csv(history, name, include, exclude):
    include_str = list_to_regex_str(include)
    exclude_str = list_to_regex_str(exclude)

    tournament = history[
        history["Tournament"].str.contains(
            include_str, regex=True, na=False, case=False
        )
    ]
    tournament = tournament[
        ~tournament["Tournament"].str.contains(
            exclude_str, regex=True, na=False, case=False
        )
    ]

    tournament.to_csv(
        r"./mdp/major_tournament_history_data/" + name + ".csv",
        index=False,
    )


nationals = [
    "nationals",
    [
        "Nationals",
        "National Table Tennis Championship",
        "Table Tennis National Championship",
        "National Championship",
    ],
    ["Team Trials", "Regional"],
]

open = [
    "open",
    [
        "US Open",
        "U.S. Open",
    ],
    ["Team Trials", "Regional"],
]

trials = [
    "trials",
    ["Team Trials"],
    ["Regional"],
]

westchester = [
    "westchester",
    [
        "Westchester",
    ],
    ["Team Trials", "Regional"],
]

icc = [
    "icc",
    [
        "ICC",
    ],
    ["Team Trials", "Regional"],
]

la_open = [
    "la_open",
    [
        "LA Open",
        "Joola LA Open",
    ],
    ["Ocala Open", "Joola Open"],
]

na_teams = [
    "na_teams",
    [
        "NA Teams",
        "North American Team",
    ],
    ["Team Trials", "Regional"],
]

edgeball = [
    "edgeball",
    ["Edgeball"],
    ["Team Trials", "Regional"],
]

aurora_cup = [
    "aurora_cup",
    ["Aurora Cup"],
    ["Team Trials", "Regional"],
]

bttc = [
    "bttc",
    ["Broward", "BTTC"],
    ["MLTT"],
]

tournament_to_csv(history, *nationals)
tournament_to_csv(history, *open)
tournament_to_csv(history, *trials)
tournament_to_csv(history, *westchester)
tournament_to_csv(history, *icc)
tournament_to_csv(history, *la_open)
tournament_to_csv(history, *na_teams)
tournament_to_csv(history, *edgeball)
tournament_to_csv(history, *aurora_cup)
tournament_to_csv(history, *bttc)
