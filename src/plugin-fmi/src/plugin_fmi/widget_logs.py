"""Module to visualize logging data and BHI."""

from pathlib import Path
from typing import TYPE_CHECKING
import os
import pandas as pd
from napari.viewer import Viewer
from qtpy.QtCore import QUrl
from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtWidgets import QFileDialog

from .gui_logs import LogsBase
from .loaders import load_las
from .visualization import logview

if TYPE_CHECKING:
    pass


class LogsProcessor(LogsBase):
    """Class to create widget for logging data manipulation."""

    def __init__(self, napari_viewer: Viewer) -> None:
        super().__init__(napari_viewer)
        self.viewer = napari_viewer
        self.init_click_events()

        self.logging_data: pd.DataFrame | None = None

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
        # Define the columns and create the Plotly figure
        cols_to_keep = [col for col in self.logging_data][:7]
        self.plot_main = logview(df_log=self.logging_data[cols_to_keep])

        # Generate the HTML with Plotly and insert custom CSS for a dark theme
        html_content = self.plot_main.to_html(include_plotlyjs="cdn")
        dark_css = """
        <style>
            body { background-color: black; color: white; }
            .plotly { color: white; }
        </style>
        """
        dark_html_content = html_content.replace("<head>", f"<head>{dark_css}")

        # Save the modified HTML content to a file
        file_path = os.path.abspath("plotly_chart_dark.html")
        with open(file_path, "w") as f:
            f.write(dark_html_content)

        # Load the dark-themed HTML into QWebEngineView
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl.fromLocalFile(file_path))
        self.right_layout.addWidget(self.browser)

