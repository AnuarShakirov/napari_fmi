"""Module to configure gui for logs window."""

from napari.viewer import Viewer
from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

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
        self.logview_tab = QWidget()
        self.cross_plot_tab = QWidget()

        # Add tabs to the QTabWidget
        self.right_tabs.addTab(self.logview_tab, "Layout")
        self.right_tabs.addTab(self.cross_plot_tab, "Cross-Plot")
        # connect click events explicitly
        self.right_tabs.currentChanged.connect(self.hide_selectboxes)

        # Set up each tab separately
        self.setup_logview_tab()
        self.setup_cross_plot_tab()

        # Add widgets to the main layout
        self.main_layout.addWidget(self.left_widget, 1)  # Left widget gets a stretch factor of 1
        self.main_layout.addWidget(self.right_tabs, 3)  # Tabs on the right get a stretch factor of 3

        # Set the central widget
        self.central_widget.setStyleSheet(f"background-color: {BACKGROUND_COLOR_LEFT_LAYOUT};")
        self.setCentralWidget(self.central_widget)

    def setup_left_layout(self) -> None:
        """Setup the left layout components."""
        # Title label
        self.label_load_folders = QLabel("Select files to upload")
        self.label_load_folders.setFont(self.get_font(size=12, bold=True))
        self.left_layout.addWidget(self.label_load_folders)
        self.add_spacer_left()

        # Buttons
        self.button_well_logging = QPushButton("Well logging data")
        self.button_well_logging.setFont(self.get_font(size=10))
        self.style_button(
            self.button_well_logging,
            bg_init_color=SELECT_FOLDER_BG_INIT_COLOR,
            bg_hover_color=SELECT_FOLDER_BG_HOVER_COLOR,
        )
        self.left_layout.addWidget(self.button_well_logging)
        self.add_spacer_left()

        self.button_formation_tops = QPushButton("Formation tops data")
        self.button_formation_tops.setFont(self.get_font(size=10))
        self.style_button(
            self.button_formation_tops,
            bg_init_color=SELECT_FOLDER_BG_INIT_COLOR,
            bg_hover_color=SELECT_FOLDER_BG_HOVER_COLOR,
        )
        self.left_layout.addWidget(self.button_formation_tops)
        self.add_spacer_left()

        self.button_drilling_data = QPushButton("Drilling data")
        self.button_drilling_data.setFont(self.get_font(size=10))
        self.style_button(
            self.button_drilling_data,
            bg_init_color=SELECT_FOLDER_BG_INIT_COLOR,
            bg_hover_color=SELECT_FOLDER_BG_HOVER_COLOR,
        )
        self.left_layout.addWidget(self.button_drilling_data)
        self.add_spacer_left()

        # place labels for the loaded files
        self.loadded_well_logging_file = QLabel("Well logging data file: ...")
        self.loadded_well_logging_file.setFont(self.get_font(size=10))
        self.loadded_formation_tops_file = QLabel("Formation tops file: ...")
        self.loadded_formation_tops_file.setFont(self.get_font(size=10))
        self.loadded_drilling_file = QLabel("Drilling data file: ...")
        self.loadded_drilling_file.setFont(self.get_font(size=10))
        self.left_layout.addWidget(self.loadded_well_logging_file)
        self.left_layout.addWidget(self.loadded_formation_tops_file)
        self.left_layout.addWidget(self.loadded_drilling_file)
        self.add_spacer_left()

        # Visualization button
        self.button_visualize_data = QPushButton("Visualize")
        self.button_visualize_data.setFont(self.get_font(size=10))
        self.style_button(
            self.button_visualize_data,
            bg_init_color=COLOR_BUTTON_VISUALIZE,
            bg_hover_color=COLOR_BUTTON_VISUALIZE_HOVER,
        )
        self.left_layout.addWidget(self.button_visualize_data)
        self.add_spacer_left()

        # place here fake multiselect combobox and then replace them
        self.label_select_logs = QLabel("Select logs to plot:")
        self.label_select_logs.setFont(self.get_font(size=10))
        self.left_layout.addWidget(self.label_select_logs)
        # add multiselect combobox
        self.logs_to_plot = MultiSelectComboBox(items=["None"], parent=None)
        self.left_layout.addWidget(self.label_select_logs)
        self.left_layout.addWidget(self.logs_to_plot)
        self.add_spacer_left()

        self.label_select_drilling = QLabel("Select drilling data to plot:")
        self.label_select_drilling.setFont(self.get_font(size=10))
        self.left_layout.addWidget(self.label_select_drilling)
        # add multiselect combobox
        self.drilling_logs_to_plot = MultiSelectComboBox(items=["None"], parent=None)
        self.left_layout.addWidget(self.drilling_logs_to_plot)
        self.add_spacer_left()

    def setup_logview_tab(self) -> None:
        """Setup the Layout tab content."""
        self.logview_tab_layout = QVBoxLayout()
        self.logview_tab.setLayout(self.logview_tab_layout)

    def setup_cross_plot_tab(self) -> None:
        """Setup the Cross-Plot tab content."""
        # Main vertical layout
        cross_plot_tab_layout = QVBoxLayout()
        cross_plot_tab_layout.setAlignment(Qt.AlignTop)

        # Upper part: Horizontal layout for left and right columns
        upper_part_layout = QHBoxLayout()
        upper_part_layout.setAlignment(Qt.AlignTop)
        # Wrap the upper part in a QWidget to apply stylesheet
        upper_part_widget = QWidget()
        upper_part_widget.setLayout(upper_part_layout)
        upper_part_widget.setStyleSheet(f"background-color: {BACKGROUND_COLOR_LEFT_LAYOUT};")

        # LEFT COLUMN
        left_column_layout = QVBoxLayout()
        self.label_x_axis = QLabel("X-axis")
        self.label_x_axis.setFont(self.get_font(size=14, bold=True))
        # Select curve widget
        self.label_select_curve_left = QLabel("Select curve:")
        self.label_select_curve_left.setFont(self.get_font(size=12))
        self.combo_box_select_curve_left = QComboBox()
        self.combo_box_select_curve_left.addItems(["None"])
        # Select scale widget
        self.label_select_scale_left = QLabel("Select scale:")
        self.label_select_scale_left.setFont(self.get_font(size=12))
        self.radio_normal_left = QRadioButton("linear")
        self.radio_normal_left.setChecked(True)
        self.radio_log_left = QRadioButton("log")
        self.scale_button_group_left = QButtonGroup()
        self.scale_button_group_left.addButton(self.radio_normal_left)
        self.scale_button_group_left.addButton(self.radio_log_left)
        # Add left column widgets
        left_column_layout.addWidget(self.label_x_axis)
        left_column_layout.addWidget(self.label_select_curve_left)
        left_column_layout.addWidget(self.combo_box_select_curve_left)
        left_column_layout.addWidget(self.label_select_scale_left)
        scale_button_layout_left = QHBoxLayout()
        scale_button_layout_left.addWidget(self.radio_normal_left)
        scale_button_layout_left.addWidget(self.radio_log_left)
        left_column_layout.addLayout(scale_button_layout_left)
        # Wrap left column in a QWidget
        left_column_widget = QWidget()
        left_column_widget.setLayout(left_column_layout)

        # RIGHT COLUMN
        right_column_layout = QVBoxLayout()
        self.label_y_axis = QLabel("Y-axis")
        self.label_y_axis.setFont(self.get_font(size=14, bold=True))
        # Select curve widget
        self.label_select_curve_right = QLabel("Select curve:")
        self.label_select_curve_right.setFont(self.get_font(size=12))
        self.combo_box_select_curve_right = QComboBox()
        self.combo_box_select_curve_right.addItems(["None"])
        # Select scale widget
        self.label_select_scale_right = QLabel("Select scale:")
        self.label_select_scale_right.setFont(self.get_font(size=12))
        self.radio_normal_right = QRadioButton("linear")
        self.radio_normal_right.setChecked(True)
        self.radio_log_right = QRadioButton("log")
        self.scale_button_group_right = QButtonGroup()
        self.scale_button_group_right.addButton(self.radio_normal_right)
        self.scale_button_group_right.addButton(self.radio_log_right)
        # Add right column widgets
        right_column_layout.addWidget(self.label_y_axis)
        right_column_layout.addWidget(self.label_select_curve_right)
        right_column_layout.addWidget(self.combo_box_select_curve_right)
        right_column_layout.addWidget(self.label_select_scale_right)
        # Scale buttons
        scale_button_layout_right = QHBoxLayout()
        scale_button_layout_right.addWidget(self.radio_normal_right)
        scale_button_layout_right.addWidget(self.radio_log_right)
        right_column_layout.addLayout(scale_button_layout_right)
        # Wrap right column in a QWidget
        right_column_widget = QWidget()
        right_column_widget.setLayout(right_column_layout)
        # Add left and right columns to the upper part layout
        upper_part_layout.addWidget(left_column_widget)
        upper_part_layout.addWidget(right_column_widget)
        # Add the upper part widget to the main vertical layout
        cross_plot_tab_layout.addWidget(upper_part_widget)

        # LOWER PART
        self.lower_part_layout = QVBoxLayout()
        self.lower_part_widget = QWidget()
        self.lower_part_widget.setLayout(self.lower_part_layout)
        cross_plot_tab_layout.addWidget(self.lower_part_widget)

        # Set the layout to the Cross-Plot tab
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

    def hide_selectboxes(self) -> None:
        """Method to hide select boxes in case cross-plot tab is selected."""
        # check if current tab is cross-plot
        current_tab = self.right_tabs.currentIndex()
        # index 0 for layout and 1 for cross-plot
        if current_tab == 1:
            self.label_select_logs.hide()
            self.logs_to_plot.hide()
            self.label_select_drilling.hide()
            self.drilling_logs_to_plot.hide()
        else:
            self.label_select_logs.show()
            self.logs_to_plot.show()
            self.label_select_drilling.show()
            self.drilling_logs_to_plot.show()
