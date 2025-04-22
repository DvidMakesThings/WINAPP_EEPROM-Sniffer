from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSlot, QObject, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat, QBrush
import logging

class QTextEditLogger(QObject, logging.Handler):
    """Logger handler that emits logs to a QTextEdit"""
    
    log_message = pyqtSignal(str, int)
    
    def __init__(self):
        super().__init__()
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
    def emit(self, record):
        msg = self.format(record)
        self.log_message.emit(msg, record.levelno)

class LogConsole(QWidget):
    """Log console widget for displaying application logs"""
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.init_ui()
        self.setup_logger()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create log text edit
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        
        # Set monospaced font
        font = QFont("Monospace")
        font.setFixedPitch(True)
        font.setPointSize(9)
        self.log_edit.setFont(font)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Clear button
        self.clear_button = QPushButton("Clear Log")
        self.clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_button)
        
        # Add stretch to push buttons to the left
        button_layout.addStretch()
        
        # Add widgets to layout
        layout.addWidget(self.log_edit)
        layout.addLayout(button_layout)
        
    def setup_logger(self):
        """Set up logger handler"""
        # Create logger handler
        self.log_handler = QTextEditLogger()
        self.log_handler.log_message.connect(self.append_log)
        
        # Add handler to logger
        self.logger.addHandler(self.log_handler)
        
    def cleanup_logger(self):
        """Clean up logger handler"""
        if hasattr(self, 'log_handler'):
            self.logger.removeHandler(self.log_handler)
            self.log_handler.close()
        
    def closeEvent(self, event):
        """Handle widget close event"""
        self.cleanup_logger()
        super().closeEvent(event)
        
    def __del__(self):
        """Clean up when object is deleted"""
        self.cleanup_logger()
        
    @pyqtSlot(str, int)
    def append_log(self, message, level):
        """Append log message with appropriate formatting"""
        # Create text format based on log level
        text_format = QTextCharFormat()
        
        if level >= logging.ERROR:
            text_format.setForeground(QBrush(QColor("#FF5252")))  # Red
        elif level >= logging.WARNING:
            text_format.setForeground(QBrush(QColor("#FFD740")))  # Amber
        elif level >= logging.INFO:
            text_format.setForeground(QBrush(QColor("#FFFFFF")))  # White
        else:  # DEBUG
            text_format.setForeground(QBrush(QColor("#B0BEC5")))  # Blue Grey
            
        # Append text with format
        cursor = self.log_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(message + "\n", text_format)
        
        # Auto-scroll to bottom
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_edit.setTextCursor(cursor)
        
    @pyqtSlot()
    def clear_log(self):
        """Clear log text"""
        self.log_edit.clear()