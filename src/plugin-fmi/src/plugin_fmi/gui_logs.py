from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QSpacerItem, QSizePolicy
from qtpy.QtGui import QFont
from napari.viewer import Viewer

# Example styles
BORDER_RADIUS_BUTTONS = "5px"
COLOR_FONT_GENERAL = "#000000"
COLOR_FONT_TITLE = "#333333"


class LogLayout(QMainWindow):
    """Class represents GUI configuration for the FMI plugin."""

    def __init__(self, napari_viewer: Viewer) -> None:
        """Init."""
        super().__init__()
        self.viewer = napari_viewer
        self.init_gui()

    def init_gui(self) -> None:  # noqa: PLR0915
        """Method to initialize the GUI frame."""
        # Set up the main window
        self.setWindowTitle("Log Layout")
        self.setGeometry(100, 100, 400, 300)  # Example window size and position

        # Layout configuration
        central_widget = QWidget()
        self.layout = QVBoxLayout(central_widget)

        # Add a button for demonstration
        button = QPushButton("New Button in Layout")
        self.layout.addWidget(button)

        # Add spacer
        self.add_spacer()

        self.setCentralWidget(central_widget)

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

    def add_spacer(self) -> None:
        """Method to add some space between widgets."""
        spacer = QSpacerItem(QSizePolicy.Preferred, QSizePolicy.Preferred, QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.layout.addSpacerItem(spacer)

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