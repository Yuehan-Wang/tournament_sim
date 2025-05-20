class KnockoutStage:
    def __init__(self, teams, match_engine):
        if len(teams) not in (16, 32):
            raise ValueError("KnockoutStage expects 16 or 32 teams")
        self.teams = teams
        self.match_engine = match_engine
        self.rounds: list[list[tuple]] = []
        self.eliminated: dict = {}
        self.winner = None
        self.runner_up = None
    def _build_fifa2026_round_of_32(self):
        winners = {t.group: t for t in self.teams if t.group_pos == 1}
        runners = {t.group: t for t in self.teams if t.group_pos == 2}
        thirds  = [t for t in self.teams if t.group_pos == 3]
        def pick_third(allowed):
            for i, tm in enumerate(thirds):
                if tm.group in allowed:
                    return thirds.pop(i)
            return thirds.pop(0)
        matches = [
            (runners["A"], runners["B"]),
            (winners["E"], pick_third({"A","B","C","D","F"})),
            (winners["F"], runners["C"]),
            (winners["C"], runners["F"]),
            (winners["I"], pick_third({"C","D","F","G","H"})),
            (runners["E"], runners["I"]),
            (winners["A"], pick_third({"C","E","F","H","I"})),
            (winners["L"], pick_third({"E","H","I","J","K"})),
            (winners["D"], pick_third({"B","E","F","I","J"})),
            (winners["G"], pick_third({"A","E","H","I","J"})),
            (runners["K"], runners["L"]),
            (winners["H"], runners["J"]),
            (winners["B"], pick_third({"E","F","G","I","J"})),
            (winners["J"], runners["H"]),
            (winners["K"], pick_third({"D","E","I","J","L"})),
            (runners["D"], runners["G"]),
        ]
        return [tm for pair in matches for tm in pair]

    def _print_match(self, t1, t2, score, winner, pens):
        pen_flag = " (p)" if pens else ""
        print(f"{t1.name} {score[0]}–{score[1]} {t2.name} → {winner.name}{pen_flag}")

    def simulate(self):
        if len(self.teams) == 32:
            current = self._build_fifa2026_round_of_32()
        else: 
            current = sorted(self.teams, key=lambda t: (t.group, t.group_pos))

        size = len(current)
        while size > 1:
            print(f"\nRound of {size}")
            winners_next: list = []
            matches_this_round: list = []

            for i in range(0, size, 2):
                t1, t2 = current[i], current[i + 1]

                winner, score, pens = self.match_engine.simulate_match(
                    t1, t2, is_knockout=True
                )

                t1.record_match(score[0], score[1])
                t2.record_match(score[1], score[0])

                loser = t2 if winner is t1 else t1
                self.eliminated[loser] = size
                winners_next.append(winner)

                matches_this_round.append((t1, t2, score, winner, pens))
                self._print_match(t1, t2, score, winner, pens)

            self.rounds.append(matches_this_round)
            current = winners_next
            size //= 2

        self.winner = current[0]
        self.eliminated[self.winner] = 1
        if self.rounds and self.rounds[-1]:
            t1, t2, *_ = self.rounds[-1][0]
            self.runner_up = t2 if self.winner is t1 else t1

    def get_champion(self):
        return self.winner

    def _rank_key(self, team):
        elim_round = self.eliminated.get(team, 99)
        return (elim_round, -team.goal_difference(), -team.rating)

    def get_rankings(self):
        return sorted(self.teams, key=self._rank_key)

    def display_rankings(self):
        if self.winner is None:
            print("Knock‑out stage not yet simulated.")
            return

        print("\n=== FINAL RANKINGS ===")
        print(f"1. {self.winner.name}  (Champion)")
        if self.runner_up:
            print(f"2. {self.runner_up.name}  (Runner‑up)")

        tiers = [
            (4,  "Semi‑finalists  (3‑4)"),
            (8,  "Quarter‑finalists (5‑8)"),
            (16, "Round‑of‑16      (9‑16)"),
            (32, "Round‑of‑32     (17‑32)"),
        ]
        for size, label in tiers:
            group = [t.name for t, rnd in self.eliminated.items() if rnd == size]
            if group:
                print(f"{label:<22}: {', '.join(sorted(group))}")
