from PySide6.QtWidgets import QDialog, QVBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from pandas import DataFrame
from typing import Any


class Charts(QDialog):
	"""Dialog to display finance charts including a pie chart and a line chart."""

	def __init__(self, parent: Any, df: DataFrame) -> None:
		"""
		Initialize the Charts dialog.

		Args:
			parent (Any): The parent widget.
			df (DataFrame): The dataframe containing financial data.
		"""
		super().__init__(parent)
		self.setWindowTitle("Finance Charts")
		self.resize(900, 700)

		layout = QVBoxLayout()
		self.setLayout(layout)

		# Create and add charts to the layout
		layout.addWidget(self._create_pie_chart(df))
		layout.addWidget(self._create_line_chart(df))

	def _create_pie_chart(self, df: DataFrame) -> FigureCanvas:
		"""
		Create a pie chart showing expenses/incomes per description.

		Args:
			df (DataFrame): The dataframe containing financial data.

		Returns:
			FigureCanvas: The canvas widget displaying the pie chart.
		"""
		fig, ax = plt.subplots(figsize=(4, 4))
		type_sums = (
			df.groupby('Description')['Amount']
			.sum()
			.sort_values(ascending=False)
			.head(10)
		)

		ax.pie(
			type_sums,
			labels=type_sums.index,
			autopct='%1.1f%%',
			startangle=140
		)
		ax.set_title('Expenses/Incomes per Description')

		return FigureCanvas(fig)

	def _create_line_chart(self, df: DataFrame) -> FigureCanvas:
		"""
		Create a line chart showing the balance over time.

		Args:
			df (DataFrame): The dataframe containing financial data.

		Returns:
			FigureCanvas: The canvas widget displaying the line chart.
		"""
		fig, ax = plt.subplots(figsize=(6, 4))

		# Prepare the dataframe
		df = df.copy()
		df['SignedAmount'] = df.apply(
			lambda row: row['Amount'] if row['Type'].lower() == 'income' else -row['Amount'],
			axis=1
		)
		df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
		df = df.dropna(subset=['Date']).sort_values('Date')
		df['Balance'] = df['SignedAmount'].cumsum()

		ax.plot(df['Date'], df['Balance'], marker='o')
		ax.set_title('Money Over Time')
		ax.set_xlabel('Date')
		ax.set_ylabel('Balance')
		ax.grid(True)

		return FigureCanvas(fig)
