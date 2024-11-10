"""Module for visualizations."""

import warnings

import pandas as pd
import plotly
import plotly.graph_objects as go
from numpy.typing import NDArray
from plotly.subplots import make_subplots


warnings.filterwarnings("ignore")


def logview(  # noqa: PLR0913
    df_log: pd.DataFrame,
    fmi_image: NDArray | None = None,
    fmi_depth: NDArray | None = None,
    fmi_segmentation: NDArray | None = None,
    df_lith_mixed: pd.DataFrame | None = pd.DataFrame(),
    df_lith_dominant: pd.DataFrame | None = pd.DataFrame(),
    df_formation: pd.DataFrame | None = pd.DataFrame(),
    features_to_log: list = [],
    col_depth: str = "DEPTH",
) -> plotly.subplots.make_subplots:
    """Method to visualize the logs.

    Args:
        df_log: dataframe containing well logging data
        fmi_image: dataframe containing FMI image data
        fmi_depth: dataframe containing FMI depth data
        fmi_segmentation: dataframe containing FMI segmentation data
        df_lith_mixed: dataframe containing mixed lithology data
        df_lith_dominant: dataframe containing dominant lithology data
        df_formation: dataframe containing formation tops data
        features_to_log: list of features to log
        col_depth: column name for depth

    Returns:
        plotly.subplots.make_subplots: plotly figure
    """
    num_cols = len(features_to_log) if features_to_log else df_log.shape[1]

    # Add columns for additional data
    if not fmi_image is None:
        num_cols += 1
    if not fmi_segmentation is None:
        num_cols += 1
    if not df_lith_mixed.empty:
        num_cols += 1
    if not df_lith_dominant.empty:
        num_cols += 1
    if not df_formation.empty:
        num_cols += 1
    # Create the figure
    fig = make_subplots(rows=1, cols=num_cols, shared_yaxes=True)
    features = [col for col in df_log.columns if col not in [col_depth] + ["WELL"]]
    col_numbers = 0

    for ix, feat in enumerate(features):
        fig.add_trace(
            go.Scatter(
                x=df_log[feat],
                y=df_log[col_depth],
                mode="lines",
                line={"color": "white", "width": 1},
                name=feat,
            ),
            row=1,
            col=ix + 1,
        )

        fig.update_xaxes(
            title={"text": feat, "font": {"color": "white"}},
            row=1,
            col=ix + 1,
            side="top",
            tickangle=-90,
            tickfont={"color": "white"},
            showgrid=True,
            gridcolor="gray",
            gridwidth=0.2,  # Set thinner grid lines
            layer="below traces",  # Ensure grid is below the curves
        )
        if feat in features_to_log:
            fig.update_xaxes(col=ix + 1, type="log")

        col_numbers += 1

    # plot FMI image
    if not fmi_image is None:
        fig.add_trace(
            go.Heatmap(
                z=fmi_image,
                y=fmi_depth,
                colorscale="viridis",
            ),
            row=1,
            col=col_numbers + 1,
        )
        fig.update_xaxes(
            title="FMI Image",
            titlefont={"color": "white"},
            row=1,
            col=col_numbers + 1,
            side="top",
            tickangle=-90,
            tickfont={"color": "white"},
            showgrid=True,
            gridcolor="gray",
            gridwidth=0.2,
            layer="below traces",
        )
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
                    line={"color": "white"},
                ),
                row=1,
                col=col_numbers + 1,
            )

        fig.update_xaxes(
            title="Formation tops",
            titlefont={"color": "white"},
            row=1,
            col=col_numbers + 1,
            side="top",
            tickangle=-90,
            tickfont={"color": "white"},
            automargin=True,
            showgrid=True,
            gridcolor="gray",
            gridwidth=0.2,
            layer="below traces",
        )
        col_numbers += 1

    fig.update_yaxes(
        title_text="DEPTH",
        row=1,
        col=1,
        autorange="reversed",
        tickformat=".0f",
        tickfont={"color": "white"},
        titlefont={"color": "white"},
        showgrid=True,
        gridcolor="gray",
        gridwidth=0.2,
        layer="below traces",
    )

    fig.update_layout(
        showlegend=False,
        plot_bgcolor="black",
        paper_bgcolor="black",
    )

    return fig
