class Team:
    def __init__(self, name, rating):
        self.name = name
        self.rating = rating
        self.reset_stats()

    def reset_stats(self):
        self.points = 0
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.goals_for = 0
        self.goals_against = 0

    def record_match(self, goals_for, goals_against):
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

    def goal_difference(self):
        return self.goals_for - self.goals_against

    def stats_summary(self):
        return f"{self.name}: {self.points} pts, GD: {self.goal_difference()}, GF: {self.goals_for}"

    def __repr__(self):
        return f"{self.name} ({self.rating})"
