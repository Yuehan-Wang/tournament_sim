import random


class PlayoffTournament:

    def __init__(self, teams, match_engine, bracket_size: int = 32):
        self.teams = sorted(teams, key=lambda t: t.rating, reverse=True)[:bracket_size]
        self.me = match_engine
        self.winner = None
        self.rounds = []         
        self.match_count = 0
        for pos, tm in enumerate(self.teams):
            tm.reset_stats()

    def run(self):
        current = self.teams[:]          
        size = len(current)
        rnd_idx = 1
        while size > 1:
            print(f"\nPlay-off Round of {size}")
            next_round = []
            rnd_results = []
            for i in range(0, size, 2):
                t1, t2 = current[i], current[i + 1]
                winner, score, _ = self.me.simulate_match(t1, t2, is_knockout=True)
                t1.record_match(score[0], score[1])
                t2.record_match(score[1], score[0])
                self.match_count += 1
                next_round.append(winner)
                rnd_results.append((t1, t2, score, winner))
                print(f"{t1.name} {score[0]}–{score[1]} {t2.name} → {winner.name}")
            self.rounds.append(rnd_results)
            current = next_round
            size //= 2
            rnd_idx += 1
        self.winner = current[0]

    def get_rankings(self):
        lost_round = {t: 64 for t in self.teams}
        for rnd_size, matches in zip([32, 16, 8, 4, 2], self.rounds):
            for t1, t2, score, winner in matches:
                loser = t2 if winner is t1 else t1
                lost_round[loser] = rnd_size
        lost_round[self.winner] = 1
        return sorted(
            self.teams, key=lambda t: (lost_round[t], -t.rating)
        )
