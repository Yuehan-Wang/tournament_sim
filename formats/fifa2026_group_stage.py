from core.group_stage_base import GroupStageBase
from core.group_stage import GroupStage

class FIFA2026GroupStage(GroupStageBase):
    """
    FIFA 2026-style group stage implementation.
        - 48 teams are divided into 12 groups of 4.
        - Top 2 teams from each group qualify directly (24 teams).
        - 8 best 3rd-placed teams also advance, based on FIFA criteria: Points → Goal Difference → Goals For.

    Wraps the core GroupStage logic and conforms to the GroupStageBase interface.
    """

    def __init__(self, teams, match_engine):
        """ Initialize the FIFA 2026 group stage format. """
        self.stage = GroupStage(teams, match_engine, group_size = 4)
        self.rankings = {} # Group rankings after simulation
        self.results = {}  # Match results by group

    def simulate(self):
        """ Simulate all matches in the group stage and store results. """
        self.stage.simulate()
        self.rankings = self.stage.get_group_rankings()
        self.results = self.stage.results

    def get_rankings(self):
        """ Get the full group stage rankings. """
        return self.rankings
    
    def get_qualified_teams(self):
        """ Return the 32 teams that advance to the knockout stage. """
        # Top 2 teams from each group
        top_2 = [r[0] for r in self.rankings.values()] + [r[1] for r in self.rankings.values()]

        # Select best 8 3rd-placed teams using FIFA tiebreak rules
        third_place = [r[2] for r in self.rankings.values()]
        best_8 = sorted(third_place, key = lambda t: (t.points, t.goal_difference(), t.goals_for), reverse = True)[:8]

        return top_2 + best_8

    def display_tables(self):
        """ Print final group standings in a formatted table. """
        for group_name in sorted(self.rankings.keys()):
            print(f"\nGroup {group_name}")
            for t in self.rankings[group_name]: print(f"{t.name:15} | Pts: {t.points} | GD: {t.goal_difference():+} | GF: {t.goals_for}")
