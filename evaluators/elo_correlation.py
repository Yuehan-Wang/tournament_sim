import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

class EloCorrelationEvaluator:
    """
    Evaluate correlation between pre-tournament Elo ratings and final standings.
    Supports Spearman correlation, rank difference analysis, and plotting.
    """

    def __init__(self):
        """ Initialize the evaluator with an empty result history. """
        self.correlation_results = []

    def evaluate(self, final_standings, initial_elos):
        """ Compute correlation between Elo and final position for a single tournament. """
        # Merge by team and sort teams by descending Elo
        merged_data = pd.merge(final_standings[['team', 'position']], initial_elos[['team', 'elo']], on = 'team')
        merged_data = merged_data.sort_values('elo', ascending = False)

        # Assign Elo-based rank (1 = highest Elo)
        merged_data['elo_rank'] = range(1, len(merged_data) + 1)

        # Compute absolute difference between actual and Elo-predicted positions
        merged_data['rank_diff'] = abs(merged_data['position'] - merged_data['elo_rank'])

        # Reverse position so higher rank = better finish (for correlation)
        merged_data['reverse_position'] = len(merged_data) - merged_data['position'] + 1

        # Spearman correlation between Elo and reverse final position
        correlation, p_value = stats.spearmanr(merged_data['reverse_position'], merged_data['elo'])

        result = {
            'correlation': correlation,
            'p_value': p_value,
            'n_teams': len(merged_data),
            'max_diff': merged_data['rank_diff'].max(),
            'avg_diff': merged_data['rank_diff'].mean()
        }

        self.correlation_results.append(result)
        return result

    def get_summary(self):
        """ Summarize all evaluations conducted so far. """
        if not self.correlation_results: return "No evaluations performed yet."

        # Extract fields across all evaluations
        correlations = [r['correlation'] for r in self.correlation_results]
        p_values = [r['p_value'] for r in self.correlation_results]
        max_diffs = [r['max_diff'] for r in self.correlation_results]
        avg_diffs = [r['avg_diff'] for r in self.correlation_results]

        summary = {
            'mean_correlation': np.mean(correlations),
            'std_correlation': np.std(correlations),
            'min_correlation': np.min(correlations),
            'max_correlation': np.max(correlations),
            'mean_p_value': np.mean(p_values),
            'n_evaluations': len(self.correlation_results),
            'mean_max_diff': np.mean(max_diffs),
            'mean_avg_diff': np.mean(avg_diffs)
        }

        return summary

    def plot_correlation(self, final_standings, initial_elos):
        """ Plot relationship between Elo rating and final position. """
        try:
            merged_data = pd.merge(final_standings[['team', 'position']], initial_elos[['team', 'elo']], on = 'team')
            merged_data = merged_data.sort_values('elo', ascending = False)
            merged_data['elo_rank'] = range(1, len(merged_data) + 1)

            # Scatter plot: Elo vs final position
            plt.figure(figsize = (10,7))
            plt.scatter(merged_data['elo_rank'], merged_data['position'], s = 30)

            # Annotate each team
            for _, row in merged_data.iterrows(): plt.annotate(row['team'], (row['elo_rank'], row['position']), xytext = (5, 5), textcoords = 'offset points')

            # Add linear trend line
            z = np.polyfit(merged_data['elo_rank'], merged_data['position'], 1)
            p = np.poly1d(z)
            plt.plot(merged_data['elo_rank'], p(merged_data['elo_rank']), "r--")

            # Show correlation on plot
            correlation = stats.spearmanr(merged_data['position'], merged_data['elo_rank'])[0]
            plt.annotate(f'Correlation: {correlation:.3f}', xy = (0.025, 0.950), xycoords = 'axes fraction', fontsize = 12)

            # Final plot formatting
            plt.title('Final Position vs Initial ELO', fontsize = 18, pad = 15)
            plt.xlabel('Initial ELO', fontsize = 12)
            plt.ylabel('Final Position', fontsize = 12)

            elo_min = merged_data['elo_rank'].min()
            elo_max = merged_data['elo_rank'].max()
            plt.xticks(np.arange(0, elo_max + 2))

            pos_min = merged_data['position'].min()
            pos_max = merged_data['position'].max()
            plt.yticks(np.arange(int(pos_min // 5 * 5), int(pos_max // 5 * 5) + 6, 5))

            plt.tight_layout()
            return plt

        except ImportError:
            print("Matplotlib is required for plotting. Please install it using 'pip install matplotlib'")
            return None 
