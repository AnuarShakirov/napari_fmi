"""Module to visualize logging data and BHI."""

import os
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from qtpy.QtCore import QUrl
from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtWidgets import QFileDialog
from scipy.ndimage import gaussian_filter, gaussian_filter1d

from .constants import SAMPLING_STEP, SIGMA
from .gui_logs import LogsBase
from .loaders import load_las
from .protocol_classes import FMIProcessorProtocol
from .visualization import logview


warnings.filterwarnings("ignore")


class LogsProcessor(LogsBase):
    """Class to create widget for logging data manipulation."""

    def __init__(self, fmi_processor: FMIProcessorProtocol) -> None:
        super().__init__(fmi_processor.viewer)
        self.fmi_processor = fmi_processor
        self.init_click_events()

        self.logging_data: pd.DataFrame | None = None
        self.fmi_image_cur: NDArray | None = None
        self.fmi_segmentation_results: NDArray | None = None
        self.fmi_image_depth_cur: NDArray | None = None
        self.fmi_porosity: NDArray | None = None

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
        self.prepare_fmi_segmentation_results()
        self.prepare_fmi_porosity()
        self.prepare_fmi_image_depth()

        # Define the columns and create the Plotly figure
        cols_to_keep = [col for col in self.logging_data][:7]
        self.plot_main = logview(
            df_log=self.logging_data[cols_to_keep],
            fmi_image=self.fmi_image_cur,
            fmi_segmentation=self.fmi_segmentation_results,
            fmi_depth=self.fmi_image_depth_cur,
            fmi_porosity=self.fmi_porosity,
        )

        # Generate the HTML with Plotly
        html_content = self.plot_main.to_html(include_plotlyjs="cdn")

        # Add custom CSS to change the background color of the container
        css = """
        <style>
            body {
                background-color: black;
            }
            .plot-container {
                background-color: black;
            }
        </style>
        """
        html_content = css + html_content

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
        fmi_image_cur = self.process_fmi_data(fmi_image_cur)
        self.fmi_image_cur = fmi_image_cur

    def prepare_fmi_image_depth(self) -> None:
        """Method to prepare FMI image depth for visualization."""
        fmi_image_depth_cur = self.fmi_processor.current_file["DEPT"].copy()
        fmi_image_depth_cur = self.sample_rows(fmi_image_depth_cur)
        self.fmi_image_depth_cur = fmi_image_depth_cur

    def prepare_fmi_segmentation_results(self) -> None:
        """Method to prepare FMI segmentation results for visualization."""
        fmi_segmentation_results = self.fmi_processor.mask_layer.data.copy()
        fmi_segmentation_results = self.process_fmi_data(fmi_segmentation_results * 255)
        self.fmi_segmentation_results = fmi_segmentation_results

    def prepare_fmi_porosity(self) -> None:
        """Method to prepare FMI porosity for visualization."""
        # prepare fmi porosity
        fmi_mask = self.fmi_processor.fmi_mask.copy()
        fmi_porosity = fmi_mask.sum(axis=1) / fmi_mask.shape[1]
        # Remove NaN values form fmi image
        fmi_porosity = self.process_fmi_data(fmi_porosity, single_dim=True)
        self.fmi_porosity = fmi_porosity

    @staticmethod
    def sample_rows(data: NDArray) -> NDArray:
        """Method to sample every Nth row."""
        return data[::SAMPLING_STEP]

    def process_fmi_data(self, data: NDArray, single_dim: bool = False) -> NDArray:
        """Method to process FMI data."""
        # remove negative values
        data = np.where(data < -99, np.nan, data)
        # substitute nan / inf to 0
        data = np.nan_to_num(data, nan=0, posinf=0, neginf=0)
        # sample every Nth row
        data = self.sample_rows(data)
        # apply smoothing
        if single_dim:
            return gaussian_filter1d(data, sigma=SIGMA)
        return gaussian_filter(data, sigma=SIGMA)
