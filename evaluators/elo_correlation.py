import numpy as np
from scipy import stats
import pandas as pd

class EloCorrelationEvaluator:
    def __init__(self):
        self.correlation_results = []

    def evaluate(self, final_standings, initial_elos):
        merged_data = pd.merge(
            final_standings[['team', 'position']],
            initial_elos[['team', 'elo']],
            on='team'
        )
        merged_data = merged_data.sort_values('elo', ascending=False)
        merged_data['elo_rank'] = range(1, len(merged_data) + 1)
        merged_data['rank_diff'] = abs(merged_data['position'] - merged_data['elo_rank'])
        merged_data['reverse_position'] = len(merged_data) - merged_data['position'] + 1
        correlation, p_value = stats.spearmanr(
            merged_data['reverse_position'],
            merged_data['elo']
        )
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
        if not self.correlation_results:
            return "No evaluations performed yet."
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
        try:
            import matplotlib.pyplot as plt
            merged_data = pd.merge(
                final_standings[['team', 'position']],
                initial_elos[['team', 'elo']],
                on='team'
            )
            merged_data = merged_data.sort_values('elo', ascending=False)
            merged_data['elo_rank'] = range(1, len(merged_data) + 1)
            plt.figure(figsize=(10, 6))
            plt.scatter(merged_data['elo'], merged_data['position'])
            for i, row in merged_data.iterrows():
                plt.annotate(row['team'], 
                           (row['elo'], row['position']),
                           xytext=(5, 5), textcoords='offset points')
            z = np.polyfit(merged_data['elo'], merged_data['position'], 1)
            p = np.poly1d(z)
            plt.plot(merged_data['elo'], p(merged_data['elo']), "r--")
            plt.title('Final Position vs Initial ELO')
            plt.xlabel('Initial ELO')
            plt.ylabel('Final Position')
            correlation = stats.spearmanr(merged_data['position'], merged_data['elo'])[0]
            plt.annotate(f'Correlation: {correlation:.3f}',
                        xy=(0.05, 0.95), xycoords='axes fraction')
            plt.tight_layout()
            return plt
        except ImportError:
            print("Matplotlib is required for plotting. Please install it using 'pip install matplotlib'")
            return None 