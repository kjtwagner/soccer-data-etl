import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def cluster_games(df, features=None, n_clusters=3, random_state=42):
    """
    cluster individual games using KMeans.

    params:
    - df: player stats - game by game table
    - features: cols to use for clustering
    - n_clusters: num clusters

    returns:
    - df: original df with "cluster_label" column
    - kmeans: fitted KMeans object
    """
    
    if features is None:
        features = ['goals', 'team_pts', 'rank_in_game', 'cumulative_score']

    # features must exist
    for f in features:
        if f not in df.columns:
            raise ValueError(f"Feature '{f}' not in dataframe.")
    
    # extract features and standardize
    X = df[features].copy()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # kmeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    # add to original df for plotting
    df = df.copy()
    df["cluster_label"] = cluster_labels
    
    return df, kmeans
