from collections import defaultdict

class IncentiveCompatibilityEvaluator:
    """
    Evaluates incentive compatibility of a tournament format.
    Supports:
        - Full evaluation using recorded match results
        - Heuristic fallback for incomplete simulations
    """

    def evaluate(self, tournament):
        """ Evaluate a tournament object for incentive issues. """
        if hasattr(tournament, "group_stage"):
            gs = tournament.group_stage

            # Use actual results if available, else use group heuristic
            if hasattr(gs, "results"):
                low, tot = self._evaluate_group_stage_full(gs)
            else:
                low, tot = self._evaluate_group_stage_heuristic(gs)

        elif tournament.__class__.__name__.lower().startswith("swiss"):
            # Assume all Swiss matches are high-incentive
            tot = sum(len(r) for r in tournament.round_results)
            low = 0
        else:
            # Fallback if structure not recognized
            tot = getattr(tournament, "match_count", 0)
            low = 0

        # Compute percentage of low-incentive matches
        pct = 0 if tot == 0 else 100 * low / tot

        return {
            "format": tournament.__class__.__name__,
            "total_matches": tot,
            "low_incentive": low,
            "pct_low_incentive": pct,
        }

    def _evaluate_group_stage_full(self, gs):
        """ Full match-by-match evaluation using group stage results. """
        low = tot = 0

        for _, matches in gs.results.items():
            pts = defaultdict(int)    # Team points
            played = defaultdict(int) # Matches played

            for t1, t2, score, _ in matches:
                tot += 1
                if self._both_safe_or_out(t1, t2, pts, played): low += 1

                # Update points based on match result
                p1, p2 = score

                if p1 > p2:
                    pts[t1] += 3
                elif p2 > p1:
                    pts[t2] += 3
                else:
                    pts[t1] += 1
                    pts[t2] += 1

                # Track games played
                played[t1] += 1
                played[t2] += 1

        return low, tot

    def _evaluate_group_stage_heuristic(self, gs):
        """ Heuristic evaluation when results aren't available. """
        # Try to access group dictionary, or reconstruct from team info
        if hasattr(gs, "groups") and gs.groups:
            groups = gs.groups
        else:
            groups = {}
            for tm in getattr(gs, "teams", []):
                grp = getattr(tm, "group", None)
                if grp is not None: groups.setdefault(grp, []).append(tm)

        if not groups: return 0, 0

        # Matches per group: C(n, 2) = n(n - 1)/2
        group_size = len(next(iter(groups.values())))
        num_groups = len(groups)
        total_matches = group_size * (group_size - 1) // 2 * num_groups

        # Assume 1 low-incentive match per group as a heuristic
        low_incentive = num_groups
        return low_incentive, total_matches

    def _both_safe_or_out(self, t1, t2, pts, played):
        """ Determine if both teams are "safe" or "out" given current standings. """
        def status(t):
            p = pts.get(t, 0)
            left = 3 - played.get(t, 0)
            max_p = p + 3 * left
            if p >= 6:
                return "safe"
            if max_p < 4:
                return "out"
            return "live"

        s1, s2 = status(t1), status(t2)
        return s1 == s2 and s1 in {"safe", "out"}
