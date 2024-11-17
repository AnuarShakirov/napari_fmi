"""Module to visualize logging data and BHI."""

import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from napari.utils.notifications import show_info
from numpy.typing import NDArray
from qtpy.QtCore import QUrl
from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtWidgets import (
    QFileDialog,
)
from scipy.ndimage import gaussian_filter, gaussian_filter1d

from .constants import ENCODED_NONE, SAMPLING_STEP, SIGMA
from .gui_logs import LogsBase
from .loaders import load_formation_tops, load_las
from .processing import pivot_data_for_visualization
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
        self.formation_tops_data: pd.DataFrame = pd.DataFrame()
        self.drilling_data: pd.DataFrame = pd.DataFrame()

        self.drilling_data_to_plot: pd.DataFrame = pd.DataFrame()
        self.logging_data_to_plot: pd.DataFrame = pd.DataFrame()

    def init_click_events(self) -> None:
        """Method to connect click events with actions."""
        self.button_well_logging.clicked.connect(self.load_well_logging_file)
        self.button_visualize_data.clicked.connect(self.plot_layout)
        self.button_formation_tops.clicked.connect(self.load_formation_tops_file)
        self.button_drilling_data.clicked.connect(self.load_drilling_data_file)

    def load_well_logging_file(self) -> None:
        """Method to load well logging .las file."""
        format_filter = "las files (*.las)"
        output: str = QFileDialog.getOpenFileName(self, caption="Select .las file", filter=format_filter)[0]
        # check if nothing was selected
        if output == "":
            return
        self.path_to_well_logging: Path = Path(output)
        self.logging_data: pd.DataFrame = load_las(self.path_to_well_logging)
        self.update_selectbox_for_logs()
        self.update_qlabel_for_selected_logs()

    def load_formation_tops_file(self) -> None:
        """Method to load formation tops .xlsx file."""
        format_filter = "xlsx files (*.xlsx)"
        output: str = QFileDialog.getOpenFileName(self, caption="Select .xlsx file", filter=format_filter)[0]
        # check if nothing was selected
        if output == "":
            return
        self.path_to_formation_tops: Path = Path(output)
        formation_tops_data, msg = load_formation_tops(self.path_to_formation_tops)
        if msg != "":
            show_info(msg)
            return

        self.formation_tops_data = pivot_data_for_visualization(formation_tops_data)
        self.update_qlabel_for_selected_formation_tops()

    def load_drilling_data_file(self) -> None:
        """Method to load drilling data .las file."""
        format_filter = "las files (*.las)"
        output: str = QFileDialog.getOpenFileName(self, caption="Select .las file", filter=format_filter)[0]
        # check if nothing was selected
        if output == "":
            return
        self.path_to_drilling_data: Path = Path(output)
        self.drilling_data: pd.DataFrame = load_las(self.path_to_drilling_data)
        self.update_selectbox_for_drilling()
        self.update_qlabel_for_selected_drilling()

    def prepare_well_logging_data_to_plot(self) -> None:
        """Method to prepare well logging data for visualization."""
        # check if the logging data is empty
        if self.logging_data.empty:
            return
        # check depth cols for logs and drilling
        depth_col_for_logs = [
            col for col in self.logging_data.columns if "depth" in col.lower() and "orig" not in col.lower()
        ]
        self.logging_data_to_plot = self.logging_data[self.logs_to_plot.get_selected_items() + depth_col_for_logs]

    def prepare_drilling_data_to_plot(self) -> None:
        """Method to prepare drilling data for visualization."""
        # check if the logging data is empty
        if self.drilling_data.empty:
            return
        # check depth cols for logs and drilling
        depth_col_for_drilling = [
            col for col in self.drilling_data.columns if "depth" in col.lower() and "orig" not in col.lower()
        ]
        self.drilling_data_to_plot = self.drilling_data[
            self.drilling_logs_to_plot.get_selected_items() + depth_col_for_drilling
        ]

    def plot_layout(self) -> None:
        """Method to plot the layout of the logging data."""
        # prepare fmi image for visualization
        self.prepare_fmi_image()
        self.prepare_fmi_segmentation_results()
        self.prepare_fmi_porosity()
        self.prepare_fmi_image_depth()
        self.prepare_well_logging_data_to_plot()
        self.prepare_drilling_data_to_plot()

        # Define the columns and create the Plotly figure
        self.plot_main = logview(
            df_log=self.logging_data_to_plot,
            fmi_image=self.fmi_image_cur,
            fmi_segmentation=self.fmi_segmentation_results,
            fmi_depth=self.fmi_image_depth_cur,
            fmi_porosity=self.fmi_porosity,
            df_formation=self.formation_tops_data,
            df_drilling=self.drilling_data_to_plot,
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
        # Clear previous content from the tab layout
        for i in reversed(range(self.logview_tab_layout.count())):
            widget_to_remove = self.logview_tab_layout.itemAt(i).widget()
            self.logview_tab_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()
        self.logview_tab_layout.addWidget(self.browser)

    def prepare_fmi_image(self) -> None:
        """Method to prepare FMI image for visualization."""
        # check if the layer exists
        if self.fmi_processor.current_layer is None:
            return
        fmi_image_cur = self.fmi_processor.current_layer.data.copy()
        fmi_image_cur = self.process_fmi_data(fmi_image_cur)
        self.fmi_image_cur = fmi_image_cur

    def prepare_fmi_image_depth(self) -> None:
        """Method to prepare FMI image depth for visualization."""
        # check if the layer exists
        if self.fmi_processor.current_file is None:
            return
        fmi_image_depth_cur = self.fmi_processor.current_file["DEPT"].copy()
        fmi_image_depth_cur = self.sample_rows(fmi_image_depth_cur)
        self.fmi_image_depth_cur = fmi_image_depth_cur

    def prepare_fmi_segmentation_results(self) -> None:
        """Method to prepare FMI segmentation results for visualization."""
        # check if the layer exists
        if self.fmi_processor.mask_layer is None:
            return
        fmi_segmentation_results = self.fmi_processor.mask_layer.data.copy()
        fmi_segmentation_results = self.process_fmi_data(fmi_segmentation_results * 255)
        self.fmi_segmentation_results = fmi_segmentation_results

    def prepare_fmi_porosity(self) -> None:
        """Method to prepare FMI porosity for visualization."""
        # check if the layer exists
        if self.fmi_processor.fmi_mask is None:
            return
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
        data = np.where(data < ENCODED_NONE, np.nan, data)
        # substitute nan / inf to 0
        data = np.nan_to_num(data, nan=0, posinf=0, neginf=0)
        # sample every Nth row
        data = self.sample_rows(data)
        # apply smoothing
        if single_dim:
            return gaussian_filter1d(data, sigma=SIGMA)
        return gaussian_filter(data, sigma=SIGMA)

    def update_selectbox_for_logs(self) -> None:
        """Method to add select box for logs."""
        if self.logging_data is None:
            return
        features_from_logs = [feat for feat in self.logging_data if "depth" not in feat.lower()]
        self.logs_to_plot.update_items(features_from_logs)

    def update_selectbox_for_drilling(self) -> None:
        """Method to add select box for drilling data."""
        if self.drilling_data is None:
            return
        features_from_drilling = [feat for feat in self.drilling_data if "depth" not in feat.lower()]
        self.drilling_logs_to_plot.update_items(features_from_drilling)

    def update_qlabel_for_selected_logs(self) -> None:
        """Method to update label for selected logs."""
        self.loadded_well_logging_file.setText(f"Well logging data file: {self.path_to_well_logging.name}")

    def update_qlabel_for_selected_formation_tops(self) -> None:
        """Method to update label for selected formation tops."""
        self.loadded_formation_tops_file.setText(f"Formation tops file: {self.path_to_formation_tops.name}")

    def update_qlabel_for_selected_drilling(self) -> None:
        """Method to update label for selected drilling data."""
        self.loadded_drilling_file.setText(f"Drilling data file: {self.path_to_drilling_data.name}")
