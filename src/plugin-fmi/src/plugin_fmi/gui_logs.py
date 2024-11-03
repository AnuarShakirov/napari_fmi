from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QSpacerItem, QSizePolicy, QHBoxLayout, QLabel
from qtpy.QtGui import QFont
from napari.viewer import Viewer
from qtpy.QtCore import Qt

COLOR_FONT_TITLE: str = "#008170"
COLOR_FONT_GENERAL: str = "white"
BORDER_RADIUS_BUTTONS: str = "3px"
SELECT_FOLDER_BG_INIT_COLOR: str = "#008170"
SELECT_FOLDER_BG_HOVER_COLOR: str = "#005b41"
BACKGROUND_COLOR_LEFT_LAYOUT: str = "#262930"
BACKGROUND_COLOR_Right_LAYOUT: str = "#000000"
class LogLayout(QMainWindow):
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
        self.right_layout.setAlignment(Qt.AlignTop)

        # title to load data
        self.label_load_folders = QLabel("Select files to upload")
        self.label_load_folders.setFont(self.get_font(size=12, bold=True))
        self.set_font_color(self.label_load_folders)
        self.left_layout.addWidget(self.label_load_folders)
        self.add_spacer_left()

        self.button_well_logging = QPushButton("Well logging data")
        self.button_well_logging.setFont(self.get_font(size=11))
        self.style_button(
            self.button_well_logging,
            bg_init_color=SELECT_FOLDER_BG_INIT_COLOR,
            bg_hover_color=SELECT_FOLDER_BG_HOVER_COLOR,
        )
        self.left_layout.addWidget(self.button_well_logging)
        self.add_spacer_left()

        self.button_formation_tops = QPushButton("Formation tops data")
        self.button_formation_tops.setFont(self.get_font(size=11))
        self.style_button(
            self.button_formation_tops,
            bg_init_color=SELECT_FOLDER_BG_INIT_COLOR,
            bg_hover_color=SELECT_FOLDER_BG_HOVER_COLOR,
        )
        self.left_layout.addWidget(self.button_formation_tops)
        self.add_spacer_left()

        self.button_drilling_data = QPushButton("Drilling data")
        self.button_drilling_data.setFont(self.get_font(size=11))
        self.style_button(
            self.button_drilling_data,
            bg_init_color=SELECT_FOLDER_BG_INIT_COLOR,
            bg_hover_color=SELECT_FOLDER_BG_HOVER_COLOR,
        )
        self.left_layout.addWidget(self.button_drilling_data)
        self.add_spacer_left()

        self.left_widget = QWidget()
        self.left_widget.setStyleSheet(f"background-color: {BACKGROUND_COLOR_LEFT_LAYOUT}")
        self.left_widget.setLayout(self.left_layout)
        self.right_widget = QWidget()
        self.right_widget.setStyleSheet(f"background-color: {BACKGROUND_COLOR_Right_LAYOUT}")
        self.right_widget.setLayout(self.right_layout)
        # Add left and right widgets to the main layout with stretch factors
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
    def style_button(button: QPushButton, bg_init_color: str, bg_hover_color: str,
                     border_radius: str = BORDER_RADIUS_BUTTONS, text_color: str = COLOR_FONT_GENERAL) -> None:
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
        """
        )