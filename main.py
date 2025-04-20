import pandas as pd
from core.team import Team
from core.match_engine import MatchEngine
from formats.fifa2026 import FIFA2026Tournament
from core.knockout_stage import KnockoutStage

def load_teams_from_csv(csv_path="data/teams.csv"):
    df = pd.read_csv(csv_path)
    teams = [Team(row["Country"], int(row["Rating"])) for _, row in df.iterrows()]
    assert len(teams) == 48, f"Expected 48 teams, got {len(teams)}"
    return teams

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


if __name__ == "__main__":
    main()
