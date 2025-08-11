"""Module for visualizations."""

import warnings

import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
from numpy.typing import NDArray
from plotly.colors import qualitative
from plotly.subplots import make_subplots
from statsmodels.api import OLS, add_constant


warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

def logview(  # noqa: PLR0913 , PLR0912, PLR0915
    df_log: pd.DataFrame,
    fmi_image: NDArray | None = None,
    fmi_depth: NDArray | None = None,
    fmi_segmentation: NDArray | None = None,
    fmi_porosity: NDArray | None = None,
    df_lith_mixed: pd.DataFrame | None = pd.DataFrame(),
    df_lith_dominant: pd.DataFrame | None = pd.DataFrame(),
    df_formation: pd.DataFrame | None = pd.DataFrame(),
    df_drilling: pd.DataFrame = pd.DataFrame(),
    features_to_log: list = [],
    col_depth: str = "DEPTH",
) -> plotly.subplots.make_subplots:
    """Method to visualize the logs.

    Args:
        df_log: dataframe containing well logging data
        fmi_image: dataframe containing FMI image data
        fmi_depth: dataframe containing FMI depth data
        fmi_segmentation: dataframe containing FMI segmentation data
        fmi_porosity: dataframe containing FMI porosity data
        df_lith_mixed: dataframe containing mixed lithology data
        df_lith_dominant: dataframe containing dominant lithology data
        df_formation: dataframe containing formation tops data
        features_to_log: list of features to log
        df_drilling: dataframe containing drilling data
        col_depth: column name for depth

    Returns:
        plotly.subplots.make_subplots: plotly figure
    """
    num_cols: int = df_log.shape[1]
    if not df_drilling.empty:
        num_cols += df_drilling.shape[1]
    # Add columns for additional data
    if not fmi_image is None:
        num_cols += 1
    if not fmi_segmentation is None:
        num_cols += 1
    if not fmi_porosity is None:
        num_cols += 1
    if not df_lith_mixed.empty:
        num_cols += 1
    if not df_lith_dominant.empty:
        num_cols += 1
    if not df_formation.empty:
        num_cols += 1
    # Create the figure
    fig = make_subplots(rows=1, cols=num_cols, shared_yaxes=True)
    features_logs = [col for col in df_log.columns if col not in [col_depth] + ["WELL"]]
    # init counter or trace number
    col_numbers = 0
    # check if bit size in drilling data if so, plot it first
    if not df_drilling.empty:
        features_drilling = [col for col in df_drilling.columns if col not in [col_depth] + ["WELL"]]
        col_depth_drilling = [col for col in df_drilling.columns if "DEPTH" in col.upper()]
        # get bit feature
        bit_features = [col for col in features_drilling if "bit" in col.lower()]
        if bit_features:
            bit_col = bit_features[0]
            features_drilling = [
                col for col in df_drilling.columns
                if col not in [col_depth, "WELL"]
                and pd.api.types.is_numeric_dtype(df_drilling[col])
                and df_drilling[col].notna().sum() > 0
            ]
            fig.add_trace(
                go.Scatter(
                    x=df_drilling[bit_col],
                    y=df_drilling[col_depth_drilling[0]],
                    mode="lines",
                    line={"color": "white", "width": 1},
                    name=bit_col,
                    fill="tozerox",
                ),
                row=1,
                col=1,
            )
            fig.update_xaxes(
                title={"text": bit_col, "font": {"color": "white"}},
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

        for feat in features_drilling:
            print(f"Plotting drilling feature: {feat}, dtype: {df_drilling[feat].dtype}, NaNs: {df_drilling[feat].isna().sum()}")
            fig.add_trace(
                go.Scatter(
                    x=df_drilling[feat],
                    y=df_drilling[col_depth],
                    mode="lines",
                    line={"color": "white", "width": 1},
                    name=feat,
                ),
                row=1,
                col=col_numbers + 1,
            )

            fig.update_xaxes(
                title={"text": feat, "font": {"color": "white"}},
                row=1,
                col=col_numbers + 1,
                side="top",
                tickangle=-90,
                tickfont={"color": "white"},
                showgrid=True,
                gridcolor="gray",
                gridwidth=0.2,  # Set thinner grid lines
                layer="below traces",  # Ensure grid is below the curves
            )
            col_numbers += 1

    for feat in features_logs:
        fig.add_trace(
            go.Scatter(
                x=df_log[feat],
                y=df_log[col_depth],
                mode="lines",
                line={"color": "white", "width": 1},
                name=feat,
            ),
            row=1,
            col=col_numbers + 1,
        )

        fig.update_xaxes(
            title={"text": feat, "font": {"color": "white"}},
            row=1,
            col=col_numbers + 1,
            side="top",
            tickangle=-90,
            tickfont={"color": "white"},
            showgrid=True,
            gridcolor="gray",
            gridwidth=0.2,  # Set thinner grid lines
            layer="below traces",  # Ensure grid is below the curves
        )
        if feat in features_to_log:
            fig.update_xaxes(col=col_numbers + 1, type="log")

        col_numbers += 1

    # plot fmi image original
    if fmi_image is not None:
        fig.add_trace(
            go.Heatmap(
                z=fmi_image,
                y=fmi_depth,
                colorscale="viridis",
                showscale=False,
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
            gridcolor="gray",
            gridwidth=0.2,
            layer="below traces",
        )
        col_numbers += 1

    # plot segmentation results for fmi image
    if fmi_segmentation is not None:
        fig.add_trace(
            go.Heatmap(
                z=fmi_segmentation,
                y=fmi_depth,
                colorscale="gray",
                showscale=False,
            ),
            row=1,
            col=col_numbers + 1,
        )
        fig.update_xaxes(
            title="FMI Segmentation",
            titlefont={"color": "white"},
            row=1,
            col=col_numbers + 1,
            side="top",
            tickangle=-90,
            tickfont={"color": "white"},
            gridcolor="gray",
            gridwidth=0.2,
            layer="below traces",
        )
        col_numbers += 1

    if fmi_porosity is not None:
        fig.add_trace(
            go.Scatter(
                x=fmi_porosity,
                y=fmi_depth,
                mode="lines",
                line={"color": "blue", "width": 1},
                name="FMI Porosity",
            ),
            row=1,
            col=col_numbers + 1,
        )

        fig.update_xaxes(
            title={"text": "FMI Porosity", "font": {"color": "white"}},
            row=1,
            col=col_numbers + 1,
            side="top",
            tickangle=-90,
            tickfont={"color": "white"},
            showgrid=True,
            gridcolor="gray",
            gridwidth=0.2,  # Set thinner grid lines
            layer="below traces",  # Ensure grid is below the curves
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


def cross_plot(  # noqa: PLR0913, PLR0912
    df_cur: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_scale: str = "linear",
    y_scale: str = "linear",
    interpolate: bool = False,
) -> go.Figure:
    """Method to visualize the cross plot using Plotly."""
    # Handle non-positive values for log scale
    if x_scale == "log":
        df_cur = df_cur[df_cur[x_col] > 0]
    if y_scale == "log":
        df_cur = df_cur[df_cur[y_col] > 0]

    # Make interpolation for curves with lower number of missing points
    if interpolate:
        depth_step_x = df_cur[df_cur[x_col].notna()]["DEPTH"].diff().mean()
        depth_step_y = df_cur[df_cur[y_col].notna()]["DEPTH"].diff().mean()
        if depth_step_x < depth_step_y:
            df_cur[x_col] = df_cur[x_col].interpolate(method="linear")
        else:
            df_cur[y_col] = df_cur[y_col].interpolate(method="linear")

    if "FORMATION" in df_cur.columns:
        df_cur["FORMATION"] = df_cur["FORMATION"].ffill()

    x_data = df_cur[x_col]
    y_data = df_cur[y_col]

    x_bins = {}
    y_bins = {}
    if x_scale == "log":
        x_bins = {
            "start": np.log10(x_data.min()),
            "end": np.log10(x_data.max()),
            "size": 0.1,
        }
    if y_scale == "log":
        y_bins = {
            "start": np.log10(y_data.min()),
            "end": np.log10(y_data.max()),
            "size": 0.1,
        }

    fig = go.Figure()

    if "FORMATION" in df_cur.columns:
        unique_formations = df_cur["FORMATION"].unique()
        color_palette = qualitative.Plotly
        color_map = {formation: color_palette[i % len(color_palette)] for i, formation in enumerate(unique_formations)}
        df_cur["color"] = df_cur["FORMATION"].map(color_map)
    else:
        df_cur["color"] = "royalblue"

    if "FORMATION" in df_cur.columns:
        for formation in unique_formations:
            formation_data = df_cur[df_cur["FORMATION"] == formation]
            fig.add_trace(
                go.Scatter(
                    x=formation_data[x_col],
                    y=formation_data[y_col],
                    mode="markers",
                    name=formation,
                    marker={"color": color_map[formation]},
                    text=formation_data["FORMATION"],
                    hovertemplate="<b>X:</b> %{x}<br><b>Y:</b> %{y}<br><b>Formation:</b> %{text}<br><extra></extra>",
                    showlegend=True,
                ),
            )
    else:
        fig.add_trace(
            go.Scatter(
                x=x_data,
                y=y_data,
                mode="markers",
                name="Data Points",
                marker={"color": "royalblue"},
                hovertemplate="<b>X:</b> %{x}<br><b>Y:</b> %{y}<br><extra></extra>",
            ),
        )

    df_no_na = df_cur.dropna(subset=[x_col, y_col])
    X = add_constant(df_no_na[x_col].values)
    y = df_no_na[y_col].values
    model = OLS(y, X).fit()
    trendline_x = np.linspace(df_no_na[x_col].min(), df_no_na[x_col].max(), 100)
    trendline_y = model.predict(add_constant(trendline_x))

    intercept = model.params[0]
    slope = model.params[1]
    r_squared = model.rsquared

    fig.add_trace(
        go.Scatter(
            x=trendline_x,
            y=trendline_y,
            mode="lines",
            name="Trendline (OLS)",
            line={"color": "red", "dash": "dash"},
            hovertemplate=f"y = {intercept:.2f} + {slope:.2f}x<br>R² = {r_squared:.2f}<br>",
        ),
    )

    fig.add_trace(
        go.Histogram(
            x=x_data,
            name=f"{x_col}",
            yaxis="y2",
            opacity=0.5,
            marker={"color": "blue"},
            showlegend=False,
            autobinx=x_scale != "log",
            xbins=x_bins if x_scale == "log" else None,
        ),
    )
    fig.add_trace(
        go.Histogram(
            y=y_data,
            name=f"{y_col}",
            xaxis="x2",
            opacity=0.5,
            marker={"color": "green"},
            showlegend=False,
            autobiny=y_scale != "log",
            ybins=y_bins if y_scale == "log" else None,
        ),
    )

    fig.update_layout(
        xaxis={
            "title": x_col,
            "type": x_scale,
            "domain": [0, 0.85],
            "tickcolor": "white",
            "tickfont": {"color": "white"},
            "titlefont": {"color": "white"},
            "gridcolor": "white",
            "zerolinecolor": "white",
        },
        yaxis={
            "title": y_col,
            "type": y_scale,
            "domain": [0, 0.85],
            "tickcolor": "white",
            "tickfont": {"color": "white"},
            "titlefont": {"color": "white"},
            "gridcolor": "white",
            "zerolinecolor": "white",
        },
        xaxis2={
            "domain": [0.85, 1],
            "showgrid": False,
            "zeroline": False,
        },
        yaxis2={
            "domain": [0.85, 1],
            "showgrid": False,
            "zeroline": False,
        },
        bargap=0.1,
        plot_bgcolor="black",
        paper_bgcolor="black",
    )

    fig.update_layout(
        showlegend=True,
        xaxis_layer="below traces",
        yaxis_layer="below traces",
    )

    return fig
