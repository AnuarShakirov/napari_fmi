"""Module for processing."""

import numpy as np
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
