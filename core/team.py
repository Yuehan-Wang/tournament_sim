import random


class Team:
    def __init__(self, name: str, rating: float):
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
        self.fair_play = 0
        self.group = None
        self.group_pos = None

    def record_match(self, goals_for: int, goals_against: int):
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

        yellows = random.randint(0, 2)          
        reds = 1 if random.random() < 0.05 else 0
        self.fair_play += yellows + 3 * reds

    def goal_difference(self):
        return self.goals_for - self.goals_against

    def stats_summary(self):
        return (
            f"{self.name}: {self.points} pts | GD {self.goal_difference():+2} | "
            f"GF {self.goals_for:2} | FP {self.fair_play}"
        )

    def __repr__(self):
        return f"{self.name} ({self.rating})"
