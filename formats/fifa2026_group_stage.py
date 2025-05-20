from core.group_stage_base import GroupStageBase
from core.group_stage import GroupStage

class FIFA2026GroupStage(GroupStageBase):
    def __init__(self, teams, match_engine):
        self.stage = GroupStage(teams, match_engine, group_size=4)
        self.rankings = {}
        self.results = {}

    def simulate(self):
        self.stage.simulate()
        self.rankings = self.stage.get_group_rankings()
        self.results = self.stage.results

    def get_rankings(self):
        return self.rankings

    def get_qualified_teams(self):
        top_2 = [r[0] for r in self.rankings.values()] + [r[1] for r in self.rankings.values()]
        third_place = [r[2] for r in self.rankings.values()]
        best_8 = sorted(third_place, key=lambda t: (t.points, t.goal_difference(), t.goals_for), reverse=True)[:8]
        return top_2 + best_8

    def display_tables(self):
        for group_name in sorted(self.rankings.keys()):
            print(f"\nGroup {group_name}")
            for t in self.rankings[group_name]:
                print(f"{t.name:15} | Pts: {t.points} | GD: {t.goal_difference():+} | GF: {t.goals_for}")
