
# Tournament Sim

A small, self-contained framework for stress-testing football tournament designs.  
The current release reproduces the three formats analysed in our paper:

| Format                             | Code class                              | Matches | Notes                      |
|------------------------------------|------------------------------------------|---------|----------------------------|
| 12 × 4 groups → 32-team KO (FIFA 2026) | `formats.fifa2026.FIFA2026Tournament` | 104     | Official World-Cup structure |
| 32-team single-elimination         | `formats.playoff.PlayoffTournament`      | 31      | “Pure play-off” baseline   |
| 8-round Swiss league               | `formats.swiss.SwissTournament`          | 192     | No knock-out phase         |

The simulator tracks two headline metrics:

- **Elo–finish correlation** (Spearman ρ, plus avg / max position error)  
- **Low-incentive fixtures** — group games where both sides are already safe or already eliminated before kick-off

---

## 1. Installation

```bash
git clone https://github.com/Yuehan-Wang/tournament_sim.git
cd tournament_sim
python -m venv venv && source venv/bin/activate      # optional
pip install -r requirements.txt
```

All dependencies are pure-Python (`pandas`, `numpy`, `matplotlib`).

---

## 2. Project layout

```
core/            generic plumbing (Team, MatchEngine, Group/KOs)
formats/         real-world presets (fifa2026, playoff, swiss)
evaluators/      post-hoc metrics (elo_correlation, incentive_compatibility)
data/teams.csv   48-team Elo table (FiveThirtyEight, Nov-2025 snapshot)
main.py          one-click driver → summary CSV + PNG plots
```

---

## 3. Running a full experiment

```bash
python main.py
```

Outputs:

- `correlation_fifa.png`, `correlation_pure_play_off.png`,  
  `correlation_8-round_swiss.png` – scatter plots

- `tournament_summary.csv` – side-by-side table  
  (format, correlation, avg_diff, low_incentive, total_matches, pct_low_incentive)

Example console output:

```
[FIFA 2026]
Correlation: 0.828 | Avg pos diff: 3.94
Low-incentive games: 12/72 (16.7 %)

[Pure Play-off]
Correlation: 0.610 | Avg pos diff: 6.77
Low-incentive games: 0/31 (0.0 %)

[8-round Swiss]
Correlation: 0.904 | Avg pos diff: 2.48
Low-incentive games: 0/192 (0.0 %)
```

---

## 4. Extending

### Add a format
Create `formats/my_format.py`, subclassing `core.GroupStage`,  
`core.KnockoutStage`, or rolling your own `run()` / `get_rankings()`.

### Add a metric
Drop an evaluator in `evaluators/` that exposes:  
```python
evaluate(tournament_or_df) -> dict
```

`main.py` is purposely compact—feel free to wrap it in your own batch-runner  
or integrate it with Jupyter for deeper plots.

---

## 5. Licence

MIT Licence © 2025 Yuehan Wang  
Real-world Elo data © FiveThirtyEight.
