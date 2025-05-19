import pandas as pd
from core.team import Team
from core.match_engine import MatchEngine
from formats.fifa2026 import FIFA2026Tournament
from core.knockout_stage import KnockoutStage
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
    champion = knockout.get_champion()
    final_round = knockout.rounds[-1]
    last_match = final_round[0]
    runner_up = last_match[0] if last_match[0] != champion else last_match[1]
    semi_final_round = knockout.rounds[-2]
    third_place = []
    for match in semi_final_round:
        if match[3] != champion and match[3] != runner_up:
            third_place.append(match[3])
    rankings = [champion, runner_up] + third_place
    for round_size in [4, 8, 16, 32]:
        for team, round_out in knockout.eliminated.items():
            if round_out == round_size and team not in rankings:
                rankings.append(team)
    return rankings

def main():
    teams = load_teams_from_csv()
    match_engine = MatchEngine()
    tournament = FIFA2026Tournament(teams, match_engine)
    tournament.run()
    qualified = tournament.get_qualified_teams()
    print(f"\nQualified to Knockout Stage: {len(qualified)} teams")
    for team in qualified:
        print(f"- {team.name} ({team.points} pts, GD: {team.goal_difference()})")
    knockout = KnockoutStage(qualified, match_engine)
    knockout.simulate()
    knockout.display_rankings()
    print("\nChampion:", knockout.get_champion().name)
    print("\n=== Correlation Analysis ===")
    teams_df = pd.read_csv('data/teams.csv')
    initial_elos = teams_df[['Country', 'Rating']].rename(columns={'Country': 'team', 'Rating': 'elo'})
    final_standings = get_rankings_from_knockout(knockout)
    final_standings_df = pd.DataFrame({
        'team': [team.name for team in final_standings],
        'position': range(1, len(final_standings) + 1)
    })
    evaluator = EloCorrelationEvaluator()
    result = evaluator.evaluate(final_standings_df, initial_elos)
    print(f"Correlation: {result['correlation']:.3f}")
    print(f"P-value: {result['p_value']:.3f}")
    print(f"Maximum position difference: {result['max_diff']}")
    print(f"Average position difference: {result['avg_diff']:.2f}")
    plt = evaluator.plot_correlation(final_standings_df, initial_elos)
    if plt:
        plt.savefig('correlation_plot.png')
        print("\nCorrelation plot has been saved to 'correlation_plot.png'")

if __name__ == "__main__":
    main()
