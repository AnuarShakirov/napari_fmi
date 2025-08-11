"""Mmodule represent GUI configuration for the plugin used for creating the FMI
plugin.
"""

from napari.viewer import Viewer
from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)
from superqt import QCollapsible, QLabeledSlider

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import os
from pathlib import Path

# Set absolute path to bundled plugin
plugin_dir = Path(__file__).resolve().parent / "platforms"
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(plugin_dir)

COLOR_FONT_TITLE: str = "#008170"
COLOR_FONT_GENERAL: str = "white"
BORDER_RADIUS_BUTTONS: str = "5px"
SELECT_FOLDER_BG_INIT_COLOR: str = "#008170"
SELECT_FOLDER_BG_HOVER_COLOR: str = "#005b41"


class FMIProcessorBase(QWidget):
    """Class represents GUI configuration for the FMI plugin."""

    def __init__(self, napari_viewer: Viewer) -> None:
        """Init."""
        super().__init__()
        self.viewer = napari_viewer
        self.init_gui()

    def init_gui(self) -> None:  # noqa: PLR0915
        """Method to initialize the GUI frame."""
        # layout configuration
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setMinimumWidth(500)
        self.setMaximumWidth(700)

        # set title and its properties
        self.label = QLabel("FMI Processor")
        self.set_font_color(self.label)
        self.label.setFont(self.get_font(size=14, bold=True))
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label)
        self.label.setAlignment(Qt.AlignCenter)
        self.add_spacer()

        # button to select target folder with label on it
        self.label_button_load_folder = QLabel("Select target folder")
        self.label_button_load_folder.setFont(self.get_font(size=10, italic=True))
        self.button_load_image_folder = QPushButton("Select folder")
        self.button_load_image_folder.setFont(self.get_font(size=12))
        self.style_button(
            self.button_load_image_folder,
            bg_init_color=SELECT_FOLDER_BG_INIT_COLOR,
            bg_hover_color=SELECT_FOLDER_BG_HOVER_COLOR,
        )
        self.layout.addWidget(self.label_button_load_folder)
        self.layout.addWidget(self.button_load_image_folder)

        # button to select folder to save results
        self.label_button_save_results = QLabel("Select folder to save results")
        self.label_button_save_results.setFont(self.get_font(size=10, italic=True))
        self.button_folder_to_save = QPushButton("Select folder")
        self.button_folder_to_save.setFont(self.get_font(size=12))
        self.style_button(
            self.button_folder_to_save,
            bg_init_color=SELECT_FOLDER_BG_INIT_COLOR,
            bg_hover_color=SELECT_FOLDER_BG_HOVER_COLOR,
        )
        self.layout.addWidget(self.label_button_save_results)
        self.layout.addWidget(self.button_folder_to_save)
        self.add_spacer()

        # QForm to output information about folder content
        self.folder_form_widget = QWidget()
        self.folder_form_layout = QFormLayout()
        self.folder_form_layout.setContentsMargins(0, 3, 0, 3)
        self.folder_form_widget.setLayout(self.folder_form_layout)
        self.layout.addWidget(self.folder_form_widget)

        # labels for the form rows
        self.folder_with_images = QLabel("Folder with data:")
        self.folder_with_images.setFont(self.get_font(size=10))
        self.images_identified_row_label = QLabel("N images:")
        self.images_identified_row_label.setFont(self.get_font(size=10))
        self.folder_path_to_results = QLabel("Folder with results:")
        self.folder_path_to_results.setFont(self.get_font(size=10))

        # initial labels for the form
        self.label_folder_image = QLabel("...")
        self.label_folder_image.setFont(self.get_font(size=10))
        self.image_folder_stat_label = QLabel("...")
        self.image_folder_stat_label.setFont(self.get_font(size=10))
        self.label_folder_results = QLabel("...")
        self.label_folder_results.setFont(self.get_font(size=10))

        # add labels to form
        self.folder_form_layout.addRow(self.folder_with_images, self.label_folder_image)
        self.folder_form_layout.addRow(
            self.images_identified_row_label,
            self.image_folder_stat_label,
        )
        self.folder_form_layout.addRow(
            self.folder_path_to_results,
            self.label_folder_results,
        )

        # table for showing images within the folder
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderLabels(["FMI files"])
        self.tableWidget.setColumnWidth(0, 300)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setCornerButtonEnabled(False)
        # specify style of the table
        self.tableWidget.setStyleSheet(
            """
            QTableWidget {
                color: white;
                border: 1px solid #005B41;
            }
            # QTableWidget:hover {
            #     background-color: #005B41;
            #     color: white;
            # }
        """,
        )
        # specify size policy for table
        self.tableWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.list_of_images = QCollapsible("List of FMI files")
        self.list_of_images.addWidget(self.tableWidget)
        self.list_of_images.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.layout.addWidget(self.list_of_images)
        self.add_spacer()

        # label for current channel of FMI
        self.channel_form_widget = QWidget()
        self.channel_form_layout = QFormLayout()
        self.channel_form_layout.setContentsMargins(0, 3, 0, 3)
        self.channel_form_widget.setLayout(self.channel_form_layout)
        self.layout.addWidget(self.channel_form_widget)

        self.label_current_file = QLabel("Current FMI file:")
        self.label_current_file.setFont(self.get_font(size=10))
        self.value_current_file = QLabel("...")
        self.value_current_file.setFont(self.get_font(size=10, bold=True))
        self.label_current_channel = QLabel("FMI data type:")
        self.label_current_channel.setFont(self.get_font(size=10))
        self.value_current_channel = QLabel("...")
        self.value_current_channel.setFont(self.get_font(size=10, bold=True))
        self.channel_form_layout.addRow(self.label_current_file, self.value_current_file)
        self.channel_form_layout.addRow(self.label_current_channel, self.value_current_channel)

        # slider to select FMI channel
        self.navigation_slider_channels = QLabeledSlider()
        self.navigation_slider_channels.setOrientation(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.navigation_slider_channels)

        # buttons to navigate through fmi files
        navigation_layout = QHBoxLayout()
        self.previous_file_button = QPushButton("◀️ Previous FMI file")
        self.next_file_button = QPushButton("Next FMI file ▶️")
        self.previous_file_button.setFont(self.get_font(size=10, italic=True))
        self.next_file_button.setFont(self.get_font(size=10, italic=True))
        navigation_layout.addWidget(self.previous_file_button)
        navigation_layout.addWidget(self.next_file_button)
        self.layout.addLayout(navigation_layout)
        self.add_spacer()

        # slider to change mask threshold value
        navigation_layout_sliders = QHBoxLayout()
        self.mask_threshold_value = QLabel("Mask threshold value:")
        self.mask_threshold_value.setFont(self.get_font(size=10, italic=True))
        self.slider_threshold = QLabeledSlider()
        self.slider_threshold.setOrientation(Qt.Orientation.Horizontal)
        self.slider_threshold.setMinimum(1)
        self.slider_threshold.setMaximum(100)
        self.slider_threshold.setSingleStep(10)
        self.slider_threshold.setValue(50)
        navigation_layout_sliders.addWidget(self.mask_threshold_value)
        navigation_layout_sliders.addWidget(self.slider_threshold)
        self.layout.addLayout(navigation_layout_sliders)
        self.add_spacer()

        # slider to change aspect ratio
        layout_aspect_ratio = QHBoxLayout()
        self.aspect_ratio_label = QLabel("Aspect ratio:")
        self.aspect_ratio_label.setFont(self.get_font(size=10, italic=True))
        self.slider_aspect_ratio = QLabeledSlider()
        self.slider_aspect_ratio.setOrientation(Qt.Orientation.Horizontal)
        self.slider_aspect_ratio.setMinimum(1)
        self.slider_aspect_ratio.setMaximum(50)
        self.slider_aspect_ratio.setSingleStep(1)
        self.slider_aspect_ratio.setValue(20)
        layout_aspect_ratio.addWidget(self.aspect_ratio_label)
        layout_aspect_ratio.addWidget(self.slider_aspect_ratio)
        self.layout.addLayout(layout_aspect_ratio)
        self.add_spacer()

        # button to save results
        self.button_save_results = QPushButton("💾 Save result")
        self.button_save_results.setFont(self.get_font(size=10, italic=False))
        # style button
        self.button_save_results.setStyleSheet(
            """
                                                    QPushButton {
                                                    border-radius: 5px;
                                                    background-color: #176B87;
                                                    color: white;
                                                    }
                                                    QPushButton:hover {
                                                    background-color: #053B50;
                                                    color: white;
                                                    }
                                                    QPushButton:disabled {
                                                            background-color: #A9A9A9;
                                                            color: #FFFFFF;                                                   }

                                                    """,
        )

        # disable the button
        self.button_save_results.setEnabled(False)
        self.layout.addWidget(self.button_save_results)

        # button to init separate window with logging data
        self.button_align_with_logs = QPushButton("📈 Align with logging data")
        self.button_align_with_logs.setFont(self.get_font(size=10, italic=False))
        self.layout.addWidget(self.button_align_with_logs)
        self.setLayout(self.layout)

    @staticmethod
    def get_font(
        size: int,
        style: str = "Arial",
        bold: bool = False,
        italic: bool = False,
    ) -> QFont:
        """Methods returns configuration for the font style and size."""
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

    def add_spacer(self) -> None:
        """Method to add some space between widgets."""
        # add some space after the label
        spacer = QSpacerItem(QSizePolicy.Preferred, QSizePolicy.Preferred, QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.layout.addSpacerItem(spacer)

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
