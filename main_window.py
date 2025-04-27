from PySide6.QtWidgets import QMainWindow, QMessageBox, QTableWidget
from PySide6.QtGui import QUndoStack
import pandas as pd
from pandas import DataFrame
from typing import Optional, Tuple

from ui_personal_finance import Ui_MainWindow
from components.CsvReader import CsvReader
from components.EditCellCommand import EditCellCommand
from components.Message import Message
from components.Charts import Charts
from components.PdfExporter import PdfExporter


class MainWindow(QMainWindow):
	"""Main window of the Personal Finance App."""

	def __init__(self) -> None:
		"""Initialize the main window, UI components, and connect signals."""
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self._show_status("Ready")

		self.csv_reader = CsvReader(self.ui)
		self.undo_stack = QUndoStack(self)
		self._ignore_change: bool = False
		self._last_cell: Optional[Tuple[int, int]] = None
		self._last_value: Optional[str] = None

		# Connect UI actions to corresponding methods
		self._connect_signals()
		self.show()

	def _connect_signals(self) -> None:
		"""Connect UI actions to their respective slots."""
		self.ui.actionImport_CSV.triggered.connect(self.import_csv)
		self.ui.actionSave_file.triggered.connect(self.save_file)
		self.ui.actionSave_to_PDF.triggered.connect(self.save_to_pdf)
		self.ui.actionExit.triggered.connect(self.exit)
		self.ui.actionAbout.triggered.connect(self.about)
		self.ui.actionUser_Guide.triggered.connect(self.user_guide)
		self.ui.actionCharts.triggered.connect(self.charts)
		self.ui.actionImportCsv.triggered.connect(self.import_csv)
		self.ui.actionUndo.triggered.connect(self.undo)
		self.ui.actionRedo.triggered.connect(self.redo)
		self.ui.actionSave.triggered.connect(self.save)
		self.ui.actionExportToPdf.triggered.connect(self.export_to_pdf)

		self.ui.tableWidget.cellClicked.connect(self._on_cell_clicked)
		self.ui.tableWidget.itemChanged.connect(self._on_item_changed)

	def _show_status(self, message: str, time: int = 0) -> None:
		"""Display a status message on the status bar."""
		self.statusBar().showMessage(message, time)

	def _on_cell_clicked(self, row: int, col: int) -> None:
		"""Capture the last clicked cell and its value."""
		item = self.ui.tableWidget.item(row, col)
		self._last_cell = (row, col)
		self._last_value = item.text() if item else ""

	def _on_item_changed(self, item) -> None:
		"""Handle item changes in the table and support undo/redo operations."""
		if self._ignore_change:
			return

		row, col = item.row(), item.column()
		new_value = item.text()
		old_value = self._last_value if self._last_cell == (row, col) else ""

		command = EditCellCommand(self.ui.tableWidget, row, col, old_value, new_value, self)
		self.undo_stack.push(command)

	def _table_to_dataframe(self, tableWidget: QTableWidget) -> Optional[DataFrame]:
		"""Convert the tableWidget data to a pandas DataFrame."""
		rows = tableWidget.rowCount()
		cols = tableWidget.columnCount()

		if rows == 0:
			return None

		headers = [tableWidget.horizontalHeaderItem(i).text() for i in range(cols)]
		data = [
			[tableWidget.item(row, col).text() if tableWidget.item(row, col) else "" for col in range(cols)]
			for row in range(rows)
		]

		try:
			df = pd.DataFrame(data, columns=headers)
			df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
			df = df.dropna(subset=['Amount', 'Date', 'Type'])

			if df.empty:
				return None

			return df

		except Exception as e:
			print("Error parsing table:", e)
			return None

	def import_csv(self) -> None:
		"""Import data from a CSV file."""
		self.csv_reader.read()
		self._show_status("CSV Imported", 2000)

	def save_file(self) -> None:
		"""Save the current table data as a new file."""
		self.csv_reader.save_as()
		self._show_status("File saved as ...", 2000)

	def save_to_pdf(self) -> None:
		"""Save the current table data to a PDF."""
		df = self._table_to_dataframe(self.ui.tableWidget)

		if df is None:
			Message(
				parent=self.ui.centralwidget,
				title="Error",
				text="The table is empty or contains invalid data.",
				icon=QMessageBox.Icon.Warning,
				default_button=QMessageBox.StandardButton.Ok,
			).show()
			return

		PdfExporter(self).export(df)
		self._show_status("PDF exported", 2000)

	def exit(self) -> None:
		"""Exit the application."""
		self.close()

	def about(self) -> None:
		"""Show the About dialog."""
		Message(
			parent=self.ui.centralwidget,
			title="About",
			text="Personal Finance App\nVersion 1.0\n\nCreated by Denis Topallaj.\n© 2025 All rights reserved.",
			icon=QMessageBox.Icon.Information,
			default_button=QMessageBox.StandardButton.Ok,
		).show()
		self._show_status("About Personal Finance App", 2000)

	def user_guide(self) -> None:
		"""Show the User Guide dialog."""
		Message(
			parent=self.ui.centralwidget,
			title="User Guide",
			text=(
				"User Guide\nHow to use the Personal Finance App:\n\n"
				"1. Import a CSV file.\n"
				"2. Edit the CSV file.\n"
				"3. Save the CSV file.\n"
				"4. Export the CSV file to PDF.\n\n"
				"You can also view the charts of your finances (Advanced/Charts).\n\n"
				"Created by Denis Topallaj.\n© 2025 All rights reserved."
			),
			icon=QMessageBox.Icon.Information,
			default_button=QMessageBox.StandardButton.Ok,
		).show()
		self._show_status("User Guide", 2000)

	def charts(self) -> None:
		"""Display financial charts based on the table data."""
		df = self._table_to_dataframe(self.ui.tableWidget)

		if df is None or df.empty:
			Message(
				parent=self.ui.centralwidget,
				title="Error",
				text="The table is empty or contains invalid data.",
				icon=QMessageBox.Icon.Warning,
				default_button=QMessageBox.StandardButton.Ok,
				informative_text="Please import or enter valid data before viewing charts.",
			).show()
			return

		Charts(self, df).exec()
		self._show_status("Charts Created", 2000)

	def undo(self) -> None:
		"""Undo the last table edit."""
		self._ignore_change = True
		self.undo_stack.undo()
		self._ignore_change = False
		self._show_status("Undo", 2000)

	def redo(self) -> None:
		"""Redo the previously undone table edit."""
		self._ignore_change = True
		self.undo_stack.redo()
		self._ignore_change = False
		self._show_status("Redo", 2000)

	def save(self) -> None:
		"""Quick save the current data."""
		self.csv_reader.quick_save()
		self._show_status("File saved", 2000)

	def export_to_pdf(self) -> None:
		"""Export the current data directly to a PDF."""
		self.save_to_pdf()
