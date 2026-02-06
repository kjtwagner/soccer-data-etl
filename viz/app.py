import pandas as pd
# -- packages --
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
import plotly.express as px
import streamlit as st
import numpy as np

# -- tools --
from utils import *
from ml import *

# -- import data --

engine = create_engine(
    "postgresql+psycopg2://bportwsoccer_user:bportwsoccer_pass@localhost:5432/soccer_etl"
)
df_game = pd.read_sql("SELECT * FROM game_indexed;", engine)
df_summary = pd.read_sql("SELECT * FROM player_summary;", engine)
df_roster = pd.read_csv('raw/roster.csv')

# add roster info in post
df_summary = df_summary.merge(
    df_roster[['player', 'position','height','year']],
    on='player',
    how='left'
)


# -- establish dashboard --
st.title("Soccer Player Rankings")
st.set_page_config(layout="wide")

mode = st.selectbox("View", ["All players", "Select Players", "Top 5 Overall",
                             "Top 5 Most Improved", "Bottom 5 Overall"])

# -- make filters --

final_rank = (df_game.sort_values("game_index").groupby("player").tail(1).sort_values("cumulative_rank"))

rank_change = (
    df_game
    .sort_values("game_index")
    .groupby("player")
    .agg(
        start_rank=("cumulative_rank", "first"),
        end_rank=("cumulative_rank", "last")
    )
    .assign(improvement=lambda d: d["start_rank"] - d["end_rank"])
    .sort_values("improvement", ascending=False)
)


if mode == "All players":
    filtered_game = df_game
    filtered_summary = df_summary

elif mode == "Select Players":
    players = st.multiselect(
        "Choose players",
        df_game["player"].unique(),
        default=df_game["player"].unique()[:3]
    )
    filtered_game = df_game[df_game["player"].isin(players)]
    filtered_summary = df_summary[df_summary["player"].isin(players)]

elif mode == "Top 5 Overall":
    top_players = final_rank.head(5)["player"]
    filtered_game = df_game[df_game["player"].isin(top_players)]
    filtered_summary = df_summary[df_summary["player"].isin(top_players)]

elif mode == "Top 5 Most Improved":
    top_players = rank_change.head(5).index
    filtered_game = df_game[df_game["player"].isin(top_players)]
    filtered_summary = df_summary[df_summary["player"].isin(top_players)]

elif mode== "Bottom 5 Overall":
    bottom_players = final_rank.tail(5)["player"]
    filtered_game = df_game[df_game["player"].isin(bottom_players)]
    filtered_summary = df_summary[df_summary["player"].isin(bottom_players)]

# -- get plots --

cumulative = plot_cumulative(filtered_game)
st.plotly_chart(cumulative, use_container_width=True)

bubble = plot_bubble(filtered_game)
st.plotly_chart(bubble, use_container_width=True)

bar = player_histogram(filtered_game)
st.plotly_chart(bar, use_container_width=True)

heat = create_heatmap(filtered_game)
st.plotly_chart(heat, use_container_width=True)

fig1, fig2 = plot_goals_and_rank(filtered_summary)
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.plotly_chart(fig2, use_container_width=True)


# # -- ml stuff --
# # sidebar controls
# st.sidebar.header("Clustering Options")
# features = st.sidebar.multiselect(
#     "Features for clustering",
#     options=['goals', 'team_pts', 'rank_in_game', 'cumulative_score', 'cumulative_percentile'],
#     default=['goals', 'team_pts', 'rank_in_game', 'cumulative_score']
# )
# n_clusters = st.sidebar.slider("Number of clusters", 2, 6, 3)
# selected_players = st.sidebar.multiselect("Select players to display", options=filtered_game['player'].unique(), default=None)

# # perform clustering
# clustered_df, kmeans_model = cluster_games(filtered_game, features=None, n_clusters=n_clusters)

# # scatter plot
# st.subheader("Scatter Plot of Clusters")
# scatter_fig = plot_game_clusters(clustered_df, x=features[0], y=features[1])
# st.plotly_chart(scatter_fig, use_container_width=True)

# # heatmap
# st.subheader("Cluster Heatmap: Player vs Game Index")
# heatmap_fig = plot_cluster_heatmap(clustered_df)
# st.plotly_chart(heatmap_fig, use_container_width=True)
