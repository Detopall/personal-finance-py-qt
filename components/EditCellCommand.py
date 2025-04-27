from PySide6.QtWidgets import QMainWindow, QTableWidgetItem, QTableWidget
from PySide6.QtGui import QUndoStack, QUndoCommand


class EditCellCommand(QUndoCommand):
    """
    Command for undoing and redoing edits made to a table cell.
    """

    def __init__(
        self,
        table_widget: QTableWidget,
        row: int,
        col: int,
        old_value: str,
        new_value: str,
        main_window: QMainWindow,
        description: str = "Edit Cell"
    ) -> None:
        """
        Initialize the EditCellCommand.

        Args:
            table_widget (QTableWidget): The table widget where the edit occurred.
            row (int): Row of the edited cell.
            col (int): Column of the edited cell.
            old_value (str): The previous value of the cell.
            new_value (str): The new value set in the cell.
            main_window (QMainWindow): The main window instance, needed to temporarily ignore item change signals.
            description (str, optional): Description of the command for the undo stack. Defaults to "Edit Cell".
        """
        super().__init__(description)
        self.table_widget = table_widget
        self.row = row
        self.col = col
        self.old_value = old_value
        self.new_value = new_value
        self.main_window = main_window

    def undo(self) -> None:
        """
        Undo the last edit by restoring the old cell value.
        """
        self.main_window._ignore_change = True
        self.table_widget.setItem(self.row, self.col, QTableWidgetItem(self.old_value))
        self.main_window._ignore_change = False

    def redo(self) -> None:
        """
        Redo the edit by setting the new cell value again.
        """
        self.main_window._ignore_change = True
        self.table_widget.setItem(self.row, self.col, QTableWidgetItem(self.new_value))
        self.main_window._ignore_change = False
