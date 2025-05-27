import random

class SwissTournament:
    """
    Simulates a Swiss-system tournament where teams are paired each round based on their current points and ratings.
    The tournament proceeds for a fixed number of rounds, updating team stats and rankings after each round.
    """

    def __init__(self, teams, match_engine, rounds: int = 8):
        """ Initialize the Swiss tournament. """
        self.teams = teams
        self.me = match_engine
        self.rounds = rounds
        self.round_results = [] # Store match results for each round
        self.match_count = 0

        # Reset stats for all teams before starting the tournament
        for t in self.teams: t.reset_stats()

    def _pair_round(self):
        """ Pair teams for the current round based on their points and ratings. """
        # Sort teams by points, rating, and random factor for tie-breaks
        ordered = sorted(self.teams, key = lambda t: (t.points, t.rating, random.random()), reverse = True)
        it = iter(ordered)

        # Pair off teams sequentially
        return list(zip(it, it))
    
    def run(self):
        """ Run the full Swiss tournament for the specified number of rounds. """
        for rnd in range(1, self.rounds + 1):
            pairs = self._pair_round()
            results_this = []
            print(f"\nSwiss Round {rnd}")

            for t1, t2 in pairs:
                winner, score, _ = self.me.simulate_match(t1, t2)

                # Update team stats after match
                t1.record_match(score[0], score[1])
                t2.record_match(score[1], score[0])
                self.match_count += 1

                results_this.append((t1, t2, score, winner))
                verb = "draw" if winner is None else f"{winner.name} wins"
                print(f"{t1.name} {score[0]}-{score[1]} {t2.name} → {verb}")

            self.round_results.append(results_this)

    def get_rankings(self):
        """ Return the current team rankings. """
        return sorted(
            self.teams,
            key = lambda t: (
                t.points,
                t.goal_difference(),
                t.goals_for,
                t.rating,
            ),
            reverse = True,
        )
