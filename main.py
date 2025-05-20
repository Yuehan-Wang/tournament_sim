import pandas as pd
from core.team import Team
from core.match_engine import MatchEngine
from formats.fifa2026 import FIFA2026Tournament
from core.knockout_stage import KnockoutStage

from formats.playoff import PlayoffTournament     
from formats.swiss   import SwissTournament     
from evaluators.incentive_compatibility import IncentiveCompatibilityEvaluator


from evaluators.elo_correlation import EloCorrelationEvaluator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def load_teams_from_csv(csv_path="data/teams.csv"):
    df = pd.read_csv(csv_path)
    teams = [Team(row["Country"], int(row["Rating"])) for _, row in df.iterrows()]
    assert len(teams) == 48, f"Expected 48 teams, got {len(teams)}"
    return teams


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


def compute_metrics(label, rankings, tournament, initial_elos,
                    corr_eval, ic_eval):
    df = pd.DataFrame({
        "team": [t.name for t in rankings],
        "position": range(1, len(rankings) + 1)
    })

    corr = corr_eval.evaluate(df, initial_elos)
    print(f"\n[{label}]")
    print(f"Correlation: {corr['correlation']:.3f}  |  "
          f"Avg pos diff: {corr['avg_diff']:.2f}")

    try:
        ic = ic_eval.evaluate(tournament)
        print(f"Low-incentive games: {ic['low_incentive']}/"
              f"{ic['total_matches']} ({ic['pct_low_incentive']:.1f} %)")
    except Exception:
        print("Low-incentive games: n/a")

    fig = corr_eval.plot_correlation(df, initial_elos)
    if fig:
        fname = f"plots/corr_{label.lower().replace(' ', '_')}.png"
        if hasattr(fig, "savefig"):
            fig.savefig(fname, bbox_inches="tight")
        else:
            import matplotlib.pyplot as _plt
            _plt.savefig(fname, bbox_inches="tight")
            _plt.close("all")
        print(f"Correlation plot saved → {fname}")




def main():
    teams_master = load_teams_from_csv()
    initial_elos = (
        pd.read_csv("data/teams.csv")[["Country", "Rating"]]
        .rename(columns={"Country": "team", "Rating": "elo"})
    )
    corr_eval = EloCorrelationEvaluator()
    ic_eval   = IncentiveCompatibilityEvaluator()

    fifa_teams     = [t for t in teams_master]          
    match_engine   = MatchEngine()
    tournament     = FIFA2026Tournament(fifa_teams, match_engine)
    tournament.run()

    qualified = tournament.get_qualified_teams()
    knockout   = KnockoutStage(qualified, match_engine)
    knockout.simulate()

    fifa_rankings = get_rankings_from_knockout(knockout)
    compute_metrics("FIFA 2026", fifa_rankings, tournament,
                    initial_elos, corr_eval, ic_eval)

    po_tournament = PlayoffTournament(load_teams_from_csv(), MatchEngine())
    po_tournament.run()
    compute_metrics("Pure Play-off",
                    po_tournament.get_rankings(), po_tournament,
                    initial_elos, corr_eval, ic_eval)

    swiss_tournament = SwissTournament(load_teams_from_csv(),
                                       MatchEngine(), rounds=8)
    swiss_tournament.run()
    compute_metrics("8-round Swiss",
                    swiss_tournament.get_rankings(), swiss_tournament,
                    initial_elos, corr_eval, ic_eval)


if __name__ == "__main__":
    main()
