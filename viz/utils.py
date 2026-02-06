import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

def plot_cumulative(df, y_col="cumulative_rank", title="Cumulative Rank Over Games"):
    """
    df: df: filtered dataframe with 'player', 'game_index', y_col
    y_col: column for y-axis (default 'cumulative_rank')
    title: change according to y_col
    returns line plot of cumulative value column with dots for imputed values
    """

    palette = sns.color_palette("Paired", n_colors=df["player"].nunique()).as_hex()
    # --- base line plot ---
    fig = px.line(
        df,
        x="game_index",
        y=y_col,
        color="player",
        title=title,
        color_discrete_sequence=palette,
        labels={
            "game_index": "Game Number",
            y_col: "Cumulative",
            "player": "Player"
        }
    )

    # --- markers for imputed points ---
    imputed = df[df["is_imputed"]]
    if not imputed.empty:
        fig.add_scatter(
            x=imputed["game_index"],
            y=imputed[y_col],
            mode="markers",
            marker=dict(
                color="lightgray",
                size=7,
                symbol="circle",
                opacity=0.7
            ),
            name="Imputed value",
            showlegend=True
        )

    # --- visual stuff ---
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray")
    )

    return fig

def plot_bubble(df):
    """ 
    df: filtered dataframe containing at least 'player', 'goals', 'total', 'game_index', 'cumulative_rank', 'is_imputed'
    returns bubble plot of total goals vs final rank, with bubble size reflecting % of games missed
    """

    # --- aggregate per player ---
    # in future, use player summary table? think about this
    plot_df = (df.groupby("player").agg(
        total_goals=("goals", "sum"),
        total_points=("total", "sum"),
        games_played=("game_index", "count"),
        imputed_goals=("is_imputed", "sum")
    ).reset_index())

    # --- need final rank ---
    last_game = (df.sort_values("game_index")
        .groupby("player")
        .tail(1)[["player", "cumulative_rank"]]
        .rename(columns={"cumulative_rank": "final_rank"}))
    plot_df = plot_df.merge(last_game, on="player")

    # --- imputed percentage -> bubble size ---
    plot_df["imputed_percent"] = round(100 * plot_df["imputed_goals"] / plot_df["games_played"], 2)
    plot_df["total_goals"] = plot_df["total_goals"].round(0)
    plot_df["bubble_size"] = 100 - (plot_df["imputed_percent"] / 25) * 60

    # --- make size-weighted scatter plot ---
    palette = sns.color_palette("Paired", n_colors=df["player"].nunique()).as_hex() #can this be gloabl
    fig = px.scatter(
        plot_df,
        x="total_goals",
        y="final_rank",
        size="bubble_size",
        color="player",
        color_discrete_sequence=palette,
        hover_name="player",
        hover_data={
            "total_goals": True,
            "final_rank": True,
            "games_played": False,
            "bubble_size": False,
            "imputed_percent": True
        },
        title="Total Goals vs Final Rank, Weighted by % of Games Missed",
        labels={
            "total_goals": "Total Goals",
            "final_rank": "Final Rank",
            "player": "Player",
            "imputed_percent" : "% Missed"
        }
    )

    # --- visual stuff ---
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray")
    )

    return fig


def player_histogram(df, count_val="total_points", title="Total Points vs Player"):
    """
    df: dataframe with "player" and a count value (goals, points, etc)
    coutn_val: column for x-axis (default 'total_points')
    title: chart title corr to count val
    returns horizontal bar chart of total XX per player as specified
    """

    # --- aggregate  ---
    # in future, use player summary table? think about this
    plot_df = (df.groupby("player").agg(
        total_goals=("goals", "sum"),
        total_points=("total", "sum"),
        games_played=("game_index", "count"),
        imputed_goals=("is_imputed", "sum")
    ).reset_index())

    # --- horizontal bar chart ---
    # this assumes user always wants highest ranked players at top - think about this
    palette = sns.color_palette("Paired", n_colors=df["player"].nunique()).as_hex()
    fig = px.bar(
        plot_df.sort_values(count_val, ascending=False),
        x=count_val,
        y="player",
        orientation="h",
        color="player",
        color_continuous_scale=palette,
        title=title,
        labels={
            count_val: "Total",
            "player": "Player"
        }
    )

    # --- visual stuff ---
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=False)
    )
    fig.update_traces(width=1)

    return fig

    
def create_heatmap(df, value_col="goals"):
    """
    df: filtered dataframe with 'player', 'first', 'last', 'game_index', value_col
    value_col: which data to use for z. May be changed (ie Rank, etc)
    returns a plotly heatmap figure with last-name labels and white overlay for imputed cells
    """

    # --- pivot main data and imputed mask ---
    # player and game index always used
    heatmap_df = df.pivot(index="player", columns="game_index", values=value_col).fillna(0)
    imputed_mask = df.pivot(index="player", columns="game_index", values="is_imputed").fillna(False)

    # --- alphabetize by last name ---
    label_map = df.set_index("player")["last"].to_dict()
    sorted_players = sorted(heatmap_df.index, key=lambda x: label_map[x])
    heatmap_df = heatmap_df.loc[sorted_players]
    imputed_mask = imputed_mask.loc[sorted_players]
    sorted_last_names = [label_map[p] for p in sorted_players]

    # --- main heatmap ---
    fig = go.Figure(
        go.Heatmap(
            z=heatmap_df.values,
            x=heatmap_df.columns,
            y=heatmap_df.index,
            colorscale="YlOrRd",
            colorbar=dict(title=value_col.capitalize()),
            hovertemplate="Player: %{y}<br>Game: %{x}<br>Goals: %{z}<extra></extra>"
        )
    )

    # --- gray out players' avg values ---
    imputed_overlay = np.where(imputed_mask.values, 1, np.nan)
    fig.add_trace(
        go.Heatmap(
            z=imputed_overlay,
            x=heatmap_df.columns,
            y=heatmap_df.index,
            colorscale=[[0, "white"], [1, "white"]],
            showscale=False,
            hoverinfo="skip"
        )
    )

    # --- visual stuff ---
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(
        scaleanchor="x",
        showgrid=False,
        autorange="reversed",
        tickvals=heatmap_df.index,
        ticktext=sorted_last_names
    )

    fig.update_layout(
        title="Player Goals Heatmap Over Games",
        xaxis_title="Game Index",
        width=max(600, len(heatmap_df.columns) * 20),
        height=max(400, len(heatmap_df.index) * 20)
        #height=max(300, 40 * len(heatmap_df.index)),
    )

    return fig

def plot_goals_and_rank(df):
    """
    df: overall/summary df
    scatter plot of total goals vs total points, with color selectable by position or year
    """

    df["final_rank"] = df["overall_score"].rank(ascending=False, method="min")

    # --- color scale selector ---
    color_options = []
    if "position" in df.columns:
        color_options.append("Position")
    if "year" in df.columns:
        color_options.append("Year")

    color_col = None
    if len(color_options) > 0:
        color_choice = st.selectbox("Color by", options=color_options)
        color_col = "position" if color_choice == "Position" else "year"

        # --- only show filters after color is selected ---
        if color_col == "position":
            selected_positions = st.multiselect(
                "Select Positions",
                options=df["position"].unique(),
                default=df["position"].unique()
            )
            df = df[df["position"].isin(selected_positions)]
            palette = px.colors.sequential.Magma
        else:
            selected_years = st.multiselect(
                "Select Years",
                options=df["year"].unique(),
                default=df["year"].unique()
            )
            df = df[df["year"].isin(selected_years)]
            palette = px.colors.sequential.Inferno

    # --- scatter: points vs goals ---
    fig1 = px.scatter(
        df,
        x="overall_score",
        y="total_goals",
        color=color_col,
        hover_name="player",
        size="overall_score",
        title="Total Points vs Goals Scored",
        color_discrete_sequence=palette if color_col == "position" else None,
        color_continuous_scale=palette if color_col == "year" else None,
        labels={
            "player": "Player",
            "total_goals": "Goals Scored",
            "overall_score": "Total Points",
            "position": "Position",
            "year": "Year"
        }
    )

    fig1.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray")
    )

    # --- scatter 2: points vs rank ---
    fig2 = px.scatter(
        df,
        x="overall_score",
        y="final_rank",
        color=color_col,
        hover_name="player",
        size="overall_score",
        title="Total Points vs Final Rank",
        color_discrete_sequence=palette if color_col == "position" else None,
        color_continuous_scale=palette if color_col == "year" else None,
        labels={
            "player": "Player",
            "total_goals": "Goals Scored",
            "final_rank": "Final Rank",
            "overall_score": "Total Points",
            "position": "Position",
            "year": "Year"
        }
    )
    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="lightgray"),
        yaxis=dict(showgrid=True, gridcolor="lightgray", autorange="reversed")
    )

    return fig1, fig2


# --- ml plots, not sure this is relevant for such small data ---
def plot_game_clusters(df, x='cumulative_score', y='goals'):
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color='cluster_label',
        hover_data=['player', 'game_index', 'goals', 'team_pts', 'rank_in_game'],
        title='Game-Level Player Clusters',
        labels={'cluster_label': 'Cluster'}
    )
    fig.update_xaxes(autorange="reversed")

    return fig

def plot_cluster_heatmap(df):
    """
    heatmap of clusters: player vs. game_index
    """

    pivot = df.pivot(index='player', columns='game_index', values='cluster_label')
    
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale='Viridis',
            colorbar=dict(title='Cluster')
        )
    )
    fig.update_layout(title='Player Game Clusters Heatmap', xaxis_title='Game Index', yaxis_title='Player')
    return fig
