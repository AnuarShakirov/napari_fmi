"""Module to create widget for FMI images processing."""

from pathlib import Path
from typing import TYPE_CHECKING, Any

import cv2
import numpy as np
import pandas as pd
from napari.utils.notifications import show_info
from napari.viewer import Viewer
from qtpy.QtWidgets import (
    QFileDialog,
    QTableWidgetItem
)

from .gui_main import FMIProcessorBase
from .loaders import get_available_files, load_fmi_pickle
from .processing import get_boolean_mask, get_whashout_curve
from .gui_logs import LogLayout
if TYPE_CHECKING:
    from numpy.typing import NDArray

CHANNELS_TO_PARSE: list = ["DYN_HRUT", "DYN_HRLT", "STA_HRLT", "STA_HRUT"]
IMAGE_SCALE: int = 20
DEPTH_KEY: str = "DEPT"



class FMIProcessor(FMIProcessorBase):
    def __init__(self, napari_viewer: Viewer) -> None:
        super().__init__(napari_viewer)
        self.viewer = napari_viewer
        self.init_click_events()

        self.current_file: np.array | None = None  # current pickle file to upload
        self.current_channel: str = None  # current channel to process within pickle file

        self.current_layer = None  # viewer layer where images are plotted
        self.index_file = None  # current index for the main pickle file
        self.index_channel = None  # current index for the channel within pickle file
        self.current_threshold = 100  # initial threshold value
        self.curve_layer = None  # viewer layer to plot curve with content of washouts
        self.mask_layer = None  # viewer layer for mask
        self.fmi_mask: NDArray | None = None  # current fmi mask
        self.output_name: str | None = None  # name of the output file
        self.path_xlsx_files: str | None = None  # path to store xlsx files
        self.path_img_files: str | None = None  # path to store segmentation results
        self.img_scale: str = IMAGE_SCALE

    def init_click_events(self) -> None:
        """Method to connect click events with actions."""
        # button to select target folder with label on it
        self.button_load_image_folder.clicked.connect(self.load_image_folder)
        # button to select folder with results
        self.button_folder_to_save.clicked.connect(self.load_results_folder)
        # slider to change channel
        self.navigation_slider_channels.valueChanged.connect(self.update_channel_by_slider)
        # next and previous button
        self.next_file_button.clicked.connect(self.update_index_file_next)
        self.previous_file_button.clicked.connect(self.update_index_file_previous)
        # slider for threshold
        self.slider_threshold.valueChanged.connect(self.update_current_threshold)
        # slider for aspect ratio
        self.slider_aspect_ratio.valueChanged.connect(self.update_aspect_ratio)
        # save button
        self.button_save_results.clicked.connect(self.save_segmentation_results)
        # align with logging data button
        self.button_align_with_logs.clicked.connect(self.open_logs_layout)

    def load_image_folder(self) -> None:
        """Method to load folder with files."""
        output = QFileDialog.getExistingDirectory(self, "Select Folder", options=QFileDialog.ShowDirsOnly)
        if output == "":
            return
        self.folder_target = Path(output)
        self.fmi_image_list = get_available_files(self.folder_target)

        self.label_folder_image.setText(self.folder_target.name)
        self.n_files_found: int = len(self.fmi_image_list)
        if self.n_files_found:
            self.image_folder_stat_label.setText(str(self.n_files_found))
            self.update_table_with_images()
            self.index_file = 0
            self.index_channel = 0
            self.update_current_file()

    def load_results_folder(self) -> None:
        """Method to load path to folder where results will be saved."""
        output = QFileDialog.getExistingDirectory(self, "Select Folder", options=QFileDialog.ShowDirsOnly)
        if output == "":
            return
        # create path_to_results folder
        self.folder_results = Path(output)

        self.label_folder_results.setText(self.folder_results.name)
        self.button_save_results.setEnabled(True)
        self.init_folders_to_save_results()

    def update_table_with_images(self) -> None:
        """Method to extend the table with images."""
        # set number of rows
        self.tableWidget.setRowCount(self.n_files_found)
        # fill the table with images
        for ix, image in enumerate(self.fmi_image_list):
            self.tableWidget.setItem(ix, 0, QTableWidgetItem(image.name))

    def configure_slider_for_channels(self) -> None:
        """Method to configure slider with channels."""
        if len(self.relevant_channels):
            self.navigation_slider_channels.setMinimum(0)
            self.navigation_slider_channels.setMaximum(len(self.relevant_channels) - 1)
            self.navigation_slider_channels.setValue(0)

    def configure_slider_for_threshold(self) -> None:
        """Method to configure slider for threshold value."""
        if len(self.relevant_channels):
            self.slider_threshold.setMinimum(0)
            self.slider_threshold.setMaximum(np.max(self.current_file[self.current_channel]))
            self.slider_threshold.setValue(self.current_threshold)

    def update_file_info(self) -> None:
        """Method to update info about current file."""
        self.value_current_file.setText(self.fmi_image_list[self.index_file].name)

    def update_channel_info(self) -> None:
        """Method to update info about channels for file."""
        all_keys = self.current_file.keys()
        self.relevant_channels = [channel for channel in all_keys if channel.upper() in CHANNELS_TO_PARSE]
        if not len(self.relevant_channels):
            show_info("File does not have relevant channels!")
            self.clear_image_layer()
            self.clear_fmi_mask()
            self.clear_curve_layer()
            self.button_save_results.setEnabled(False)
            return

        self.current_channel = self.relevant_channels[self.index_channel]
        self.value_current_channel.setText(self.current_channel)
        self.plot_fmi_channel()

    def update_channel_by_slider(self, value: int) -> None:
        """Method to update slider for channels."""
        if not len(self.relevant_channels):
            return
        self.index_channel = value
        self.current_channel = self.relevant_channels[self.index_channel]
        self.value_current_channel.setText(self.current_channel)
        self.plot_fmi_channel()

    def update_index_file_previous(self) -> None:
        """Method to update current index for file to previous value."""
        # check if self.cur_index is not None
        if self.index_file is None:
            return
        # check if self.cur_index is not the first index
        if self.index_file > 0:
            self.index_file -= 1
            self.update_current_file()

    def update_index_file_next(self) -> None:
        """Method to update current index for file to previous value."""
        # check if self.cur_index is not None
        if self.index_file is None:
            return
        # check if self.cur_index is not the first index
        if self.index_file < self.n_files_found - 1:
            self.index_file += 1
            self.update_current_file()

    def update_current_file(self) -> None:
        """Method to update currently processing file."""
        self.current_file: dict[str, Any] = load_fmi_pickle(self.fmi_image_list[self.index_file])
        self.update_file_info()
        self.update_channel_info()
        self.configure_slider_for_channels()
        self.configure_slider_for_threshold()

    def update_current_threshold(self, value: int) -> None:
        """Method to update current threshold value for the whashout detection."""
        self.current_threshold = value
        self.plot_whashout_curve()

    def update_fmi_mask(self) -> None:
        """Method to plot whashout mask."""
        self.fmi_mask: NDArray = get_boolean_mask(
            fmi_image=self.current_file[self.current_channel],
            threshold=self.current_threshold,
        )

    def update_aspect_ratio(self, value: int) -> None:
        """Method to update aspect ratio of the main image."""
        self.img_scale = value
        self.plot_fmi_channel()

    def plot_fmi_channel(self) -> None:
        """Method to plot fmi channel in viewer."""
        if self.current_file is not None and self.current_channel is not None:
            self.clear_image_layer()
            self.current_layer = self.viewer.add_image(
                self.current_file[self.current_channel],
                name=f"{self.fmi_image_list[self.index_file].name}_{self.current_channel}",
                scale=(1, self.img_scale),
                colormap="bop blue",
                interpolation2d="linear",
            )
            self.plot_whashout_curve()

    def plot_whashout_curve(self) -> None:
        """Method to plot whashout curve."""
        self.clear_curve_layer()
        self.clear_fmi_mask()
        self.update_fmi_mask()
        self.whashout_curve = get_whashout_curve(fmi_boolean=self.fmi_mask)
        self.curve_layer = self.viewer.add_shapes(
            [self.whashout_curve],
            shape_type="path",
            edge_width=3,
            edge_color="white",
            scale=(1, self.img_scale),
            name="Caverns content, %",
            visible=False,
        )
        self.plot_fmi_mask()

    def plot_fmi_mask(self) -> None:
        """Method to plot fmi mask according to threshold value."""
        self.mask_layer = self.viewer.add_labels(
            self.fmi_mask * 255,
            scale=(1, self.img_scale),
            name="Segmentation results",
            opacity=0.6,
        )

    def clear_image_layer(self) -> None:
        """Method to clear images after visualization."""
        if self.current_layer is not None:
            self.viewer.layers.remove(self.current_layer)
            self.current_layer = None

    def clear_curve_layer(self) -> None:
        """Method to clear curve layer."""
        if self.curve_layer is not None:
            self.viewer.layers.remove(self.curve_layer)
            self.curve_layer = None

    def clear_fmi_mask(self) -> None:
        """Method to clear mask layer."""
        if self.mask_layer is not None:
            self.viewer.layers.remove(self.mask_layer)
            self.mask_layer = None

    def init_folders_to_save_results(self) -> None:
        """Method to init folders where we will store .xlsx file and images."""
        self.path_xlsx_files: Path = self.folder_results / "excel_files"
        self.path_img_files: Path = self.folder_results / "segmentation_results"
        self.path_xlsx_files.resolve().mkdir(exist_ok=True, parents=True)
        self.path_img_files.resolve().mkdir(exist_ok=True, parents=True)

    def save_segmentation_results(self) -> None:
        """Method to save segmentation results to .xlsx file."""

        df_results = pd.DataFrame(
            {
                "Depth": self.current_file[DEPTH_KEY],
                "Whashout": self.whashout_curve[:, 1] / self.fmi_mask.shape[1]  # normalize to width of the image
            }
        )
        file_name: str = self.fmi_image_list[self.index_file].name.split('.')[0]
        save_name: str = f"{file_name}_{self.current_threshold}.xlsx"
        path_to_export: Path = self.path_xlsx_files / save_name
        df_results.to_excel(path_to_export.resolve(), index=False)
        self.save_mask()
        show_info(f"Results for {file_name} were saved to .xlsx file!")

    def save_mask(self) -> None:
        """Method to save the mask"""
        file_name: str = self.fmi_image_list[self.index_file].name.split('.')[0]
        save_name: str = f"{file_name}_{self.current_threshold}.png"
        path_to_save: Path = self.path_img_files / save_name
        cv2.imwrite(str(path_to_save.resolve()), self.mask_layer.data)
        show_info(f"Results for {file_name} were saved to .xlsx and .png files!")

    def open_logs_layout(self) -> None:
        """Method to start new layout for logging data processing."""
        self.log_window = LogLayout(napari_viewer=self.viewer)
        self.log_window.show()
