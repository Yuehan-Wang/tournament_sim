import random
from itertools import combinations

class GroupStage:
    """
    4-team group with FIFA tie-breaks.
    Points → Goal Difference → Goals For → Fair-play points → Drawing of lots.
    """

    def __init__(self, teams, match_engine, group_size: int = 4):
        """ Initialize the group stage. """
        self.teams = teams
        self.match_engine = match_engine
        self.group_size = group_size

        # Create groups (typically groups A to L with 12 groups of 4 teams each)
        self.groups = self._create_groups()

        # Dictionary to hold results per group: key = group letter, value = list of matches
        self.results = {}

    # ----------------------------------------------------------

    def _create_groups(self):
        """
        Create groups for the tournament.

        Process:
            - Sort teams by rating descending.
            - Split teams into 4 pots of 12 teams each (top 12 rated in pot 1, next 12 in pot 2, etc.)
            - Shuffle each pot to randomize draw.
            - Assign one team from each pot to each group, ensuring balanced groups.
        """
        sorted_teams = sorted(self.teams, key = lambda t: t.rating, reverse = True)

        # Divide teams into 4 pots, each with 12 teams (assuming 48 teams total)
        pots = [sorted_teams[i * 12 : (i + 1) * 12] for i in range(4)]

        # Shuffle teams within each pot to randomize group assignment
        for pot in pots: random.shuffle(pot)

        # Create 12 groups labeled from 'A' to 'L'
        groups = {chr(65 + i): [] for i in range(12)}

        # Assign one team from each pot to each group to balance team strengths
        for i in range(4):
            for j, g in enumerate(groups):
                groups[g].append(pots[i][j])

        return groups

    # ----------------------------------------------------------

    def simulate(self):
        """
        Simulate all matches in the group stage.

        - For each group:
            - Iterate over all unique pairs of teams (each team plays others once).
            - Simulate the match using match_engine.
            - Record match results for each team.
            - Store match results for reporting.

        - After all matches:
            - Rank teams within each group using FIFA tie-break criteria.
            - Assign each team their group and group position (1, 2, 3, 4).
        """
        for g, teams in self.groups.items():
            self.results[g] = []

            # Generate all pairwise matches (each team plays every other once)
            for t1, t2 in combinations(teams, 2):
                winner, score, _ = self.match_engine.simulate_match(t1, t2)

                # Record match results on team objects (goals scored and conceded)
                t1.record_match(score[0], score[1])
                t2.record_match(score[1], score[0])

                # Store result tuple: (team1, team2, score, winner)
                self.results[g].append((t1, t2, score, winner))

                # Display match result for feedback
                verb = "Draw" if winner is None else f"{winner.name} wins"
                print(f"[Group {g}] {t1.name} {score[0]}-{score[1]} {t2.name} → {verb}")

        # Assign group and position labels based on rankings for knockout stage usage
        for g, ranked in self.get_group_rankings().items():
            for pos, tm in enumerate(ranked, 1):
                tm.group = g
                tm.group_pos = pos

    # ----------------------------------------------------------

    def get_group_rankings(self):
        """ Compute and return rankings of teams within each group. """
        ranks = {}

        for g, teams in self.groups.items():
            ranks[g] = sorted(
                teams,
                key = lambda t: (
                    t.points,
                    t.goal_difference(),
                    t.goals_for,
                    -t.fair_play,
                    random.random()
                ),
                reverse = True
            )

        return ranks

    def display_tables(self):
        """ Print the current standings tables for all groups. """
        for g, table in self.get_group_rankings().items():
            print(f"\nGroup {g}")
            for t in table: print(f"{t.name:15} | Pts {t.points:2} | GD {t.goal_difference():+2} | GF {t.goals_for:2} | FP {t.fair_play}")
