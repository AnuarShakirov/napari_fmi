"""Define the FMIProcessorProtocol class."""

from typing import Protocol

from napari import Viewer


class FMIProcessorProtocol(Protocol):
    """Protocol class for the FMI plugin."""

    viewer: Viewer
    current_layer: any
    current_threshold: int
    img_scale: str

    def init_click_events(self) -> None:
        """Method to connect click events with actions."""

    def load_image_folder(self) -> None:
        """Method to load image folder."""

    def update_current_file(self) -> None:
        """Method to update the current file."""

    def plot_fmi_channel(self) -> None:
        """Method to plot the FMI channel."""

    def save_segmentation_results(self) -> None:
        """Method to save the segmentation results."""
