"""Module to load FMI files."""

from pathlib import Path

import lasio
import pandas as pd
from openpyxl.utils.exceptions import InvalidFileException

from .constants import N_COLS_FORMATION_TOPS


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


def load_formation_tops(path: Path) -> (pd.DataFrame, str):
    """Method to load formation tops data from xlsx file."""
    # get file name
    file_name = path.name
    # try to open file
    try:
        df_form = pd.read_excel(path)
    except InvalidFileException as e:
        message = f"Can not open file {file_name}. Error message is: {e}"
        return pd.DataFrame(), message
    # check if file is empty
    if df_form.empty:
        message = f"File {file_name} is empty!"
        return pd.DataFrame(), message
    # Define conditions
    condition_aap = (df_form == "AAP").any(axis=1)
    condition_aop = (df_form == "AOP").any(axis=1)
    # Filter the DataFrame
    if condition_aap.any():
        df_filtered = df_form[condition_aap]
    elif condition_aop.any():
        df_filtered = df_form[condition_aop]
    else:
        df_filtered = df_form.copy()
    # check if n columns is 6
    if df_filtered.shape[1] != N_COLS_FORMATION_TOPS:
        message = "For well column names are not correct." " Table should contain 6 columns!"
        return pd.DataFrame(), message
    # raname columns
    df_filtered.columns = ["TOP", "FORMATION_SHORT", "FORMATION", "LATERAL", "VERSION", "DATE"]
    # get only TOP and FORMATION columns
    df_filtered = df_filtered[["TOP", "FORMATION"]]
    # generate BOTTOM AND WELL columns
    df_filtered["BOTTOM"] = df_filtered.TOP.shift(-1)
    df_filtered["BOTTOM"].iloc[-1] = df_filtered.TOP.iloc[-1] + 20000
    return df_filtered, ""
