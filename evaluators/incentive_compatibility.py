from collections import defaultdict


class IncentiveCompatibilityEvaluator:
    def evaluate(self, tournament):
        if hasattr(tournament, "group_stage"):
            gs = tournament.group_stage
            if hasattr(gs, "results"):                     
                low, tot = self._evaluate_group_stage_full(gs)
            else:                                          
                low, tot = self._evaluate_group_stage_heuristic(gs)

        elif tournament.__class__.__name__.lower().startswith("swiss"):
            tot = sum(len(r) for r in tournament.round_results)
            low = 0
        else:
            tot = getattr(tournament, "match_count", 0)
            low = 0

        pct = 0 if tot == 0 else 100 * low / tot
        return {
            "format": tournament.__class__.__name__,
            "total_matches": tot,
            "low_incentive": low,
            "pct_low_incentive": pct,
        }


    def _evaluate_group_stage_full(self, gs):
        low = tot = 0
        for g, matches in gs.results.items():         
            pts = defaultdict(int)
            played = defaultdict(int)
            for t1, t2, score, _ in matches:
                tot += 1
                if self._both_safe_or_out(t1, t2, pts, played):
                    low += 1
                p1, p2 = score
                if p1 > p2:
                    pts[t1] += 3
                elif p2 > p1:
                    pts[t2] += 3
                else:                 
                    pts[t1] += 1
                    pts[t2] += 1    
                played[t1] += 1
                played[t2] += 1
        return low, tot


    def _evaluate_group_stage_heuristic(self, gs):
        if hasattr(gs, "groups") and gs.groups:
            groups = gs.groups
        else:
            groups = {}
            for tm in getattr(gs, "teams", []):
                grp = getattr(tm, "group", None)
                if grp is not None:
                    groups.setdefault(grp, []).append(tm)

        if not groups:             
            return 0, 0

        group_size = len(next(iter(groups.values())))
        num_groups = len(groups)
        total_matches = group_size * (group_size - 1) // 2 * num_groups
        low_incentive = num_groups         

        return low_incentive, total_matches

    def _both_safe_or_out(self, t1, t2, pts, played):
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
