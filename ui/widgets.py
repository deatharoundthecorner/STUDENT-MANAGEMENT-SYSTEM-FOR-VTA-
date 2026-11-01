# ui/widgets.py
# Reusable, self-contained UI components adhering to the ChatGPT-inspired design system

from PySide6.QtWidgets import (QLineEdit, QFrame, QHBoxLayout, QPushButton,
                             QLabel, QWidget, QSizePolicy)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt, QSize, Signal
from ui.icons import get_icon


class PasswordLineEdit(QLineEdit):
    """
    Modern password input field with an integrated trailing show/hide toggle.
    Preserves cursor position and text selection on toggle.
    """
    def __init__(self, placeholder: str = "", parent: QWidget = None):
        super().__init__(parent)
        self.setEchoMode(QLineEdit.Password)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(38)
        self.setProperty("class", "FormInput")

        # Trailing action for show/hide password
        self._is_visible = False
        self._action = self.addAction(
            get_icon("eye", color="#64748B", size=16),
            QLineEdit.TrailingPosition
        )
        self._action.setToolTip("Show / Hide password")
        self._action.triggered.connect(self.toggle_echo_mode)

    def toggle_echo_mode(self):
        pos = self.cursorPosition()
        has_sel = self.hasSelectedText()
        sel_start = self.selectionStart()
        sel_len = len(self.selectedText())

        if self.echoMode() == QLineEdit.Password:
            self.setEchoMode(QLineEdit.Normal)
            self._is_visible = True
            self._action.setIcon(get_icon("eye_off", color="#2563EB", size=16))
        else:
            self.setEchoMode(QLineEdit.Password)
            self._is_visible = False
            self._action.setIcon(get_icon("eye", color="#64748B", size=16))

        # Restore cursor and selection
        if has_sel:
            self.setSelection(sel_start, sel_len)
        else:
            self.setCursorPosition(pos)

    def reset_visibility(self):
        self.setEchoMode(QLineEdit.Password)
        self._is_visible = False
        self._action.setIcon(get_icon("eye", color="#64748B", size=16))


def make_password_input(placeholder: str = "", height: int = 38):
    """
    Backward-compatible factory returning (container, line_edit).
    Returns (PasswordLineEdit, PasswordLineEdit) so callers can add either or both.
    """
    field = PasswordLineEdit(placeholder=placeholder)
    if height != 38:
        field.setFixedHeight(height)
    return field, field


class FormLabel(QLabel):
    """Consistent, professional form field label."""
    def __init__(self, text: str, required: bool = False, parent: QWidget = None):
        super().__init__(parent)
        if required:
            self.setText(f"{text} <span style='color: #EF4444;'>*</span>")
        else:
            self.setText(text)
        self.setProperty("class", "FormLabel")


class StatusBanner(QLabel):
    """
    Reserved-height status and feedback banner that avoids layout shifts
    when error or success messages appear.
    """
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWordWrap(True)
        self.setMinimumHeight(24)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setProperty("class", "StatusBanner")
        self.setText("")

    def show_error(self, message: str):
        self.setStyleSheet("color: #DC2626; font-size: 12px; font-weight: 500;")
        self.setText(message)

    def show_success(self, message: str):
        self.setStyleSheet("color: #059669; font-size: 12px; font-weight: 500;")
        self.setText(message)

    def show_info(self, message: str):
        self.setStyleSheet("color: #64748B; font-size: 12px; font-weight: 500;")
        self.setText(message)

    def clear_message(self):
        self.setStyleSheet("")
        self.setText("")
