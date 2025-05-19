import random
import numpy as np

class MatchEngine:
    def __init__(self, base_goal_expectation=1.1):
        self.base_goal_expectation = base_goal_expectation

    def _elo_win_probability(self, rating1, rating2):
        return 0.9 if rating1 > rating2 else 0.05

    def _draw_probability(self, rating1, rating2):
        return 0.05

    def _expected_goals(self, rating1, rating2):
        elo_diff = rating1 - rating2
        attack_factor = 1 + elo_diff / 1200
        defend_factor = 1 - elo_diff / 1200
        base_attack = self.base_goal_expectation * attack_factor
        base_defend = self.base_goal_expectation * defend_factor
        team1_goals = 0.85*base_attack + 0.15*base_defend
        team2_goals = 0.85*base_defend + 0.15*base_attack
        return (
            max(team1_goals * np.random.lognormal(0, 0.12), 0.15),
            max(team2_goals * np.random.lognormal(0, 0.12), 0.15)
        )

    def _simulate_penalty(self, rating1, rating2):
        elo_diff = rating1 - rating2
        prob = 0.5 + min(max(elo_diff / 30000, -0.03), 0.03)
        return random.random() < prob

    def simulate_match(self, team1, team2, is_knockout=False):
        rating1, rating2 = team1.rating, team2.rating
        win_prob = self._elo_win_probability(rating1, rating2)
        draw_prob = self._draw_probability(rating1, rating2)
        loss_prob = 1 - win_prob - draw_prob
        rand = random.random()
        outcome = "win1" if rand < win_prob else "draw" if rand < win_prob+draw_prob else "win2"
        goal_exp1, goal_exp2 = self._expected_goals(rating1, rating2)
        score1 = np.random.poisson(goal_exp1)
        score2 = np.random.poisson(goal_exp2)
        if outcome == "win1" and score1 <= score2:
            score1 = max(score1, score2 + (1 if score2 - score1 < 2 else 0))
        elif outcome == "win2" and score2 <= score1:
            score2 = max(score2, score1 + (1 if score1 - score2 < 2 else 0))
        elif outcome == "draw":
            score1 = score2 = min(score1, score2)
        if is_knockout and score1 == score2:
            goal_exp1 *= 1.4
            goal_exp2 *= 1.4
            score1 += np.random.poisson(goal_exp1)
            score2 += np.random.poisson(goal_exp2)
            if score1 == score2:
                return (team1 if self._simulate_penalty(rating1, rating2) else team2,
                       (score1, score2), True)
        return (team1 if score1 > score2 else team2 if score2 > score1 else None,
               (score1, score2),
               False)