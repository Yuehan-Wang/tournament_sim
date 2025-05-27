class PlayoffTournament:
    """
    Simulates a single-elimination playoff tournament.
    Teams are seeded by rating and paired off in each round. Winners advance to the next round until a champion is decided.
    Tracks match results, team statistics, and supports ranking teams based on the round they were eliminated.
    """

    def __init__(self, teams, match_engine, bracket_size: int = 32):
        """ Initialize playoff tournament with top teams by rating. """
        # Sort teams by rating descending and take top bracket_size
        self.teams = sorted(teams, key = lambda t: t.rating, reverse = True)[:bracket_size]
        self.me = match_engine
        self.winner = None
        self.rounds = [] # Store matches per round
        self.match_count = 0

        # Reset team stats for new simulation
        for _, tm in enumerate(self.teams): tm.reset_stats()

    def run(self):
        """ Simulate the playoff rounds until a winner is decided. """
        current = self.teams[:]
        size = len(current)
        rnd_idx = 1

        while size > 1:
            print(f"\nPlay-off Round of {size}")
            next_round = []
            rnd_results = []

            for i in range(0, size, 2):
                t1, t2 = current[i], current[i + 1]
                winner, score, _ = self.me.simulate_match(t1, t2, is_knockout = True)

                # Update team stats
                t1.record_match(score[0], score[1])
                t2.record_match(score[1], score[0])
                self.match_count += 1

                next_round.append(winner)
                rnd_results.append((t1, t2, score, winner))
                print(f"{t1.name} {score[0]}-{score[1]} {t2.name} → {winner.name}")

            self.rounds.append(rnd_results)
            current = next_round
            size //= 2
            rnd_idx += 1

        self.winner = current[0]

    def get_rankings(self):
        """ Generate rankings based on the round each team lost. """
        lost_round = {t: 64 for t in self.teams} # Default lost round for all

        # Assign lost round based on match results
        for rnd_size, matches in zip([32, 16, 8, 4, 2], self.rounds):
            for t1, t2, _, winner in matches:
                loser = t2 if winner is t1 else t1
                lost_round[loser] = rnd_size

        lost_round[self.winner] = 1 # Winner "lost" in round 1 (final winner)

        # Sort by lost round ascending (earlier eliminated lower) then by rating descendingass
        return sorted(self.teams, key = lambda t: (lost_round[t], -t.rating))
