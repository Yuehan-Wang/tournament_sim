class KnockoutStage:
    """
    Knockout stage of the tournament.
    Supports 16 or 32 teams (e.g. FIFA 2026 format).
    """

    def __init__(self, teams, match_engine):
        """
        Initialize the knockout stage.

        Args:
            teams (list): List of qualified teams (must be 16 or 32).
            match_engine: Match simulation engine used for games.
        """
        if len(teams) not in (16, 32): raise ValueError("KnockoutStage expects 16 or 32 teams")
        self.teams = teams
        self.match_engine = match_engine

        # List of rounds; each round is a list of match tuples
        self.rounds: list[list[tuple]] = []

        # Dict to track when each team was eliminated (by round size)
        self.eliminated: dict = {}

        # Finalist metadata
        self.winner = None
        self.runner_up = None

    # ----------------------------------------------------------

    def _build_fifa2026_round_of_32(self):
        """
        Create the FIFA 2026 Round of 32 bracket.

        Process:
            - Group winners (1st place) and runners-up (2nd place) auto-qualify.
            - Remaining slots filled by best-performing 3rd-place teams.
            - Matches are hard-coded to mirror FIFA's planned bracket structure.

        Returns:
            list: Ordered list of teams in round-of-32 matchups.
        """
        winners = {t.group: t for t in self.teams if t.group_pos == 1}
        runners = {t.group: t for t in self.teams if t.group_pos == 2}
        thirds  = [t for t in self.teams if t not in winners and t not in runners]

        def pick_third(allowed):
            # Pick the first available 3rd-placed team from allowed groups
            for i, tm in enumerate(thirds):
                if tm.group in allowed:
                    return thirds.pop(i)
            return thirds.pop(0) # Fallback if none match

        # Matches based on FIFA 2026 provisional knockout logic
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

        # Flatten match list into a single ordered team list
        return [tm for pair in matches for tm in pair]

    def _print_match(self, t1, t2, score, winner, pens):
        """
        Print formatted match result (with penalty note if needed).
        """
        pen_flag = " (p)" if pens else ""
        print(f"{t1.name} {score[0]}-{score[1]} {t2.name} → {winner.name}{pen_flag}")

    # ----------------------------------------------------------

    def simulate(self):
        """
        Simulate all matches in the knockout stage.

        Process:
            - For 32 teams, build custom round-of-32 bracket.
            - For 16 teams, sort by group and position.
            - Run matchups round by round.
            - Record results and eliminate losing teams.
            - Track final winner and runner-up.
        """
        if len(self.teams) == 32:
            current = self._build_fifa2026_round_of_32()
        else:
            current = sorted(self.teams, key = lambda t: (t.group, t.group_pos))

        size = len(current)

        while size > 1:
            print(f"\nRound of {size}")
            winners_next: list = []
            matches_this_round: list = []

            # Pair teams for current round
            for i in range(0, size, 2):
                t1, t2 = current[i], current[i + 1]

                # Simulate match (with penalties if needed)
                winner, score, pens = self.match_engine.simulate_match(t1, t2, is_knockout = True)

                # Record goals scored and conceded
                t1.record_match(score[0], score[1])
                t2.record_match(score[1], score[0])

                # Mark loser as eliminated this round
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

        # Set runner-up from final match
        if self.rounds and self.rounds[-1]:
            t1, t2, *_ = self.rounds[-1][0]
            self.runner_up = t2 if self.winner is t1 else t1

    # ----------------------------------------------------------

    def get_champion(self):
        """
        Return the tournament winner.
        """
        return self.winner

    def _rank_key(self, team):
        """
        Key for final ranking.

        Order:
            - Round of elimination (lower better)
            - Goal difference (higher better)
            - Team rating (higher better)

        Returns:
            tuple: Sorting key for ranking teams.
        """
        elim_round = self.eliminated.get(team, 99)
        return (elim_round, -team.goal_difference(), -team.rating)

    def get_rankings(self):
        """
        Return all teams ranked by final position.
        """
        return sorted(self.teams, key = self._rank_key)

    def display_rankings(self):
        """
        Print final rankings summary.

        Shows champion, runner-up, and teams by round exit.
        """
        if self.winner is None:
            print("Knock-out stage not yet simulated.")
            return

        print("\n=== FINAL RANKINGS ===")
        print(f"1. {self.winner.name}  (Champion)")
        if self.runner_up: print(f"2. {self.runner_up.name}  (Runner-up)")

        # Group teams by elimination round
        tiers = [
            (4,  "Semi-finalists    (3-4)"),
            (8,  "Quarter-finalists (5-8)"),
            (16, "Round-of-16      (9-16)"),
            (32, "Round-of-32     (17-32)"),
        ]

        for size, label in tiers:
            group = [t.name for t, rnd in self.eliminated.items() if rnd == size]
            if group: print(f"{label:<22}: {', '.join(sorted(group))}")
