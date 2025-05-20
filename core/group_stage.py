import random
from itertools import combinations


class GroupStage:
    """4-team group with FIFA tie-breaks:
       Points → GD → GF → fair-play → drawing of lots."""

    def __init__(self, teams, match_engine, group_size: int = 4):
        self.teams = teams
        self.match_engine = match_engine
        self.group_size = group_size
        self.groups = self._create_groups()
        self.results = {}

    # ----------------------------------------------------------
    def _create_groups(self):
        sorted_teams = sorted(self.teams, key=lambda t: t.rating, reverse=True)
        pots = [sorted_teams[i * 12:(i + 1) * 12] for i in range(4)]
        for pot in pots:
            random.shuffle(pot)

        groups = {chr(65 + i): [] for i in range(12)}          # A-L
        for i in range(4):                                      # pots 1-4
            for j, g in enumerate(groups):
                groups[g].append(pots[i][j])
        return groups

    # ----------------------------------------------------------
    def simulate(self):
        for g, teams in self.groups.items():
            self.results[g] = []
            for t1, t2 in combinations(teams, 2):
                winner, score, _ = self.match_engine.simulate_match(t1, t2)
                t1.record_match(score[0], score[1])
                t2.record_match(score[1], score[0])
                verb = "Draw" if winner is None else f"{winner.name} wins"
                print(f"[Group {g}] {t1.name} {score[0]}–{score[1]} {t2.name} → {verb}")
                self.results[g].append((t1, t2, score, winner))

        # label for KO builder
        for g, ranked in self.get_group_rankings().items():
            for pos, tm in enumerate(ranked, 1):
                tm.group = g
                tm.group_pos = pos

    # ----------------------------------------------------------
    def get_group_rankings(self):
        ranks = {}
        for g, teams in self.groups.items():
            ranks[g] = sorted(
                teams,
                key=lambda t: (
                    t.points,
                    t.goal_difference(),
                    t.goals_for,
                    -t.fair_play,          # fewer card points = better
                    random.random()        # drawing of lots
                ),
                reverse=True
            )
        return ranks

    def display_tables(self):
        for g, table in self.get_group_rankings().items():
            print(f"\nGroup {g}")
            for t in table:
                print(f"{t.name:15} | Pts {t.points:2} | GD {t.goal_difference():+2} "
                      f"| GF {t.goals_for:2} | FP {t.fair_play}")
