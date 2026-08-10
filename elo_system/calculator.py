import numpy as np
import pandas as pd

from alive_progress import alive_bar


"""
class Player
    attributes:
        id - used to uniquely identify this player
        rating - rating of this player
"""


class Player:

    def __init__(self, id, rating):
        self.id = id
        self.rating = rating
        self.adjusted = False

    def __eq__(self, player):
        return self.id == player.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return str(f"{self.id}: {self.rating}")

    def __repr__(self):
        return str(f"{self.id}: {self.rating}")


"""
class Tournament
    attributes:
        players: all players in the tournament
        all_results: tournament results for all players in this tourament
        table: ratings exchange table provided by USATT
"""


class Tournament:
    """
    function __init__
        initializes tournament object, assigns values to attributes

        parameters:
            results - match results of the tournament
                      format is a dictionary with keys as players and values as {"wins": [ratings of opponents], "losses": [ratings of opponents]}
    """

    def __init__(self, players):
        self.players = players

        self.all_results = dict()
        for player in self.players:
            self.all_results[player] = {"wins": [], "losses": []}

        # ratings exchange table initialization
        point_spread_bounds = [
            (0, 12),
            (13, 37),
            (38, 62),
            (63, 87),
            (88, 112),
            (113, 137),
            (138, 162),
            (163, 187),
            (188, 212),
            (213, 237),
            (238, np.inf),
        ]
        point_spread_index = pd.IntervalIndex.from_tuples(
            point_spread_bounds, closed="both"
        )

        expected_result_rating_change = [8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 0]
        upset_result_rating_change = [8, 10, 13, 16, 20, 25, 30, 35, 40, 45, 50]

        table = pd.DataFrame(
            index=point_spread_index,
            data={
                "expected": expected_result_rating_change,
                "upset": upset_result_rating_change,
            },
        )

        self.table = table

    def __str__(self):
        return str(self.players)

    def __repr__(self):
        return str(self.players)

    """
    function exchange_chart
        follows the USATT rating exchange chart to calculate rating change

        parameters:
            player - player on which to do rating calculations on
            results - tournament results of the player

        returns:
            dictionary containing details about match results
                net change - net change in rating
                20+ point wins - number of wins with rating gain >= 20 but < 50
                50+ point wins - number of wins with rating gain >= 50
                50+ wins rating differential - total rating difference between self and opponents of all 50+ point wins
    """

    def exchange_chart(self, player, results):
        net_change = 0
        twenty_point_wins = 0
        fifty_point_wins = 0
        fifty_point_rating_differential = 0

        # rating calculation for wins
        for opponent_rating in results["wins"]:
            spread = player.rating - opponent_rating

            if spread > 0:
                rating_change = self.table.loc[spread, "expected"]
            else:
                rating_change = self.table.loc[abs(spread), "upset"]

            # extra details needed for adjustment calculations
            if 20 <= rating_change < 50:
                twenty_point_wins += 1

            if rating_change >= 50:
                fifty_point_wins += 1
                fifty_point_rating_differential += spread

            net_change += rating_change

        # rating calculation for losses
        for opponent_rating in results["losses"]:
            spread = player.rating - opponent_rating

            if spread > 0:
                rating_change = -self.table.loc[spread, "upset"]
            else:
                rating_change = -self.table.loc[abs(spread), "expected"]

            # max loss per match is 3 if rating < 100 to avoid ratings below 0
            if player.rating < 100:
                rating_change = max(rating_change, -3)

            net_change += rating_change

        return {
            "net change": net_change,
            "20+ point wins": twenty_point_wins,
            "50+ point wins": fifty_point_wins,
            "50+ wins rating differential": fifty_point_rating_differential,
        }

    """
    function special_adjustment
        special adjustment functionality under pass 1, gives rating adjustment under extraordinarily outstanding results
        also used in pass 2 for unrated players with both wins and losses

        parameters:
            player - player on which to do adjustment calculations
            results - tournament results of the player

        returns:
            new rating after calculations for adjustment/initial ratings
    """

    def special_adjustment(self, results):
        self.adjusted = True
        sorted_wins = sorted(results["wins"], reverse=True)
        sorted_losses = sorted(results["losses"])

        # ------- OWN FUNCTIONALITY, STILL WAITING ON MAYER -------
        if len(sorted_losses) == 0:
            return sorted_wins[0]
        # ---------------------------------------------------------

        if sorted_wins[0] < sorted_losses[0]:
            return np.mean(sorted_wins[0:2])

        i = 0
        j = 0
        while (
            i < len(sorted_wins)
            and j < len(sorted_losses)
            and sorted_wins[i] >= sorted_losses[j]
        ):
            i += 1
            j += 1

        return np.round(np.mean(sorted_wins[:i] + sorted_losses[:j]))

    """
    function pass1
        pass 1 of the new USATT ratings calculation, gives rating adjustments to players with outstanding results

        parameters:
            player - player on which to do adjustment calculations on
            results - tournament results of the player

        returns:
            nothing, simply adjusts rating for future rating exchange calculations
    """

    def pass1(self, player, results):
        exchange_details = self.exchange_chart(player, results)
        net_change = exchange_details["net change"]

        # standard adjustment
        if net_change > 60 or (
            net_change > 40 and exchange_details["20+ point wins"] >= 2
        ):
            player.rating += net_change

        # special adjustment
        if (
            net_change > 150
            or exchange_details["50+ point wins"] >= 3
            or (
                exchange_details["50+ point wins"] >= 2
                and exchange_details["50+ wins rating differential"] >= 700
            )
        ):
            player.rating = int(self.special_adjustment(results))

    """
    function pass2
        pass 2 of the new USATT ratings calculation, gives initial ratings to unrated players

        parameters:
            player - player on which to do initial rating calculations on
            results - tournament results of the player

        returns:
            nothing, only sets initial ratings to unrated players
    """

    def pass2(self, player, results, estimated={}):
        if len(results["wins"]) == 0 or len(results["losses"]) == 0:
            if player not in estimated:
                # ------- OWN FUNCTIONALITY, FOR SIMULATION PURPOSES -------
                player.rating = 1000
                # ---------------------------------------------------------
                # raise ValueError(f"missing estimated rating input for player {player.id}")
            else:
                player.rating = estimated[player]
        else:
            best_win = np.max(results["wins"])
            worst_loss = np.min(results["losses"])

            if worst_loss >= best_win:
                player.rating = int(best_win)
            else:
                player.rating = int(self.special_adjustment(results))

            player.rating = int(max(player.rating, 200))

    """
    function final_pass
        final pass of the new USATT ratings calculation, uses the rating exchange table to assign new ratings to all players given results

        parameters:
            player - player on which to do rating calculations on
            results - tournament results of the player

        returns:
            nothing, only assigns new ratings according to ratings exchange table
    """

    def final_pass(self, player, results):
        exchange_details = self.exchange_chart(player, results)
        player.rating += exchange_details["net change"]

    """
    function full_pass
        full pass through all passes of the new USATT ratings calculation

        parameters:
            nothing

        returns:
            nothing, only updates ratings for all players
    """

    def full_pass(self, estimated={}):
        n = len(self.players)

        # pass 1 for rating adjustments
        for player in self.all_results:
            results = self.all_results[player]
            self.pass1(player, results)

        # pass 2 for unrated players
        for player in self.all_results:
            if player.rating == 0:
                results = self.all_results[player]
                self.pass2(player, results, estimated)

        # pass 3 for all players
        for player in self.all_results:
            results = self.all_results[player]

            self.final_pass(player, results)
