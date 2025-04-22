from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QColor

class HexView(QWidget):
    """Hex view widget for displaying EEPROM data in table format"""
    
    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.data = bytearray()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Set monospaced font
        font = QFont("Monospace")
        font.setFixedPitch(True)
        font.setPointSize(10)
        
        # Create table for hex view
        self.table = QTableWidget()
        self.table.setFont(font)
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.PenStyle.SolidLine)
        self.table.verticalHeader().setVisible(True)
        self.table.horizontalHeader().setVisible(True)
        self.table.setAlternatingRowColors(True)
        
        # Set dark theme colors
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: 1px solid #333333;
                gridline-color: #333333;
            }
            QTableWidget::item {
                padding: 5px;
                font-family: "Monospace";
            }
            QTableWidget::item:selected {
                background-color: #264F78;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #D4D4D4;
                padding: 5px;
                border: 1px solid #333333;
                font-family: "Monospace";
            }
            QTableWidget:alternate-background-color {
                background-color: #252526;
            }
        """)
        
        layout.addWidget(self.table)
        
    def set_data(self, data):
        """Set data and update the hex view"""
        self.data = data
        self.update_hex_view()
        
    def get_data(self):
        """Get current data"""
        return self.data
        
    def update_hex_view(self):
        """Update the hex view with current data"""
        if not self.data:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
            
        bytes_per_row = 16
        num_rows = (len(self.data) + bytes_per_row - 1) // bytes_per_row
        
        # Set up table structure - 16 columns for hex + separator + 16 for ASCII
        total_columns = bytes_per_row * 2 + 1  # Added separator column
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(total_columns)
        
        # Set up headers
        headers = []
        # Hex headers
        for i in range(bytes_per_row):
            headers.append(f"{i:02X}")
        # Separator header
        headers.append("")
        # ASCII headers
        for i in range(bytes_per_row):
            headers.append(f"A{i:X}")
        self.table.setHorizontalHeaderLabels(headers)
        
        # Set row headers (addresses)
        row_headers = [f"{i * bytes_per_row:08X}" for i in range(num_rows)]
        self.table.setVerticalHeaderLabels(row_headers)
        
        # Fill table with data
        for row in range(num_rows):
            # Add separator column
            separator_item = QTableWidgetItem("")
            separator_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            # separator_item.setBackground(QColor("#333333"))
            self.table.setItem(row, bytes_per_row, separator_item)
            
            for col in range(bytes_per_row):
                idx = row * bytes_per_row + col
                if idx < len(self.data):
                    byte = self.data[idx]
                    
                    # Hex value
                    hex_item = QTableWidgetItem(f"{byte:02X}")
                    hex_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    hex_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    self.table.setItem(row, col, hex_item)
                    
                    # ASCII value (in separate column after separator)
                    ascii_char = chr(byte) if 32 <= byte <= 126 else '.'
                    ascii_item = QTableWidgetItem(ascii_char)
                    ascii_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    ascii_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    self.table.setItem(row, col + bytes_per_row + 1, ascii_item)
                else:
                    # Empty cells for padding
                    empty_hex = QTableWidgetItem("")
                    empty_hex.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    self.table.setItem(row, col, empty_hex)
                    
                    empty_ascii = QTableWidgetItem("")
                    empty_ascii.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    self.table.setItem(row, col + bytes_per_row + 1, empty_ascii)
        
        # Adjust column widths
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        for col in range(total_columns):
            if col == bytes_per_row:  # Separator column
                self.table.setColumnWidth(col, 20)
            else:
                self.table.setColumnWidth(col, 35)
        
        # Adjust row heights
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        for row in range(num_rows):
            self.table.setRowHeight(row, 30)
            
    def modify_byte(self, address, value):
        """Modify a byte at the specified address"""
        if 0 <= address < len(self.data):
            self.data[address] = value
            self.update_hex_view()
            return True
        return False