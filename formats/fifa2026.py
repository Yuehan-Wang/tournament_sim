from formats.fifa2026_group_stage import FIFA2026GroupStage

class FIFA2026Tournament:
    """
    Complete FIFA 2026 tournament simulation class.
        - Runs the group stage (48 teams, 12 groups of 4)
        - Stores qualified teams for knockout stage
    """

    def __init__(self, teams, match_engine):
        """ Initialize tournament with teams and match engine. """
        self.match_engine = match_engine
        self.teams = teams
        self.group_stage = None
        self.knockout_stage = None
        self.qualified_teams = []

    def run(self):
        """ Run the group stage simulation and determine qualified teams. """
        self.group_stage = FIFA2026GroupStage(self.teams, self.match_engine)
        self.group_stage.simulate()
        self.group_stage.display_tables()
        self.qualified_teams = self.group_stage.get_qualified_teams()

    def get_qualified_teams(self):
        """ Return the list of teams qualified from the group stage. """
        return self.qualified_teams
