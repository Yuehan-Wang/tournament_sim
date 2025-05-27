import random

class Team:
    """
    Team object representing a participating country or club.
    Stores Elo rating, match statistics, and group stage metadata.
    """

    def __init__(self, name: str, rating: float):
        """
        Initialize a team.

        Args:
            name: Team name.
            rating: Elo rating used for simulation.
        """
        self.name = name
        self.rating = rating
        self.reset_stats()

    def reset_stats(self):
        """
        Reset all match and group-related statistics.
        """
        self.points = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.goals_for = 0
        self.goals_against = 0
        self.fair_play = 0
        self.group = None
        self.group_pos = None

    # ----------------------------------------------------------

    def record_match(self, goals_for: int, goals_against: int):
        """
        Record the outcome of a match.

        Updates:
            - Points (3 win, 1 draw, 0 loss)
            - Goals scored and conceded
            - Fair-play points (randomly generated cards)

        Args:
            goals_for: Goals scored by this team.
            goals_against: Goals conceded.
        """
        self.goals_for += goals_for
        self.goals_against += goals_against

        if goals_for > goals_against:
            self.points += 3
            self.wins += 1
        elif goals_for == goals_against:
            self.points += 1
            self.draws += 1
        else:
            self.losses += 1

        # Fair play: yellow cards = 1 pt, red cards = 3 pts
        yellows = random.randint(0, 2)
        reds = 1 if random.random() < 0.05 else 0
        self.fair_play += yellows + 3 * reds

    # ----------------------------------------------------------

    def goal_difference(self):
        """
        Return goal difference (goals scored - conceded).
        """
        return self.goals_for - self.goals_against

    def stats_summary(self):
        """
        Return string summary of team stats.

        Format: name, points, goal diff, goals for, fair play.
        """
        return f"{self.name}: {self.points} pts | GD {self.goal_difference():+2} | GF {self.goals_for:2} | FP {self.fair_play}"

    def __repr__(self):
        """
        User-friendly representation of the team.
        """
        return f"{self.name} ({self.rating})"
