from sqlalchemy import create_engine
import pandas as pd

# loads csvs from transform
df = pd.read_csv('etl_output/game_indexed_20260120.csv')
player_summary = pd.read_csv('etl_output/player_summary_20260120.csv')

# connect
engine = create_engine("postgresql+psycopg2://bportwsoccer_user:bportwsoccer_pass@localhost:5432/soccer_etl")

# load tables into postgresql
df.to_sql('game_indexed', engine, if_exists='replace', index=False)
player_summary.to_sql('player_summary', engine, if_exists='replace', index=False)

print("Tables successfully loaded.")
