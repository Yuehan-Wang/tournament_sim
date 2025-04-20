import random
from itertools import combinations

class GroupStage:
    def __init__(self, teams, match_engine, group_size=4):
        self.teams = teams
        self.match_engine = match_engine
        self.group_size = group_size
        self.groups = self._create_groups()
        self.results = {}

    def _create_groups(self):
        sorted_teams = sorted(self.teams, key=lambda t: t.rating, reverse=True)
        
        pots = [sorted_teams[i*12 : (i+1)*12] for i in range(4)]
        
        for pot in pots:
            random.shuffle(pot) 

        groups = {chr(ord('A') + i): [] for i in range(12)}
        
        for group_idx in range(12):
            group_name = chr(ord('A') + group_idx)
            for pot in pots:
                selected_team = pot[group_idx]
                groups[group_name].append(selected_team)
        
        return groups

    def simulate(self):
        for group_name, teams in self.groups.items():
            self.results[group_name] = []
            for team1, team2 in combinations(teams, 2):
                winner, score, via_penalty = self.match_engine.simulate_match(team1, team2, is_knockout=False)
                team1.record_match(score[0], score[1])
                team2.record_match(score[1], score[0])
                self.results[group_name].append((team1, team2, score, winner))
                if winner is None:
                    print(f"[Group {group_name}] {team1.name} {score[0]} - {score[1]} {team2.name} → Draw")
                else:
                    print(f"[Group {group_name}] {team1.name} {score[0]} - {score[1]} {team2.name} → {winner.name} wins")

    def get_group_rankings(self):
        rankings = {}
        for group_name, teams in self.groups.items():
            sorted_teams = sorted(
                teams,
                key=lambda t: (t.points, t.goal_difference(), t.goals_for),
                reverse=True
            )
            rankings[group_name] = sorted_teams
        return rankings
