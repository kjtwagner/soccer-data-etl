import pandas as pd
import os
from datetime import datetime

data_staged = '../data/staged/player_game_stats.csv'
df = pd.read_csv(data_staged)

df['player'] = df['first'] + ' ' + df['last']

## add more per game metrics to game-indexed table

df['rank_in_game'] = df.groupby('game_index')['total'].rank(ascending=False, method='min')

# cumulative totals and ranks
df['cumulative_goals'] = df.groupby('player')['goals'].cumsum()
df['cumulative_score'] = df.groupby('player')['total'].cumsum()
df['cumulative_rank'] = df.groupby('game_index')['cumulative_score'].rank(ascending=False, method='min')

# percentile ranks
df['cumulative_percentile'] = df.groupby('game_index')['cumulative_score'].rank(pct=True)
df['cumulative_goals_percentile'] = df.groupby('game_index')['cumulative_goals'].rank(pct=True)

## make player summary for season aggregates - avoid game index table redundancy
player_summary = df.groupby('player').agg(
    total_goals=('goals', 'sum'),
    overall_score=('total', 'sum'),
    avg_score_per_game=('total', 'mean'),
    games_played_total=('game_index','count'),
    games_played_actual=('is_imputed', lambda x: (x==0).sum()),
    max_total=('total','max'),
    min_total=('total','min'),
    avg_goals_per_game=('goals','mean')
).reset_index()

## export
output_folder = 'etl_output'
os.makedirs(output_folder, exist_ok=True)
ts = datetime.now().strftime('%Y%m%d')

df.to_csv(os.path.join(output_folder, f'game_indexed_{ts}.csv'), index=False)
player_summary.to_csv(os.path.join(output_folder, f'player_summary_{ts}.csv'), index=False)

