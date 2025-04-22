from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QSpinBox, QLineEdit, QPushButton, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSlot, QRegularExpression
from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator

class ByteEditor(QWidget):
    """Byte editor widget for modifying individual bytes"""
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.data = bytearray()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Single byte editor
        byte_group = QGroupBox("Single Byte Editor")
        byte_layout = QHBoxLayout(byte_group)
        
        # Address input
        addr_label = QLabel("Address (hex):")
        self.addr_edit = QLineEdit()
        self.addr_edit.setMaximumWidth(100)
        # Only allow hex characters
        hex_regex = QRegularExpression("[0-9A-Fa-f]+")
        self.addr_edit.setValidator(QRegularExpressionValidator(hex_regex))
        self.addr_edit.textChanged.connect(self.update_current_byte)
        
        # Value input
        value_label = QLabel("Value (hex):")
        self.value_edit = QLineEdit()
        self.value_edit.setMaximumWidth(50)
        # Only allow hex characters, max 2
        byte_regex = QRegularExpression("[0-9A-Fa-f]{1,2}")
        self.value_edit.setValidator(QRegularExpressionValidator(byte_regex))
        
        # ASCII representation
        ascii_label = QLabel("ASCII:")
        self.ascii_edit = QLineEdit()
        self.ascii_edit.setMaximumWidth(50)
        self.ascii_edit.setMaxLength(1)
        self.ascii_edit.textChanged.connect(self.ascii_changed)
        
        # Write button
        self.write_button = QPushButton("Write Byte")
        self.write_button.clicked.connect(self.write_byte)
        
        byte_layout.addWidget(addr_label)
        byte_layout.addWidget(self.addr_edit)
        byte_layout.addWidget(value_label)
        byte_layout.addWidget(self.value_edit)
        byte_layout.addWidget(ascii_label)
        byte_layout.addWidget(self.ascii_edit)
        byte_layout.addWidget(self.write_button)
        byte_layout.addStretch()
        
        layout.addWidget(byte_group)
        
        # Range editor
        range_group = QGroupBox("Memory Range")
        range_layout = QHBoxLayout(range_group)
        
        # Start address
        start_label = QLabel("Start:")
        self.start_edit = QLineEdit()
        self.start_edit.setMaximumWidth(100)
        self.start_edit.setValidator(QRegularExpressionValidator(hex_regex))
        
        # End address
        end_label = QLabel("End:")
        self.end_edit = QLineEdit()
        self.end_edit.setMaximumWidth(100)
        self.end_edit.setValidator(QRegularExpressionValidator(hex_regex))
        
        # Fill value
        fill_label = QLabel("Fill Value:")
        self.fill_edit = QLineEdit()
        self.fill_edit.setMaximumWidth(50)
        self.fill_edit.setValidator(QRegularExpressionValidator(byte_regex))
        self.fill_edit.setText("FF")
        
        # Fill button
        self.fill_button = QPushButton("Fill Range")
        self.fill_button.clicked.connect(self.fill_range)
        
        range_layout.addWidget(start_label)
        range_layout.addWidget(self.start_edit)
        range_layout.addWidget(end_label)
        range_layout.addWidget(self.end_edit)
        range_layout.addWidget(fill_label)
        range_layout.addWidget(self.fill_edit)
        range_layout.addWidget(self.fill_button)
        range_layout.addStretch()
        
        layout.addWidget(range_group)
        
        # Add spacer at the bottom
        layout.addStretch()
        
    def set_data(self, data):
        """Set data for the editor"""
        self.data = data
        
    def get_data(self):
        """Get current data"""
        return self.data
        
    @pyqtSlot()
    def update_current_byte(self):
        """Update value and ASCII displays for current address"""
        try:
            addr_text = self.addr_edit.text()
            if not addr_text:
                return
                
            addr = int(addr_text, 16)
            if addr < len(self.data):
                # Update value
                value = self.data[addr]
                self.value_edit.setText(f"{value:02X}")
                
                # Update ASCII
                if 32 <= value <= 126:  # Printable ASCII
                    self.ascii_edit.setText(chr(value))
                else:
                    self.ascii_edit.setText("")
        except ValueError:
            pass
            
    @pyqtSlot(str)
    def ascii_changed(self, text):
        """Handle ASCII text changes"""
        if text:
            # Get ASCII value
            value = ord(text[0])
            # Update hex value
            self.value_edit.setText(f"{value:02X}")
            
    @pyqtSlot()
    def write_byte(self):
        """Write byte to the data"""
        try:
            addr_text = self.addr_edit.text()
            value_text = self.value_edit.text()
            
            if not addr_text or not value_text:
                return
                
            addr = int(addr_text, 16)
            value = int(value_text, 16)
            
            if addr < len(self.data):
                self.data[addr] = value
                self.logger.info(f"Wrote byte at address 0x{addr:04X}: 0x{value:02X}")
                
                # Move to next address
                self.addr_edit.setText(f"{addr + 1:X}")
        except ValueError:
            self.logger.error("Invalid address or value")
            
    @pyqtSlot()
    def fill_range(self):
        """Fill range with specified value"""
        try:
            start_text = self.start_edit.text()
            end_text = self.end_edit.text()
            fill_text = self.fill_edit.text()
            
            if not start_text or not end_text or not fill_text:
                return
                
            start = int(start_text, 16)
            end = int(end_text, 16)
            fill = int(fill_text, 16)
            
            # Validate range
            if start > end or end >= len(self.data):
                self.logger.error("Invalid address range")
                return
                
            # Fill range
            for addr in range(start, end + 1):
                self.data[addr] = fill
                
            self.logger.info(f"Filled range 0x{start:04X}-0x{end:04X} with 0x{fill:02X}")
        except ValueError:
            self.logger.error("Invalid address or value")