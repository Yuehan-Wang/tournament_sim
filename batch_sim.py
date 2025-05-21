import argparse
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
from tqdm import tqdm

from formats.fifa2026 import FIFA2026Tournament
from formats.playoff   import PlayoffTournament
from formats.swiss     import SwissTournament

from evaluators.elo_correlation         import EloCorrelationEvaluator
from evaluators.incentive_compatibility import IncentiveCompatibilityEvaluator

from core.team         import Team
from core.match_engine import MatchEngine
from core.knockout_stage import KnockoutStage

corr_eval = EloCorrelationEvaluator()
ic_eval   = IncentiveCompatibilityEvaluator()


def get_rankings_from_knockout(knockout):
    champion   = knockout.get_champion()
    last_match = knockout.rounds[-1][0]
    runner_up  = last_match[0] if last_match[0] != champion else last_match[1]
    third_place = [m[3] for m in knockout.rounds[-2]
                   if m[3] not in (champion, runner_up)]
    rankings = [champion, runner_up] + third_place
    for round_size in [4, 8, 16, 32]:
        rankings.extend([t for t, r in knockout.eliminated.items()
                         if r == round_size and t not in rankings])
    return rankings


def run_one(tournament_cls, ratings_df):
    """Play one complete tournament and return (rho, pos_err, dead_pct)."""
    teams = [Team(row["Country"], int(row["Rating"]))
             for _, row in ratings_df.iterrows()]

    match_engine = MatchEngine()
    tour = tournament_cls(teams, match_engine)
    tour.run()                                  

    if isinstance(tour, FIFA2026Tournament):
        qualified = tour.get_qualified_teams()
        knockout = KnockoutStage(qualified, match_engine)
        knockout.simulate()
        rankings = get_rankings_from_knockout(knockout)
    else:
        rankings = tour.get_rankings()

    df = pd.DataFrame({
        "team":     [t.name for t in rankings],
        "position": range(1, len(rankings) + 1)
    })
    initial_elos = ratings_df.rename(columns={"Country": "team",
                                            "Rating":  "elo"})
    corr = corr_eval.evaluate(df, initial_elos)

    try:
        ic   = ic_eval.evaluate(tour)
        dead = ic["pct_low_incentive"]         
    except Exception:
        dead = 0.0                            
    return corr["correlation"], corr["avg_diff"], dead

def main(args):
    ratings_df = pd.read_csv(args.rating_csv)
    out_dir    = Path("results")
    out_dir.mkdir(exist_ok=True)

    formats = {
        "FIFA2026": FIFA2026Tournament,
        "Playoff":  PlayoffTournament,
        "Swiss8R":  SwissTournament,
    }

    metrics = defaultdict(list)

    for fmt_name, tour_cls in formats.items():
        print(f"\nRunning {args.n} editions of {fmt_name} …")
        for _ in tqdm(range(args.n)):
            rho, err, dead = run_one(tour_cls, ratings_df)
            metrics["format"].append(fmt_name)
            metrics["rho"].append(rho)
            metrics["err"].append(err)
            metrics["dead_pct"].append(dead)

    df = pd.DataFrame(metrics)
    df.to_csv(out_dir / "batch_metrics.csv", index=False)

    print("\n=== Monte-Carlo summary (mean ± SD) ===")
    summary = (df.groupby("format")
                 .agg({"rho":      ["mean", "std"],
                       "err":      ["mean", "std"],
                       "dead_pct": ["mean", "std"]})
                 .round(3))
    print(summary.to_markdown())
    print(f"\nRaw data saved → {out_dir/'batch_metrics.csv'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=1000,
                        help="repetitions per format (default 1000)")
    parser.add_argument("--rating_csv", required=True,
                        help="CSV with columns: Country, Rating")
    main(parser.parse_args())
