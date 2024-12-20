"""Module to implement QT widgets for the plugin."""

from qtpy.QtCore import QPoint, Qt
from qtpy.QtGui import QMouseEvent
from qtpy.QtWidgets import QLineEdit, QListWidget, QListWidgetItem, QWidget

from .constants import N_LOGS


class MultiSelectComboBox(QLineEdit):
    """Class to create a multi-select combo box."""

    def __init__(self, items: list[str], parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)  # Make QLineEdit read-only for display purposes
        self.items = items  # List of items to display
        self.selected_items = []  # List to store selected items

        # Set up the list widget as a dropdown popup
        self.list_widget = QListWidget(parent)  # Set the parent to main widget
        self.list_widget.setWindowFlags(Qt.ToolTip)  # Allows toggling visibility

        # Populate list widget with checkable items
        self.populate_items(items)

        # Initialize selected items based on pre-checked items
        self.update_selected_items()

        # Connect the itemChanged signal to update selected items when checked
        self.list_widget.itemChanged.connect(self.update_selected_items)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Method to handle mouse press event."""
        # Toggle visibility of list_widget when QLineEdit is clicked
        if self.list_widget.isVisible():
            self.list_widget.hide()  # Hide if already visible
        else:
            # Show list_widget as a popup just below the QLineEdit
            self.list_widget.move(self.mapToGlobal(QPoint(0, self.height())))
            self.list_widget.show()

    def update_selected_items(self) -> None:
        """Method to update selected items."""
        # Gather checked items and display them in QLineEdit
        self.selected_items = [
            self.list_widget.item(i).text()
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).checkState() == Qt.Checked
        ]
        self.setText(", ".join(self.selected_items))

    def get_selected_items(self) -> list[str]:
        """Method to retrieve selected items."""
        return self.selected_items

    def clear_items(self) -> None:
        """Clear all items in the list widget."""
        self.list_widget.clear()
        self.selected_items = []
        self.setText("")  # Clear the QLineEdit display
        self.items = []  # Reset the items list

    def update_items(self, new_items: list[str]) -> None:
        """Update the items in the list widget."""
        self.clear_items()  # Clear existing items
        self.populate_items(new_items)  # Populate with new items
        self.items = new_items  # Update the internal items list
        self.update_selected_items()  # Refresh the selected items display

    def populate_items(self, items: list[str]) -> None:
        """Helper method to populate the list widget with items."""
        for index, item_text in enumerate(items):
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Make item checkable
            # Check the first three items by default
            if index < N_LOGS:  # Adjust this number to change how many are pre-checked
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)
