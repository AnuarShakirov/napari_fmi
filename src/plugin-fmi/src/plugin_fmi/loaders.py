"""Module to load FMI files."""

from pathlib import Path

import lasio
import pandas as pd


def get_available_files(path_to_folder: Path, file_format: str = ".pkl") -> list[Path]:
    """Method to return list of files within the folder.

    Args:
        path_to_folder: path to folder
        file_format: format of files
    Returns: List of files within folder

    """
    return [file for file in path_to_folder.iterdir() if file.is_file() and file_format in file.name]


def load_fmi_pickle(path_to_file: Path) -> dict:
    """Method to read pickle file.

    Args:
        path_to_file: path to pickle

    Returns: pd.Dataframe

    """
    return pd.read_pickle(path_to_file)


def load_las(file_path: str) -> pd.DataFrame:
    """Method to load las file.

    Args:
        file_path: path to las

    Returns: pandas dataframe with logs

    """
    # Check if the file exists
    return lasio.read(file_path).df().reset_index(drop=False)
