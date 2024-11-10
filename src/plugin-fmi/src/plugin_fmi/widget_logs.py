"""Module to visualize logging data and BHI."""

import os
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from qtpy.QtCore import QUrl
from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtWidgets import QFileDialog
from scipy.ndimage import gaussian_filter

from .gui_logs import LogsBase
from .loaders import load_las
from .protocol_class import FMIProcessorProtocol
from .visualization import logview


warnings.filterwarnings("ignore")


class LogsProcessor(LogsBase):
    """Class to create widget for logging data manipulation."""

    def __init__(self, fmi_processor: FMIProcessorProtocol) -> None:
        super().__init__(fmi_processor.viewer)
        self.fmi_processor = fmi_processor
        self.init_click_events()

        self.logging_data: pd.DataFrame | None = None
        self.fmi_image_cur: np.ndarray | None = None
        self.fmi_image_depth_cur: np.ndarray | None = None

    def init_click_events(self) -> None:
        """Method to connect click events with actions."""
        self.button_well_logging.clicked.connect(self.load_well_logging_file)
        self.button_visualize_data.clicked.connect(self.plot_layout)

    def load_well_logging_file(self) -> None:
        """Method to load well logging .las file."""
        format_filter = "las files (*.las)"
        output: str = QFileDialog.getOpenFileName(self, caption="Select .las file", filter=format_filter)[0]
        # check if nothing was selected
        if output == "":
            return
        self.path_to_las: Path = Path(output)
        self.logging_data: pd.DataFrame = load_las(self.path_to_las)
        cols_to_keep = [col for col in self.logging_data][:7]

    def plot_layout(self) -> None:
        """Method to plot the layout of the logging data."""
        # prepare fmi image for visualization
        self.prepare_fmi_image()
        # Define the columns and create the Plotly figure
        cols_to_keep = [col for col in self.logging_data][:7]
        self.plot_main = logview(
            df_log=self.logging_data[cols_to_keep],
            fmi_image=self.fmi_image_cur,
            fmi_depth=self.fmi_image_depth_cur,
        )
        # Generate the HTML with Plotly
        html_content = self.plot_main.to_html(include_plotlyjs="cdn")
        # Save the HTML content to a file
        file_path = os.path.abspath("plotly_chart.html")
        with open(file_path, "w") as f:
            f.write(html_content)

        # Load the HTML into QWebEngineView
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl.fromLocalFile(file_path))
        self.logview_tab_layout.addWidget(self.browser)

    def prepare_fmi_image(self) -> None:
        """Method to prepare FMI image for visualization."""
        fmi_image_cur = self.fmi_processor.current_layer.data.copy()
        # Remove NaN values form fmi image
        fmi_image_cur = np.nan_to_num(np.where(fmi_image_cur < -99, np.nan, fmi_image_cur), nan=0, posinf=0, neginf=0)
        # take every 10th row for visualization of fmi
        fmi_image_cur = fmi_image_cur[::10]
        # apply smoothing
        fmi_image_cur = gaussian_filter(fmi_image_cur, sigma=2)
        self.fmi_image_cur = fmi_image_cur
        self.fmi_image_depth_cur = self.fmi_processor.current_file["DEPT"][::10]
