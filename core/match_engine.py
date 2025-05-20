import random
import numpy as np


class MatchEngine:
    def __init__(self, base_goal_expectation: float = 1.1):
        self.base_goal_expectation = base_goal_expectation

    # ----------------------------------------------------------
    #  Probability helpers – kept exactly as requested
    # ----------------------------------------------------------
    def _elo_win_probability(self, rating1, rating2):
        return 0.90 if rating1 > rating2 else 0.05

    def _draw_probability(self, rating1, rating2):
        return 0.05

    # ----------------------------------------------------------
    #  Translate Elo gap → two attacking means
    # ----------------------------------------------------------
    def _expected_goals(self, rating1, rating2):
        elo_diff = rating1 - rating2
        factor = 1 + elo_diff / 1200                # 600-pt gap → 1 + 0.5
        g1 = max(0.2, self.base_goal_expectation * factor)
        g2 = max(0.2, self.base_goal_expectation / factor)
        return g1, g2

    # ----------------------------------------------------------
    def _simulate_penalty(self, rating1, rating2):
        return random.random() < self._elo_win_probability(rating1, rating2)

    # ----------------------------------------------------------
    def simulate_match(self, team1, team2, *, is_knockout=False):
        r1, r2 = team1.rating, team2.rating

        # decide W-D-L first
        win_p = self._elo_win_probability(r1, r2)
        draw_p = self._draw_probability(r1, r2)
        rand = random.random()
        forced = "win1" if rand < win_p else "draw" if rand < win_p + draw_p else "win2"

        mu1, mu2 = self._expected_goals(r1, r2)

        # sample Poisson scores until they fit the forced result
        for _ in range(50):
            g1 = np.random.poisson(mu1)
            g2 = np.random.poisson(mu2)
            if (forced == "win1" and g1 > g2) or (forced == "win2" and g2 > g1) \
               or (forced == "draw" and g1 == g2):
                break
        else:  # safety fall-back
            if forced == "win1":
                g1, g2 = g2 + 1, g2
            elif forced == "win2":
                g1, g2 = g1, g1 + 1
            else:
                g1 = g2 = max(g1, g2)

        # extra-time & penalties
        went_to_pens = False
        if is_knockout and g1 == g2:
            g1 += np.random.poisson(mu1 * 0.4)
            g2 += np.random.poisson(mu2 * 0.4)
            if g1 == g2:  # still level
                went_to_pens = True
                if self._simulate_penalty(r1, r2):
                    g1 += 1
                else:
                    g2 += 1

        winner = None if g1 == g2 else (team1 if g1 > g2 else team2)
        return winner, (int(g1), int(g2)), went_to_pens
