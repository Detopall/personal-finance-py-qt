from typing import Optional
from PySide6.QtWidgets import QMessageBox, QWidget


class Message:
	"""
	A convenience wrapper for displaying customizable message boxes.
	"""

	def __init__(
		self,
		parent: Optional[QWidget] = None,
		title: str = "Message",
		text: str = "",
		informative_text: Optional[str] = None,
		detailed_text: Optional[str] = None,
		icon: QMessageBox.Icon = QMessageBox.Icon.Information,
		buttons: QMessageBox.StandardButtons = QMessageBox.StandardButton.Ok,
		default_button: Optional[QMessageBox.StandardButton] = None,
	) -> None:
		"""
		Initialize a new Message dialog.

		Args:
			parent (Optional[QWidget]): The parent widget for the message box.
			title (str): The title of the message box window.
			text (str): The main text content of the message.
			informative_text (Optional[str]): Additional informative text.
			detailed_text (Optional[str]): Optional detailed text shown on request.
			icon (QMessageBox.Icon): The icon to display (Information, Warning, Critical, etc.).
			buttons (QMessageBox.StandardButtons): The buttons to show in the dialog.
			default_button (Optional[QMessageBox.StandardButton]): The button that is selected by default.
		"""
		self.msg_box = QMessageBox(parent)
		self.msg_box.setWindowTitle(title)
		self.msg_box.setText(text)
		self.msg_box.setIcon(icon)
		self.msg_box.setStandardButtons(buttons)

		if informative_text:
			self.msg_box.setInformativeText(informative_text)

		if detailed_text:
			self.msg_box.setDetailedText(detailed_text)

		if default_button:
			self.msg_box.setDefaultButton(default_button)

	def show(self) -> int:
		"""
		Display the message box and wait for user interaction.

		Returns:
			int: The button clicked by the user.
		"""
		return self.msg_box.exec()
