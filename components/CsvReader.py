from PySide6.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox
import pandas as pd
from pandas import DataFrame
from typing import Optional

from .Message import Message


class CsvReader:
	"""Handles reading from and writing to CSV files for the application."""

	def __init__(self, ui: object) -> None:
		"""
		Initialize the CsvReader.

		Args:
			ui (object): The user interface instance containing the table widget.
		"""
		self.ui = ui
		self.current_filename: Optional[str] = None

	def _check_csv_columns(self, df: DataFrame) -> bool:
		"""
		Check if the dataframe has the required columns.

		Args:
			df (DataFrame): The dataframe to check.

		Returns:
			bool: True if required columns exist, False otherwise.
		"""
		required_columns = ["Description", "Date", "Type", "Amount"]
		return all(col in df.columns for col in required_columns)

	def read(self) -> None:
		"""Open a file dialog to read a CSV file and populate the table widget."""
		filename, _ = QFileDialog.getOpenFileName(
			self.ui.centralwidget, "Open File", "", "CSV Files (*.csv)"
		)
		if not filename:
			return

		self.current_filename = filename
		try:
			df = pd.read_csv(filename)
		except Exception as e:
			Message(
				parent=self.ui.centralwidget,
				title="Error",
				text="Failed to read the CSV file.",
				icon=QMessageBox.Icon.Critical,
				default_button=QMessageBox.StandardButton.Ok,
				informative_text=str(e),
			).show()
			return

		if not self._check_csv_columns(df):
			Message(
				parent=self.ui.centralwidget,
				title="Error",
				text="The CSV file does not have the required columns. Please check the User Guide for more information.",
				icon=QMessageBox.Icon.Warning,
				default_button=QMessageBox.StandardButton.Ok,
				informative_text="Required columns: Description, Date, Type, Amount",
			).show()
			return

		table = self.ui.tableWidget
		table.setRowCount(df.shape[0])
		table.setColumnCount(df.shape[1])
		table.setHorizontalHeaderLabels(df.columns)

		for row in range(df.shape[0]):
			for col in range(df.shape[1]):
				item = QTableWidgetItem(str(df.iat[row, col]))
				table.setItem(row, col, item)

		table.resizeColumnsToContents()

	def get_table_data(self) -> DataFrame:
		"""
		Retrieve data from the table widget as a pandas DataFrame.

		Returns:
			DataFrame: The extracted table data.
		"""
		table = self.ui.tableWidget
		rows, cols = table.rowCount(), table.columnCount()

		headers = [
			(table.horizontalHeaderItem(col).text() if table.horizontalHeaderItem(col) else f"Column {col+1}")
			for col in range(cols)
		]

		data = []
		for row in range(rows):
			row_data = []
			for col in range(cols):
				item = table.item(row, col)
				row_data.append(item.text() if item else "")
			data.append(row_data)

		return pd.DataFrame(data, columns=headers)

	def save_as(self) -> None:
		"""Open a save dialog and save the current table data to a specified CSV file."""
		filename, _ = QFileDialog.getSaveFileName(
			self.ui.centralwidget, "Save File As", "", "CSV Files (*.csv)"
		)
		if not filename:
			return

		df = self.get_table_data()
		df.to_csv(filename, index=False)
		self.current_filename = filename

	def quick_save(self) -> None:
		"""Save the table data to the last opened/saved file, or prompt 'Save As' if none."""
		if self.current_filename:
			df = self.get_table_data()
			df.to_csv(self.current_filename, index=False)
		else:
			self.save_as()
