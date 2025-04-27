from PySide6.QtWidgets import QFileDialog, QMessageBox
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import os
from typing import Optional, List, Tuple


class PdfExporter:
	def __init__(self, parent=None):
		"""
		Initialize the PDF Exporter.

		Args:
			parent: The parent widget for dialog boxes.
		"""
		self.parent = parent

	def export(self, df: pd.DataFrame) -> None:
		"""
		Export the given DataFrame into a styled PDF with charts.

		Args:
			df (pd.DataFrame): The data to export.
		"""
		if not self._check_data(df):
			return

		file_path = self._get_save_path()
		if not file_path:
			return

		pie_path, time_path = self._create_chart_images(df)

		try:
			elements = self._create_pdf_elements(df, pie_path, time_path)
			self._build_pdf(file_path, elements)
			self._show_message("Success", "PDF exported successfully!", QMessageBox.Icon.Information)
		except Exception as e:
			self._show_message("Error", f"Failed to export PDF: {e}", QMessageBox.Icon.Critical)
		finally:
			self._cleanup_temp_files([pie_path, time_path])

	def _check_data(self, df: Optional[pd.DataFrame]) -> bool:
		"""
		Validate that the DataFrame is not empty.

		Args:
			df (Optional[pd.DataFrame]): The data to validate.

		Returns:
			bool: True if valid, False otherwise.
		"""
		if df is None or df.empty:
			self._show_message("Error", "No data to export.", QMessageBox.Icon.Warning)
			return False
		return True

	def _get_save_path(self) -> Optional[str]:
		"""
		Open a save file dialog for the PDF.

		Returns:
			Optional[str]: The selected file path, or None if canceled.
		"""
		file_path, _ = QFileDialog.getSaveFileName(
			self.parent, "Save PDF", "", "PDF Files (*.pdf)"
		)
		return file_path

	def _create_chart_images(self, df: pd.DataFrame) -> Tuple[str, str]:
		"""
		Create temporary chart images (Pie chart and Balance over Time chart).

		Args:
			df (pd.DataFrame): The data used for charts.

		Returns:
			Tuple[str, str]: Paths to the generated pie chart and time chart images.
		"""
		pie_path = self._create_pie_chart(df)
		time_path = self._create_time_chart(df)
		return pie_path, time_path

	def _create_pie_chart(self, df: pd.DataFrame) -> str:
		"""
		Create a pie chart and save it to a temporary file.

		Args:
			df (pd.DataFrame): The data used for the pie chart.

		Returns:
			str: Path to the pie chart image.
		"""
		fd, path = tempfile.mkstemp(suffix=".png")
		os.close(fd)

		pie_data = df.groupby('Description')['Amount'].apply(lambda x: x.astype(float).sum())
		pie_data = pie_data.sort_values(ascending=False).head(10)

		fig, ax = plt.subplots(figsize=(7, 7), dpi=120)
		ax.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140)
		ax.set_title('Expenses/Incomes per Description')
		plt.tight_layout()
		fig.savefig(path)
		plt.close(fig)

		return path

	def _create_time_chart(self, df: pd.DataFrame) -> str:
		"""
		Create a balance-over-time line chart and save it to a temporary file.

		Args:
			df (pd.DataFrame): The data used for the time chart.

		Returns:
			str: Path to the time chart image.
		"""
		fd, path = tempfile.mkstemp(suffix=".png")
		os.close(fd)

		df_time = df.copy()
		df_time['Amount'] = df_time['Amount'].astype(float)
		df_time['SignedAmount'] = df_time.apply(
			lambda row: row['Amount'] if row['Type'].lower() == 'income' else -row['Amount'],
			axis=1
		)
		df_time['Date'] = pd.to_datetime(df_time['Date'])
		df_time = df_time.sort_values('Date')
		df_time['Balance'] = df_time['SignedAmount'].cumsum()

		fig, ax = plt.subplots(figsize=(10, 5), dpi=120)
		ax.plot(df_time['Date'], df_time['Balance'], marker='o', color='tab:blue')
		ax.set_title('Money Over Time')
		ax.set_xlabel('Date')
		ax.set_ylabel('Balance')
		ax.grid(True)
		plt.tight_layout()
		fig.savefig(path)
		plt.close(fig)

		return path

	def _create_pdf_elements(self, df: pd.DataFrame, pie_path: str, time_path: str) -> List:
		"""
		Create PDF elements including table and charts.

		Args:
			df (pd.DataFrame): The data for the table.
			pie_path (str): Path to the pie chart image.
			time_path (str): Path to the time chart image.

		Returns:
			List: List of flowable ReportLab elements.
		"""
		styles = getSampleStyleSheet()
		elements = [
			Paragraph("Personal Finance Data", styles['Title']),
			Spacer(1, 12),
			self._create_table(df),
			Spacer(1, 24),
			Paragraph("Top 10 Expenses/Incomes per Description", styles['Heading2']),
			Image(pie_path, width=350, height=350),
			Spacer(1, 24),
			Paragraph("Money Over Time", styles['Heading2']),
			Image(time_path, width=450, height=250)
		]
		return elements

	def _create_table(self, df: pd.DataFrame) -> Table:
		"""
		Create a styled table for the PDF.

		Args:
			df (pd.DataFrame): The data for the table.

		Returns:
			Table: ReportLab Table element.
		"""
		expected_columns = ['Description', 'Date', 'Type', 'Amount']
		df = df.copy()
		df = df[expected_columns]
		df['Amount'] = df['Amount'].map(lambda x: f"{float(x):.2f}")

		data = [expected_columns] + df.values.tolist()

		table = Table(data, repeatRows=1)
		table.setStyle(TableStyle([
			('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
			('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
			('ALIGN', (0, 0), (-1, -1), 'CENTER'),
			('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
			('BOTTOMPADDING', (0, 0), (-1, 0), 12),
			('GRID', (0, 0), (-1, -1), 1, colors.black),
		]))
		return table

	def _build_pdf(self, file_path: str, elements: List) -> None:
		"""
		Build and save the PDF.

		Args:
			file_path (str): Path where the PDF will be saved.
			elements (List): List of ReportLab flowables.
		"""
		doc = SimpleDocTemplate(file_path, pagesize=A4)
		doc.build(elements)

	def _cleanup_temp_files(self, paths: List[str]) -> None:
		"""
		Remove temporary files created during PDF generation.

		Args:
			paths (List[str]): List of file paths to remove.
		"""
		for path in paths:
			if os.path.exists(path):
				os.remove(path)

	def _show_message(self, title: str, text: str, icon: QMessageBox.Icon) -> None:
		"""
		Show a message box.

		Args:
			title (str): The message box title.
			text (str): The main message text.
			icon (QMessageBox.Icon): The icon type.
		"""
		if self.parent:
			QMessageBox(icon, title, text, parent=self.parent).exec()
