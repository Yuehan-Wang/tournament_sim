class GroupStageBase:
    def simulate(self):
        raise NotImplementedError

    def get_rankings(self):
        raise NotImplementedError

    def get_qualified_teams(self):
        raise NotImplementedError

    def display_tables(self):
        raise NotImplementedError
