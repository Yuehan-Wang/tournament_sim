import random
import numpy as np

class MatchEngine:
    """
    Match simulator using Elo ratings and Poisson goal models.
    Handles both group and knockout matches, including penalties.
    """

    def __init__(self, base_goal_expectation: float = 1.1):
        """
        Initialize the match engine.

        Args:
            base_goal_expectation: Average goal rate for balanced teams.
        """
        self.base_goal_expectation = base_goal_expectation

    # ----------------------------------------------------------
    # Probability helpers - kept exactly as requested
    # ----------------------------------------------------------

    def _elo_win_probability(self, rating1, rating2):
        """
        Return win probability for rating1 vs rating2.

        Uses simplified fixed outcomes for demonstration purposes.
        """
        return 0.90 if rating1 > rating2 else 0.05

    def _draw_probability(self, rating1, rating2):
        """
        Return probability of draw for rating1 vs rating2.
        """
        return 0.05

    # ----------------------------------------------------------
    # Translate Elo gap → two attacking means
    # ----------------------------------------------------------

    def _expected_goals(self, rating1, rating2):
        """
        Convert Elo ratings to goal expectations (Poisson means).

        Process:
            - Use rating gap to compute attacking strength ratio.
            - Adjust goal expectation up or down accordingly.

        Returns:
            tuple: (mean goals for team1, mean goals for team2)
        """
        elo_diff = rating1 - rating2
        factor = 1 + elo_diff / 1200 # 600-point gap → factor = 1.5
        g1 = max(0.2, self.base_goal_expectation * factor)
        g2 = max(0.2, self.base_goal_expectation / factor)
        return g1, g2

    # ----------------------------------------------------------

    def _simulate_penalty(self, rating1, rating2):
        """
        Simulate penalty shootout based on ratings.

        Returns:
            bool: True if team1 wins, False otherwise.
        """
        return random.random() < self._elo_win_probability(rating1, rating2)

    # ----------------------------------------------------------

    def simulate_match(self, team1, team2, *, is_knockout = False):
        """
        Simulate a match between two teams.

        Process:
            - Determine outcome type (win/loss/draw) based on Elo win prob.
            - Sample Poisson scores until they match desired outcome.
            - For knockouts:
                - Add extra time if draw.
                - Use penalty shootout if still level.

        Args:
            team1, team2: Competing team objects.
            is_knockout: Whether penalties are allowed.

        Returns:
            tuple: (winner, (score1, score2), went_to_penalties)
        """
        r1, r2 = team1.rating, team2.rating

        # Decide W/D/L outcome probabilistically
        win_p = self._elo_win_probability(r1, r2)
        draw_p = self._draw_probability(r1, r2)
        rand = random.random()
        forced = "win1" if rand < win_p else "draw" if rand < win_p + draw_p else "win2"

        # Get expected goal means based on Elo gap
        mu1, mu2 = self._expected_goals(r1, r2)

        # Try multiple times to sample goals matching forced outcome
        for _ in range(50):
            g1 = np.random.poisson(mu1)
            g2 = np.random.poisson(mu2)
            if (forced == "win1" and g1 > g2) or (forced == "win2" and g2 > g1) or (forced == "draw" and g1 == g2): break
        else:
            # Fallback in case no sample matched forced result
            if forced == "win1":
                g1, g2 = g2 + 1, g2
            elif forced == "win2":
                g1, g2 = g1, g1 + 1
            else:
                g1 = g2 = max(g1, g2)

        went_to_pens = False

        # Knockout rules: add extra time and/or penalties if tied
        if is_knockout and g1 == g2:
            g1 += np.random.poisson(mu1 * 0.4)
            g2 += np.random.poisson(mu2 * 0.4)

            if g1 == g2:
                went_to_pens = True
                if self._simulate_penalty(r1, r2):
                    g1 += 1
                else:
                    g2 += 1

        # Determine winner
        winner = None if g1 == g2 else (team1 if g1 > g2 else team2)
        return winner, (int(g1), int(g2)), went_to_pens
