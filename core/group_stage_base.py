class GroupStageBase:
    """
    Abstract base class for group stage implementations.

    Defines the core interface expected from any group stage format:
        - Simulation of matches
        - Retrieval of team rankings
        - Extraction of qualified teams for the next round
        - Display of group tables

    Subclasses should implement all abstract methods.
    """

    def simulate(self):
        raise NotImplementedError

    def get_rankings(self):
        raise NotImplementedError

    def get_qualified_teams(self):
        raise NotImplementedError

    def display_tables(self):
        raise NotImplementedError
