import random
from collections import defaultdict
from itertools import zip_longest


class SwissTournament:
    def __init__(self, teams, match_engine, rounds: int = 8):
        self.teams = teams
        self.me = match_engine
        self.rounds = rounds
        self.round_results = []         
        self.match_count = 0
        for t in self.teams:
            t.reset_stats()

    def _pair_round(self):
        ordered = sorted(
            self.teams,
            key=lambda t: (t.points, t.rating, random.random()),
            reverse=True,
        )
        it = iter(ordered)
        return list(zip(it, it))        
    
    def run(self):
        for rnd in range(1, self.rounds + 1):
            pairs = self._pair_round()
            results_this = []
            print(f"\nSwiss Round {rnd}")
            for t1, t2 in pairs:
                winner, score, _ = self.me.simulate_match(t1, t2)
                t1.record_match(score[0], score[1])
                t2.record_match(score[1], score[0])
                self.match_count += 1
                results_this.append((t1, t2, score, winner))
                verb = "draw" if winner is None else f"{winner.name} wins"
                print(f"{t1.name} {score[0]}–{score[1]} {t2.name} → {verb}")
            self.round_results.append(results_this)


    def get_rankings(self):
        return sorted(
            self.teams,
            key=lambda t: (
                t.points,
                t.goal_difference(),
                t.goals_for,
                t.rating,
            ),
            reverse=True,
        )
