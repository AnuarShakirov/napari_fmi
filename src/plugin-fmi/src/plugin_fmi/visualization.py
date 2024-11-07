"""Module for visualizations."""

import warnings

import pandas as pd
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

warnings.filterwarnings('ignore')

def logview(
        df_log: pd.DataFrame,
        df_lith_mixed: pd.DataFrame = pd.DataFrame(),
        df_lith_dominant: pd.DataFrame = pd.DataFrame(),
        df_formation: pd.DataFrame = pd.DataFrame(),
        features_to_log: list = [],
        col_depth: str = "DEPTH"
) -> plotly.subplots.make_subplots:
    """Method to visualize the logs.

    Args:
        df_log:
        df_lith_mixed:
        df_lith_dominant:
        df_formation:
        features_to_log:
        col_depth:

    Returns:

    """
    num_cols = len(features_to_log) if features_to_log else df_log.shape[1]

    if not df_lith_mixed.empty:
        num_cols += 1
    if not df_lith_dominant.empty:
        num_cols += 1
    if not df_formation.empty:
        num_cols += 1

    fig = make_subplots(rows=1, cols=num_cols, shared_yaxes=True)

    features = [col for col in df_log.columns if col not in [col_depth] + ['WELL']]
    col_numbers = 0

    for ix, feat in enumerate(features):
        fig.add_trace(
            go.Scatter(
                x=df_log[feat],
                y=df_log[col_depth],
                mode="lines",
                line=dict(color="white", width=1),
                name=feat,
            ),
            row=1,
            col=ix + 1,
        )

        fig.update_xaxes(
            title=dict(text=feat, font=dict(color="white")),
            row=1,
            col=ix + 1,
            side="top",
            tickangle=-90,
            tickfont=dict(color="white"),
            showgrid=True,
            gridcolor="gray",
            gridwidth=0.2,  # Set thinner grid lines
            layer="below traces"  # Ensure grid is below the curves
        )
        if feat in features_to_log:
            fig.update_xaxes(col=ix + 1, type="log")

        col_numbers += 1

    if not df_formation.empty:
        features_to_drop = ["DEPTH"]
        cols_zone = [col for col in df_formation.columns if col not in features_to_drop]

        for jx, zone in enumerate(cols_zone):
            fig.add_trace(
                go.Scatter(
                    x=df_formation[zone],
                    y=df_formation[col_depth],
                    fill="tozerox",
                    mode="lines",
                    name=zone,
                    line=dict(color="white"),
                ),
                row=1,
                col=col_numbers + 1,
            )

        fig.update_xaxes(
            title="Formation tops",
            titlefont=dict(color="white"),
            row=1,
            col=col_numbers + 1,
            side="top",
            tickangle=-90,
            tickfont=dict(color="white"),
            automargin=True,
            showgrid=True,
            gridcolor="gray",
            gridwidth=0.2,
            layer="below traces"
        )
        col_numbers += 1

    fig.update_yaxes(
        title_text="DEPTH",
        row=1,
        col=1,
        autorange="reversed",
        tickformat=".0f",
        tickfont=dict(color="white"),
        titlefont=dict(color="white"),
        showgrid=True,
        gridcolor="gray",
        gridwidth=0.2,
        layer="below traces"
    )

    fig.update_layout(
        # height=900,
        # width=1200,
        showlegend=False,
        plot_bgcolor="black",
        paper_bgcolor="black",
    )

    return fig