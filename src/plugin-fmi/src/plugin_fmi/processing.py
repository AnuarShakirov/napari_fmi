"""Module for processing."""

import numpy as np
import pandas as pd
from numpy.typing import NDArray


def get_boolean_mask(fmi_image: NDArray, threshold: int) -> NDArray:
    """Method to prepare boolean (0 or 1) mask for fmi image.

    Args:
        fmi_image: raw input array
        threshold: threshold value for making 0 or 1
    Returns:
        boolean 2d NDArray
    """
    return np.where(fmi_image < threshold, 1, 0)


def get_whashout_curve(fmi_boolean: NDArray) -> np.array:
    """Method to visualize curve representing content of whashouts.

    Args:
        fmi_boolean: array to calculate the whashout

    """
    # obtain curve
    height, width = fmi_boolean.shape
    fmi_sum = fmi_boolean.sum(axis=1) / width
    x = np.arange(height)
    y = fmi_sum * width
    return np.vstack((x, y)).T


def pivot_data_for_visualization(
    df_strat: pd.DataFrame,
    col_reference: str = "FORMATION",
    col_depth: str = "TOP",
    depth_step: float = 0.5,
) -> pd.DataFrame:
    """Method to pivot data for visualization."""
    # pivot table
    df_pivot = (
        df_strat[[col_depth, col_reference]]
        .dropna()
        .pivot(index=col_depth, columns=col_reference, values=col_depth)  # noqa: PD010
    )
    # fillna with 0
    df_pivot = df_pivot.fillna(0)
    # replace all non na values with 100
    df_pivot[df_pivot != 0] = 100
    # reset index
    df_pivot = df_pivot.reset_index()
    # rename Кровля to MD
    df_pivot.rename(columns={col_depth: "DEPTH"}, inplace=True)
    # resample the dataframe
    start, end = df_pivot["DEPTH"].min(), df_pivot["DEPTH"].max()
    new_md = list(np.arange(start, end + depth_step, depth_step))
    resampled_df = pd.DataFrame(new_md, columns=["DEPTH"])
    return resampled_df.merge(df_pivot, on="DEPTH", how="outer").sort_values(by="DEPTH").ffill()
