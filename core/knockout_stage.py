import random

class KnockoutStage:
    def __init__(self, teams, match_engine):
        assert len(teams) in [16, 32]
        self.teams = teams
        self.match_engine = match_engine
        self.rounds = []
        self.winner = None
        self.eliminated = {}

    def simulate(self):
        current_round = self.teams[:]
        round_num = 1
        round_size = len(current_round)
        while len(current_round) > 1:
            random.shuffle(current_round)
            next_round = []
            matches = []
            print(f"\nRound of {round_size}")
            for i in range(0, len(current_round), 2):
                team1, team2 = current_round[i], current_round[i+1]
                winner, score, via_penalty = self.match_engine.simulate_match(team1, team2, is_knockout=True)
                loser = team2 if winner == team1 else team1
                self.eliminated[loser] = round_size
                matches.append((team1, team2, score, winner, via_penalty))
                next_round.append(winner)
                if via_penalty:
                    print(f"{team1.name} {score[0]} - {score[1]} {team2.name} -> {winner.name} wins on penalties")
                else:
                    print(f"{team1.name} {score[0]} - {score[1]} {team2.name} -> {winner.name} wins")
            self.rounds.append(matches)
            current_round = next_round
            round_size = len(current_round)
            round_num += 1
        self.winner = current_round[0]
        print(f"\nChampion: {self.winner.name}")

    def get_champion(self):
        return self.winner

    def display_rankings(self):
        print("\nFinal Rankings (by elimination round):")
        ranks = {1: [self.winner]}
        final_round = self.rounds[-1]
        last_match = final_round[0]
        runner_up = last_match[0] if last_match[0] != self.winner else last_match[1]
        ranks[2] = [runner_up]
        semi_final_round = self.rounds[-2]
        third_place = []
        for match in semi_final_round:
            if match[3] != self.winner and match[3] != runner_up:
                third_place.append(match[3])
        buckets = {
            4: [],
            8: [],
            16: [],
            32: []
        }
        for team, round_out in self.eliminated.items():
            if round_out in buckets:
                buckets[round_out].append(team)
        def print_rank(range_str, teams):
            for t in sorted(teams, key=lambda x: (-x.points, -x.goal_difference(), -x.goals_for)):
                print(f"{range_str:10} {t.name:20} Elo: {t.rating}")
        print_rank("1st", ranks[1])
        print_rank("2nd", ranks[2])
        print_rank("3rd", third_place)
        print_rank("4th", buckets[4])
        print_rank("5th-8th", buckets[8])
        print_rank("9th-16th", buckets[16])
        print_rank("17th-32nd", buckets[32])
