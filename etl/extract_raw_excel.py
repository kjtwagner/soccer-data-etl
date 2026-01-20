import numpy as np
import pandas as pd

file = '../data/raw/gng_2025_alldata_formatted.xlsx' #day 8 has 4 games only

df = pd.read_excel(file,header=6)
# fix naming convention to remove spaces
df.columns = (df.columns.str.strip().str.lower().str.replace(" ", "_"))

## Get one row per player, per game
# repeating col names (38 games per player)
# make one row per player per game (split)
repeat_cols = ['team', 'team_pts', 'goals', 'total'] # ignore total on day for now

records = []

for i in range(0, 39):
    suffix = '' if i == 0 else f'.{i}' # ie since no team.0 

    cols = [c + suffix for c in repeat_cols]
    if not all(c in df.columns for c in cols):
        continue

    temp = df[['last', 'first'] + cols].copy()
    temp.columns = ['last', 'first', 'team', 'team_pts', 'goals', 'total']
    temp['game_index'] = i + 1

    records.append(temp)

long_df = pd.concat(records, ignore_index=True)

## Some vals were calculate (when player was sick/absent)
impute_cols = ['goals', 'team_pts'] #cols where calculated avg may be used

long_df['is_imputed'] = False #default to assume observed

for col in impute_cols:
    fractional = long_df[col] % 1 != 0 #filling with player's own avg causes float. Obs always int
    long_df.loc[fractional, 'is_imputed'] = True

# just track this explicity
long_df['impute_method'] = np.where(long_df['is_imputed'],'player_average','observed')

# save csv for ease
long_df.to_csv("../data/staged/player_game_stats.csv", index=False)
