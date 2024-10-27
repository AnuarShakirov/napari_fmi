"""Module to load FMI files."""

from pathlib import Path

import pandas as pd


def get_available_files(path_to_folder: Path) -> list[Path]:
    """Method to return list of files within the folder.

    Args:
        path_to_folder: path to folder

    Returns: List of files within folder

    """
    return [file for file in path_to_folder.iterdir() if file.is_file()]


def load_fmi_pickle(path_to_file: Path) -> dict:
    """Method to read pickle file.

    Args:
        path_to_file: path to pickle

    Returns: pd.Dataframe

    """
    return pd.read_pickle(path_to_file)
