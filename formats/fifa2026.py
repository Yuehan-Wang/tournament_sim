from formats.fifa2026_group_stage import FIFA2026GroupStage

class FIFA2026Tournament:
    def __init__(self, teams, match_engine):
        self.match_engine = match_engine
        self.teams = teams
        self.group_stage = None
        self.knockout_stage = None
        self.qualified_teams = []

    def run(self):
        self.group_stage = FIFA2026GroupStage(self.teams, self.match_engine)
        self.group_stage.simulate()
        self.group_stage.display_tables()

        self.qualified_teams = self.group_stage.get_qualified_teams()

    def get_qualified_teams(self):
        return self.qualified_teams
