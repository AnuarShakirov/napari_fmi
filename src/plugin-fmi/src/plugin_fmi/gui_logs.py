"""Module to configure gui for logs window."""

import os

import plotly.graph_objects as go
from napari.viewer import Viewer
from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from qtpy.QtWidgets import QSizePolicy, QSpacerItem
from .qt_widgets import MultiSelectComboBox

COLOR_FONT_TITLE: str = "#008170"
COLOR_FONT_GENERAL: str = "white"
BORDER_RADIUS_BUTTONS: str = "3px"
SELECT_FOLDER_BG_INIT_COLOR: str = "#008170"
SELECT_FOLDER_BG_HOVER_COLOR: str = "#005b41"
BACKGROUND_COLOR_LEFT_LAYOUT: str = "#262930"
BACKGROUND_COLOR_Right_LAYOUT: str = "#000000"
# colors for vizualize button
COLOR_BUTTON_VISUALIZE: str = "#4169E1"
COLOR_BUTTON_VISUALIZE_HOVER: str = "#16348C"


class LogsBase(QMainWindow):
    """Class represents GUI configuration for the FMI plugin."""

    def __init__(self, napari_viewer: Viewer) -> None:
        """Initialize."""
        super().__init__()
        self.viewer = napari_viewer
        self.init_gui()

    def init_gui(self) -> None:
        """Method to initialize the GUI frame."""
        # Set up the main window
        self.setWindowTitle("Log Layout")
        self.setGeometry(100, 100, 800, 600)  # Adjusted window size

        # Create the central widget and main layout
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout(self.central_widget)  # Two-column layout

        # Left column layout
        self.left_layout = QVBoxLayout()
        self.left_layout.setAlignment(Qt.AlignTop)
        self.setup_left_layout()

        # Left widget
        self.left_widget = QWidget()
        self.left_widget.setStyleSheet(f"background-color: {BACKGROUND_COLOR_LEFT_LAYOUT};")  # Example color
        self.left_widget.setLayout(self.left_layout)

        # Right side with tabs
        self.right_tabs = QTabWidget()
        self.right_tabs.setStyleSheet(f"background-color: {BACKGROUND_COLOR_Right_LAYOUT};")  # Example color for tabs

        # Create tab pages
        self.layout_tab = QWidget()
        self.cross_plot_tab = QWidget()

        # Add tabs to the QTabWidget
        self.right_tabs.addTab(self.layout_tab, "Layout")
        self.right_tabs.addTab(self.cross_plot_tab, "Cross-Plot")

        # Set up each tab separately
        self.setup_layout_tab()
        self.setup_cross_plot_tab()

        # Add widgets to the main layout
        self.main_layout.addWidget(self.left_widget, 1)  # Left widget gets a stretch factor of 1
        self.main_layout.addWidget(self.right_tabs, 3)  # Tabs on the right get a stretch factor of 3

        # Set the central widget
        self.central_widget.setStyleSheet(f"background-color: {BACKGROUND_COLOR_LEFT_LAYOUT};")
        self.setCentralWidget(self.central_widget)

    def setup_left_layout(self):
        """Setup the left layout components."""
        # Title label
        self.label_load_folders = QLabel("Select files to upload")
        self.label_load_folders.setFont(self.get_font(size=12, bold=True))
        self.left_layout.addWidget(self.label_load_folders)
        self.add_spacer_left()

        # Buttons
        self.button_well_logging = QPushButton("Well logging data")
        self.left_layout.addWidget(self.button_well_logging)
        self.add_spacer_left()

        self.button_formation_tops = QPushButton("Formation tops data")
        self.left_layout.addWidget(self.button_formation_tops)
        self.add_spacer_left()

        self.button_drilling_data = QPushButton("Drilling data")
        self.left_layout.addWidget(self.button_drilling_data)
        self.add_spacer_left()

        # Select box
        items = ["Option 1", "Option 2", "Option 3"]
        self.multiselect = MultiSelectComboBox(items)
        self.left_layout.addWidget(self.multiselect)

        # Visualization button
        self.button_visualize_data = QPushButton("Visualize data")
        self.left_layout.addWidget(self.button_visualize_data)
        self.add_spacer_left()

    def setup_layout_tab(self):
        """Setup the Layout tab content."""
        layout_tab_layout = QVBoxLayout()
        layout_tab_layout.addWidget(QLabel("Content for the Layout tab"))

        # Example button for Layout tab
        button_layout_tab = QPushButton("Additional Feature for Layout")
        layout_tab_layout.addWidget(button_layout_tab)

        self.layout_tab.setLayout(layout_tab_layout)

    def setup_cross_plot_tab(self):
        """Setup the Cross-Plot tab content."""
        cross_plot_tab_layout = QVBoxLayout()
        cross_plot_tab_layout.addWidget(QLabel("Content for the Cross-Plot tab"))

        # Example button for Cross-Plot tab
        button_cross_plot_tab = QPushButton("Additional Feature for Cross-Plot")
        cross_plot_tab_layout.addWidget(button_cross_plot_tab)

        self.cross_plot_tab.setLayout(cross_plot_tab_layout)

    @staticmethod
    def get_font(size: int, style: str = "Arial", bold: bool = False, italic: bool = False) -> QFont:
        """Method returns configuration for the font style and size."""
        font = QFont()
        font.setPointSize(size)
        font.setFamily(style)
        font.setBold(bold)
        font.setItalic(italic)
        return font

    @staticmethod
    def set_font_color(widget: QWidget, color: str = COLOR_FONT_TITLE) -> None:
        """Method to set the font color of a given widget."""
        widget.setStyleSheet(f"color: {color};")

    def add_spacer_left(self) -> None:
        """Method to add some space between widgets."""
        spacer = QSpacerItem(QSizePolicy.Preferred, QSizePolicy.Preferred, QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.left_layout.addSpacerItem(spacer)

    @staticmethod
    def style_button(
            button: QPushButton,
            bg_init_color: str,
            bg_hover_color: str,
            border_radius: str = BORDER_RADIUS_BUTTONS,
            text_color: str = COLOR_FONT_GENERAL,
    ) -> None:
        """Method to style button."""
        button.setStyleSheet(
            f"""
            QPushButton {{
                border-radius: {border_radius};
                background-color: {bg_init_color};
                color: {text_color};
            }}
            QPushButton:hover {{
                background-color: {bg_hover_color};
                color: {text_color};
            }}
        """,
        )

    @staticmethod
    def create_plotly_chart():
        fig = go.Figure(data=go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13], mode='lines+markers'))
        fig.update_layout(title="Sample Plotly Chart")
        # Save the figure as an HTML file
        file_path = os.path.abspath("plotly_chart.html")
        fig.write_html(file_path)
        return file_path



