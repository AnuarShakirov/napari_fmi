"""Module to configure gui for logs window."""

import os

import plotly.graph_objects as go
from napari.viewer import Viewer
from qtpy.QtCore import Qt, QPoint
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QMainWindow, QPushButton, QSizePolicy, QSpacerItem
from qtpy.QtWidgets import QWidget, QVBoxLayout

from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QDialog
from qtpy.QtCore import Qt, QRect
import sys

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
        self.main_layout = QHBoxLayout(self.central_widget)  # Use QHBoxLayout for two-column layout

        # Left and right columns layout
        self.left_layout = QVBoxLayout()
        self.left_layout.setAlignment(Qt.AlignTop)
        self.right_layout = QVBoxLayout()
        # self.right_layout.setAlignment(Qt.Align)

        # title to load data
        self.label_load_folders = QLabel("Select files to upload")
        self.label_load_folders.setFont(self.get_font(size=12, bold=True))
        self.set_font_color(self.label_load_folders)
        self.left_layout.addWidget(self.label_load_folders)
        self.add_spacer_left()
        
        # Button to load well logging data
        self.button_well_logging = QPushButton("Well logging data")
        self.button_well_logging.setFont(self.get_font(size=11))
        self.style_button(
            self.button_well_logging,
            bg_init_color=SELECT_FOLDER_BG_INIT_COLOR,
            bg_hover_color=SELECT_FOLDER_BG_HOVER_COLOR,
        )
        self.left_layout.addWidget(self.button_well_logging)
        self.add_spacer_left()
        
        
        # Show the selected file with well logs
        self.well_log_file_form_widget = QWidget()
        self.well_log_file_form_layout = QFormLayout()
        self.well_log_file_form_layout.setContentsMargins(0, 3, 0, 3)
        self.well_log_file_form_widget.setLayout(self.well_log_file_form_layout)
        self.left_layout.addWidget(self.well_log_file_form_widget)

        self.label_current_well_log_file = QLabel("Well logging file:")
        self.label_current_well_log_file.setFont(self.get_font(size=10))
        self.set_font_color(self.label_current_well_log_file, COLOR_FONT_GENERAL)  # Set font color to white

        self.value_current_well_log_file = QLabel("...")
        self.value_current_well_log_file.setFont(self.get_font(size=10, bold=True))
        self.set_font_color(self.value_current_well_log_file, COLOR_FONT_GENERAL)  # Set font color to white

        self.well_log_file_form_layout.addRow(self.label_current_well_log_file, self.value_current_well_log_file)


        # Button to load formation tops data
        self.button_formation_tops = QPushButton("Formation tops data")
        self.button_formation_tops.setFont(self.get_font(size=11))
        self.style_button(
            self.button_formation_tops,
            bg_init_color=SELECT_FOLDER_BG_INIT_COLOR,
            bg_hover_color=SELECT_FOLDER_BG_HOVER_COLOR,
        )
        self.left_layout.addWidget(self.button_formation_tops)
        self.add_spacer_left()

        # Show the selected file with formation tops
        self.formations_form_widget = QWidget()
        self.formations_form_layout = QFormLayout()
        self.formations_form_layout.setContentsMargins(0, 3, 0, 3)
        self.formations_form_widget.setLayout(self.formations_form_layout)
        self.left_layout.addWidget(self.formations_form_widget)

        self.label_current_formations_file = QLabel("Formations file:")
        self.label_current_formations_file.setFont(self.get_font(size=10))
        self.set_font_color(self.label_current_formations_file, COLOR_FONT_GENERAL)  # Set font color to white

        self.value_current_formations_file = QLabel("...")
        self.value_current_formations_file.setFont(self.get_font(size=10, bold=True))
        self.set_font_color(self.value_current_formations_file, COLOR_FONT_GENERAL)  # Set font color to white

        self.formations_form_layout.addRow(self.label_current_formations_file, self.value_current_formations_file)

        # Button to load drilling data
        self.button_drilling_data = QPushButton("Drilling data")
        self.button_drilling_data.setFont(self.get_font(size=11))
        self.style_button(
            self.button_drilling_data,
            bg_init_color=SELECT_FOLDER_BG_INIT_COLOR,
            bg_hover_color=SELECT_FOLDER_BG_HOVER_COLOR,
        )
        self.left_layout.addWidget(self.button_drilling_data)
        self.add_spacer_left()
        
        
        # Show the selected file with drilling data
        self.drill_data_form_widget = QWidget()
        self.drill_data_form_layout = QFormLayout()
        self.drill_data_form_layout.setContentsMargins(0, 3, 0, 3)
        self.drill_data_form_widget.setLayout(self.drill_data_form_layout)
        self.left_layout.addWidget(self.drill_data_form_widget)

        self.label_current_drill_data_file = QLabel("Drilling data file:")
        self.label_current_drill_data_file.setFont(self.get_font(size=10))
        self.set_font_color(self.label_current_drill_data_file, COLOR_FONT_GENERAL)  # Set font color to white

        self.value_current_drill_data_file = QLabel("...")
        self.value_current_drill_data_file.setFont(self.get_font(size=10, bold=True))
        self.set_font_color(self.value_current_drill_data_file, COLOR_FONT_GENERAL)  # Set font color to white

        self.drill_data_form_layout.addRow(self.label_current_drill_data_file, self.value_current_drill_data_file)
        

        # test selectbox
        items = ["Option 1", "Option 2", "Option 3"]
        self.multiselect = MultiSelectComboBox(items)
        self.left_layout.addWidget(self.multiselect)

        # Button to run visualizations
        self.button_visualize_data = QPushButton("Visualize data")
        self.button_visualize_data.setFont(self.get_font(size=11))
        self.style_button(
            self.button_visualize_data,
            bg_init_color=COLOR_BUTTON_VISUALIZE,
            bg_hover_color=COLOR_BUTTON_VISUALIZE_HOVER,
        )
        self.left_layout.addWidget(self.button_visualize_data)
        self.add_spacer_left()
        
        # test selectbox for cross-plot
        items_logs = ["Log 1", "Log 2", "Log 3"]
        self.multiselect = MultiSelectComboBox(items_logs)
        self.left_layout.addWidget(self.multiselect)
        
        # button to run cross-plot visualizations
        self.button_visualize_crossplot = QPushButton("Make Cross-plot")
        self.button_visualize_crossplot.setFont(self.get_font(size=11))
        self.style_button(
            self.button_visualize_crossplot,
            bg_init_color=COLOR_BUTTON_VISUALIZE,
            bg_hover_color=COLOR_BUTTON_VISUALIZE_HOVER,
        )
        self.left_layout.addWidget(self.button_visualize_crossplot)
        self.add_spacer_left()

        # configure style for layouts
        self.left_widget = QWidget()
        self.left_widget.setStyleSheet(f"background-color: {BACKGROUND_COLOR_LEFT_LAYOUT}")
        self.left_widget.setLayout(self.left_layout)
        self.right_widget = QWidget()
        self.right_widget.setStyleSheet(f"background-color: {BACKGROUND_COLOR_Right_LAYOUT}")
        self.right_widget.setLayout(self.right_layout)
        self.main_layout.addWidget(self.left_widget, 1)  # Left widget gets a stretch factor of 1
        self.main_layout.addWidget(self.right_widget, 3)  # Right widget gets a stretch factor of 3

        # Set the central widget
        self.central_widget.setStyleSheet(f"background-color: {BACKGROUND_COLOR_LEFT_LAYOUT}")
        self.setCentralWidget(self.central_widget)

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


class MultiSelectComboBox(QLineEdit):
    def init(self, items, parent=None):
        super().init(parent)
        self.setReadOnly(True)  # Make QLineEdit read-only for display purposes
        self.items = items
        self.selected_items = []

        # Set up the list widget as a dropdown popup
        self.list_widget = QListWidget()
        self.list_widget.setWindowFlags(Qt.Popup)
        self.list_widget.setFocusPolicy(Qt.NoFocus)

        # Populate list widget with checkable items
        for item_text in items:
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Make item checkable
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)

        # Connect the itemChanged signal to update selected items when checked
        self.list_widget.itemChanged.connect(self.update_selected_items)

        # Connect focus out event to close the popup
        self.list_widget.installEventFilter(self)

    def mousePressEvent(self, event):
        # Show list_widget as a popup just below the QLineEdit
        self.list_widget.move(self.mapToGlobal(QPoint(0, self.height())))
        self.list_widget.show()
        self.list_widget.setFocus()

    def update_selected_items(self):
        # Gather checked items and display them in QLineEdit
        self.selected_items = [
            self.list_widget.item(i).text()
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == Qt.Checked
        ]
        self.setText(", ".join(self.selected_items))

    def eventFilter(self, source, event):
        if source == self.list_widget and event.type() == event.FocusOut:
            self.list_widget.hide()
        return super().eventFilter(source, event)

    def get_selected_items(self):
        # Method to retrieve selected items
        return self.selected_items


class MultiSelectComboBox(QLineEdit):
    def init(self, items, parent=None):
        super().init(parent)
        self.setReadOnly(True)  # Make QLineEdit read-only for display purposes
        self.items = items
        self.selected_items = []

        # Set up the list widget as a dropdown popup
        self.list_widget = QListWidget()
        self.list_widget.setWindowFlags(Qt.Popup)
        self.list_widget.setFocusPolicy(Qt.NoFocus)

        # Populate list widget with checkable items
        for item_text in items:
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Make item checkable
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)

        # Connect the itemChanged signal to update selected items when checked
        self.list_widget.itemChanged.connect(self.update_selected_items)

        # Connect focus out event to close the popup
        self.list_widget.installEventFilter(self)

    def mousePressEvent(self, event):
        # Show list_widget as a popup just below the QLineEdit
        self.list_widget.move(self.mapToGlobal(QPoint(0, self.height())))
        self.list_widget.show()
        self.list_widget.setFocus()

    def update_selected_items(self):
        # Gather checked items and display them in QLineEdit
        self.selected_items = [
            self.list_widget.item(i).text()
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == Qt.Checked
        ]
        self.setText(", ".join(self.selected_items))

    def eventFilter(self, source, event):
        if source == self.list_widget and event.type() == event.FocusOut:
            self.list_widget.hide()
        return super().eventFilter(source, event)

    def get_selected_items(self):
        # Method to retrieve selected items
        return self.selected_items


class MultiSelectComboBox(QLineEdit):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)  # Make QLineEdit read-only for display purposes
        self.items = items
        self.selected_items = []

        # Set up the list widget as a dropdown popup
        self.list_widget = QListWidget(parent)  # Set the parent to main widget
        self.list_widget.setWindowFlags(Qt.ToolTip)  # Allows toggling visibility

        # Populate list widget with checkable items
        for item_text in items:
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Make item checkable
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)

        # Connect the itemChanged signal to update selected items when checked
        self.list_widget.itemChanged.connect(self.update_selected_items)

    def mousePressEvent(self, event):
        # Toggle visibility of list_widget when QLineEdit is clicked
        if self.list_widget.isVisible():
            self.list_widget.hide()  # Hide if already visible
        else:
            # Show list_widget as a popup just below the QLineEdit
            self.list_widget.move(self.mapToGlobal(QPoint(0, self.height())))
            self.list_widget.show()

    def update_selected_items(self):
        # Gather checked items and display them in QLineEdit
        self.selected_items = [
            self.list_widget.item(i).text()
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == Qt.Checked
        ]
        self.setText(", ".join(self.selected_items))

    def get_selected_items(self):
        # Method to retrieve selected items
        return self.selected_items


