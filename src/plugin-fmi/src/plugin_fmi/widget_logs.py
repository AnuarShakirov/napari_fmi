"""Module to visualize logging data and BHI."""

import os
import warnings
from contextlib import suppress
from functools import reduce
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
from .visualization import cross_plot, logview


warnings.filterwarnings("ignore")


class LogsProcessor(LogsBase):
    """Class to create widget for logging data manipulation."""

    def __init__(self, fmi_processor: FMIProcessorProtocol) -> None:
        super().__init__(fmi_processor.viewer)
        self.fmi_processor = fmi_processor
        self.init_click_events()

        self.fmi_image_cur: NDArray | None = None
        self.fmi_segmentation_results: NDArray | None = None
        self.fmi_image_depth_cur: NDArray | None = None
        self.fmi_porosity: NDArray | None = None

        self.formation_tops_data: pd.DataFrame = pd.DataFrame()
        self.drilling_data: pd.DataFrame = pd.DataFrame()
        self.logging_data: pd.DataFrame = pd.DataFrame()

        self.drilling_data_to_plot: pd.DataFrame = pd.DataFrame()
        self.logging_data_to_plot: pd.DataFrame = pd.DataFrame()
        self.formation_tops_cross_plot: pd.DataFrame = pd.DataFrame()
        self.fmi_data_to_plot: pd.DataFrame = pd.DataFrame()

        # dict to map curve names to dataframe
        self.curve_mapping = {}

        # prepare fmi image for visualization
        self.prepare_fmi_image()
        self.prepare_fmi_segmentation_results()
        self.prepare_fmi_image_depth()
        self.prepare_fmi_porosity()
        self.map_curve_to_dataframe()

        # dataframe to store the data for cross plot
        self.cross_plot_data = pd.DataFrame()

    def init_click_events(self) -> None:
        """Method to connect click events with actions."""
        self.button_well_logging.clicked.connect(self.load_well_logging_file)
        self.button_formation_tops.clicked.connect(self.load_formation_tops_file)
        self.button_drilling_data.clicked.connect(self.load_drilling_data_file)
        self.update_visualize_button_behavior()

    def init_gui(self) -> None:
        """Method to initialize the GUI and connfigure visualize button behavior."""
        super().init_gui()
        # Connect tab change signal to update button behavior
        self.right_tabs.currentChanged.connect(self.update_visualize_button_behavior)
        # Initial setup for the current tab
        self.update_visualize_button_behavior()

    def update_visualize_button_behavior(self) -> None:
        """Update the button behavior based on the current tab index."""
        # Disconnect any previous connections
        with suppress(TypeError):
            self.button_visualize_data.clicked.disconnect()
        # Get the current tab index
        current_tab = self.right_tabs.currentIndex()
        # Connect the appropriate function based on the current tab
        if current_tab == 0:
            self.button_visualize_data.clicked.connect(self.plot_layout)
        elif current_tab == 1:
            self.button_visualize_data.clicked.connect(self.plot_cross_plot)

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
        self.map_curve_to_dataframe()
        self.merge_dataframes_for_crossplot()

    def load_formation_tops_file(self) -> None:
        """Method to load formation tops .xlsx file."""
        format_filter = "xlsx files (*.xlsx)"
        output: str = QFileDialog.getOpenFileName(self, caption="Select .xlsx file", filter=format_filter)[0]
        # check if nothing was selected
        if output == "":
            return
        self.path_to_formation_tops: Path = Path(output)
        self.formation_tops_data, msg = load_formation_tops(self.path_to_formation_tops)
        if msg != "":
            show_info(msg)
            return

        self.formation_tops_data_processed = pivot_data_for_visualization(self.formation_tops_data)
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
        self.map_curve_to_dataframe()
        self.merge_dataframes_for_crossplot()

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
        self.prepare_well_logging_data_to_plot()
        self.prepare_drilling_data_to_plot()

        # Define the columns and create the Plotly figure
        self.plot_main = logview(
            df_log=self.logging_data_to_plot,
            fmi_image=self.fmi_image_cur,
            fmi_segmentation=self.fmi_segmentation_results,
            fmi_depth=self.fmi_image_depth_cur,
            fmi_porosity=self.fmi_porosity,
            df_formation=self.formation_tops_data_processed,
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

    def plot_cross_plot(self) -> None:
        """Method to plot cross-plot."""
        self.prepare_well_logging_data_to_plot()
        self.prepare_drilling_data_to_plot()
        self.merge_dataframes_for_crossplot()
        x_scale = self.scale_button_group_left.checkedButton().text()
        y_scale = self.scale_button_group_right.checkedButton().text()
        x_feature = self.combo_box_select_curve_left.currentText()
        y_feature = self.combo_box_select_curve_right.currentText()
        interpolate = self.curve_mapping[x_feature] != self.curve_mapping[y_feature]
        self.cross_plot = cross_plot(
            df_cur=self.cross_plot_data,
            x_col=x_feature,
            y_col=y_feature,
            x_scale=x_scale,
            y_scale=y_scale,
            interpolate=interpolate,
        )

        # Generate the HTML with Plotly
        html_content_cross_plot = self.cross_plot.to_html(include_plotlyjs="cdn")

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
        html_content_cross_plot = css + html_content_cross_plot

        # Save the HTML content to a file
        file_path = os.path.abspath("plotly_cross_plot.html")
        with open(file_path, "w") as f:
            f.write(html_content_cross_plot)

        # Load the HTML into QWebEngineView
        self.browser_cross_plot = QWebEngineView()
        self.browser_cross_plot.setUrl(QUrl.fromLocalFile(file_path))

        # Clear previous content from the tab layout
        for i in reversed(range(self.lower_part_layout.count())):
            widget_to_remove = self.lower_part_layout.itemAt(i).widget()
            self.lower_part_layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()
        self.lower_part_layout.addWidget(self.browser_cross_plot)

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
        # prepare dataframe sampled
        depth_col = self.sample_rows(self.fmi_image_depth_cur)
        fmi_porosity = self.sample_rows(fmi_porosity)
        self.fmi_data_to_plot = pd.DataFrame({"DEPTH": depth_col, "PHIT_FMI": fmi_porosity})


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

    def map_curve_to_dataframe(self) -> None:
        """Method to map curve names to dataframe."""
        curve_mapping_original = {
            "WELL_LOGGING": list(self.logging_data.columns) if not self.logging_data.empty else [],
            "DRILLING": list(self.drilling_data.columns) if not self.drilling_data.empty else [],
            "PHIT_FMI": list(self.fmi_data_to_plot.columns) if not self.fmi_data_to_plot.empty else [],
        }
        self.curve_mapping = {
            value: key
            for key, values in curve_mapping_original.items()
            if values  # Exclude empty lists
            for value in values
        }
        # assign keys of the dict to the select curve widget
        self.combo_box_select_curve_left.clear()
        self.combo_box_select_curve_right.clear()
        self.combo_box_select_curve_left.addItems(list(self.curve_mapping.keys()))
        self.combo_box_select_curve_right.addItems(list(self.curve_mapping.keys()))

    def merge_dataframes_for_crossplot(self) -> None:
        """Method to merge dataframes for cross plot."""
        # check if the dataframes are empty
        df_fmi = pd.DataFrame()
        if self.fmi_porosity is not None:
            df_fmi = pd.DataFrame({"DEPTH": self.fmi_image_depth_cur, "PHIT_FMI": self.fmi_porosity})
        # get depth column for the dataframes
        depth_col_logging = [
            col for col in self.logging_data.columns if "depth" in col.lower() and "orig" not in col.lower()
        ]
        depth_col_drilling = [
            col for col in self.drilling_data.columns if "depth" in col.lower() and "orig" not in col.lower()
        ]
        # prepare formation tops data
        self.prepare_formation_tops_data_for_crops_plot()
        # renamge the depth column
        if len(depth_col_logging):
            self.logging_data.rename(columns={depth_col_logging[0]: "DEPTH"}, inplace=True)
        if len(depth_col_drilling):
            self.drilling_data.rename(columns={depth_col_drilling[0]: "DEPTH"}, inplace=True)
        # check which dataframes are empty
        list_df_to_merge = [
            df_cur
            for df_cur in [df_fmi, self.logging_data, self.drilling_data, self.formation_tops_cross_plot]
            if not df_cur.empty
        ]
        # merge the dataframes on DEPTH
        self.cross_plot_data = reduce(
            lambda left, right: pd.merge(left, right, on="DEPTH", how="outer"),
            list_df_to_merge,
        ).sort_values("DEPTH")

    def prepare_formation_tops_data_for_crops_plot(self) -> None:
        """Method to prepare formation tops data for cross plot."""
        # check if the formation tops data is empty
        if self.formation_tops_data.empty:
            return
        # prepare formation tops data
        formation_tops = self.formation_tops_data_processed.copy()
        formation_columns = [col for col in formation_tops.columns if "DEPTH" not in col]
        formation_tops["FORMATION"] = self.formation_tops_data_processed[formation_columns].idxmax(axis=1)
        self.formation_tops_cross_plot = formation_tops[["DEPTH", "FORMATION"]]
