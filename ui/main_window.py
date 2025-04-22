import os
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, 
                              QWidget, QPushButton, QComboBox, QLabel, 
                              QTabWidget, QSplitter, QFileDialog, 
                              QMessageBox, QStatusBar, QGroupBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from ui.hex_view import HexView
from ui.byte_editor import ByteEditor
from ui.log_console import LogConsole
from hardware.ch341_manager import CH341Manager
from utils.eeprom_types import EEPROM_SIZES, I2C_SPEEDS, MANUFACTURERS

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, settings, logger):
        super().__init__()
        self.settings = settings
        self.logger = logger
        self.ch341 = CH341Manager(logger)
        
        self.init_ui()
        self.setup_connections()
        self.load_settings()
        
        # Status update timer
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("EEPROM Programmer")
        self.setMinimumSize(900, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create control panel (top)
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Create splitter for main area
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Create tabs for different views
        self.tabs = QTabWidget()
        
        # Hex view tab
        self.hex_view = HexView(self.logger)
        self.tabs.addTab(self.hex_view, "Hex View")
        
        # Byte editor tab
        self.byte_editor = ByteEditor(self.logger)
        self.tabs.addTab(self.byte_editor, "Byte Editor")
        
        splitter.addWidget(self.tabs)
        
        # Create log console
        self.log_console = LogConsole(self.logger)
        splitter.addWidget(self.log_console)
        
        # Set initial splitter sizes
        splitter.setSizes([400, 200])
        
        main_layout.addWidget(splitter)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.connection_status = QLabel("Status: Disconnected")
        self.status_bar.addPermanentWidget(self.connection_status)
        
    def create_control_panel(self):
        """Create the control panel with buttons and dropdowns"""
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        
        # Connection group
        connection_group = QGroupBox("Connection")
        conn_layout = QHBoxLayout(connection_group)
        
        # Manufacturer dropdown
        self.manufacturer_label = QLabel("Manufacturer:")
        self.manufacturer_combo = QComboBox()
        self.manufacturer_combo.addItems(MANUFACTURERS.keys())
        self.manufacturer_combo.currentTextChanged.connect(self.update_eeprom_sizes)
        
        # EEPROM size dropdown
        self.eeprom_size_label = QLabel("EEPROM Type:")
        self.eeprom_size_combo = QComboBox()
        
        # I2C speed dropdown
        self.i2c_speed_label = QLabel("I2C Speed:")
        self.i2c_speed_combo = QComboBox()
        for speed in I2C_SPEEDS:
            self.i2c_speed_combo.addItem(speed["name"])
        
        # Connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.setProperty("type", "connect")
        
        # Detect button
        self.detect_button = QPushButton("Detect EEPROM")
        self.detect_button.setEnabled(False)
        
        conn_layout.addWidget(self.manufacturer_label)
        conn_layout.addWidget(self.manufacturer_combo)
        conn_layout.addWidget(self.eeprom_size_label)
        conn_layout.addWidget(self.eeprom_size_combo)
        conn_layout.addWidget(self.i2c_speed_label)
        conn_layout.addWidget(self.i2c_speed_combo)
        conn_layout.addWidget(self.connect_button)
        conn_layout.addWidget(self.detect_button)
        
        panel_layout.addWidget(connection_group)
        
        # Operation group
        operation_group = QGroupBox("Operations")
        op_layout = QHBoxLayout(operation_group)
        
        # Read button
        self.read_button = QPushButton("Read")
        self.read_button.setEnabled(False)
        self.read_button.setProperty("type", "read")
        
        # Write button
        self.write_button = QPushButton("Write")
        self.write_button.setEnabled(False)
        self.write_button.setProperty("type", "write")
        
        # Erase button
        self.erase_button = QPushButton("Erase")
        self.erase_button.setEnabled(False)
        self.erase_button.setProperty("type", "erase")
        
        # Verify button
        self.verify_button = QPushButton("Verify")
        self.verify_button.setEnabled(False)
        
        # Dump button
        self.dump_button = QPushButton("Save Hex")
        self.dump_button.setEnabled(False)
        
        # Load button
        self.load_button = QPushButton("Load Hex")
        
        op_layout.addWidget(self.read_button)
        op_layout.addWidget(self.write_button)
        op_layout.addWidget(self.erase_button)
        op_layout.addWidget(self.verify_button)
        op_layout.addWidget(self.dump_button)
        op_layout.addWidget(self.load_button)
        
        panel_layout.addWidget(operation_group)
        
        # Initialize EEPROM sizes for default manufacturer
        self.update_eeprom_sizes(self.manufacturer_combo.currentText())
        
        return panel
        
    def update_eeprom_sizes(self, manufacturer):
        """Update EEPROM size dropdown based on selected manufacturer"""
        self.eeprom_size_combo.clear()
        if manufacturer in MANUFACTURERS:
            devices = MANUFACTURERS[manufacturer]["devices"]
            prefix = MANUFACTURERS[manufacturer]["prefix"]
            
            for size in EEPROM_SIZES:
                # Extract base model (e.g., "24C32" from "24C32 (32Kbit / 4K bytes)")
                base_model = size["name"].split()[0]
                # Check if this size matches any of the manufacturer's devices
                if any(device in base_model for device in devices):
                    # Add manufacturer prefix if needed
                    if not base_model.startswith(prefix):
                        display_name = f"{prefix}{base_model[4:]} {size['name'][6:]}"
                    else:
                        display_name = size["name"]
                    self.eeprom_size_combo.addItem(display_name)
        
    def setup_connections(self):
        """Connect UI signals to slots"""
        # Connection buttons
        self.connect_button.clicked.connect(self.toggle_connection)
        self.detect_button.clicked.connect(self.detect_eeprom)
        
        # Operation buttons
        self.read_button.clicked.connect(self.read_eeprom)
        self.write_button.clicked.connect(self.write_eeprom)
        self.erase_button.clicked.connect(self.erase_eeprom)
        self.verify_button.clicked.connect(self.verify_eeprom)
        self.dump_button.clicked.connect(self.save_hex_file)
        self.load_button.clicked.connect(self.load_hex_file)
        
    def load_settings(self):
        """Load settings from QSettings"""
        # Restore window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
        # Restore manufacturer
        manufacturer = self.settings.value("manufacturer", 0, int)
        self.manufacturer_combo.setCurrentIndex(manufacturer)
        
        # Restore EEPROM size and I2C speed
        eeprom_size = self.settings.value("eeprom_size", 0, int)
        self.eeprom_size_combo.setCurrentIndex(eeprom_size)
        
        i2c_speed = self.settings.value("i2c_speed", 0, int)
        self.i2c_speed_combo.setCurrentIndex(i2c_speed)
        
    def save_settings(self):
        """Save settings to QSettings"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("manufacturer", self.manufacturer_combo.currentIndex())
        self.settings.setValue("eeprom_size", self.eeprom_size_combo.currentIndex())
        self.settings.setValue("i2c_speed", self.i2c_speed_combo.currentIndex())
        
    def closeEvent(self, event):
        """Handle window close event"""
        self.save_settings()
        # Disconnect from CH341 if connected
        if self.ch341.is_connected():
            self.ch341.disconnect()
        event.accept()
        
    def get_eeprom_size_by_name(self, name):
        """Get EEPROM size configuration by name"""
        for size in EEPROM_SIZES:
            if name in size["name"]:
                return size
        return None
        
    @pyqtSlot()
    def toggle_connection(self):
        """Toggle connection to CH341"""
        if not self.ch341.is_connected():
            # Get selected EEPROM size and I2C speed
            eeprom_idx = self.eeprom_size_combo.currentIndex()
            eeprom_size = EEPROM_SIZES[eeprom_idx]
            
            i2c_idx = self.i2c_speed_combo.currentIndex()
            i2c_speed = I2C_SPEEDS[i2c_idx]
            
            # Connect to CH341
            success = self.ch341.connect(eeprom_size, i2c_speed)
            
            if success:
                self.logger.info(f"Connected to CH341 with {i2c_speed['name']}")
                self.connect_button.setText("Disconnect")
                self.connect_button.setProperty("type", "disconnect")
                self.connect_button.style().unpolish(self.connect_button)
                self.connect_button.style().polish(self.connect_button)
                self.update_ui_connected()
            else:
                QMessageBox.critical(self, "Connection Error", 
                                   "Failed to connect to CH341 device.")
        else:
            # Disconnect from CH341
            self.ch341.disconnect()
            self.logger.info("Disconnected from CH341")
            self.connect_button.setText("Connect")
            self.connect_button.setProperty("type", "connect")
            self.connect_button.style().unpolish(self.connect_button)
            self.connect_button.style().polish(self.connect_button)
            self.update_ui_disconnected()
    
    def update_ui_connected(self):
        """Update UI elements for connected state"""
        self.detect_button.setEnabled(True)
        self.read_button.setEnabled(True)
        self.write_button.setEnabled(True)
        self.erase_button.setEnabled(True)
        self.verify_button.setEnabled(True)
        self.dump_button.setEnabled(True)
        
    def update_ui_disconnected(self):
        """Update UI elements for disconnected state"""
        self.detect_button.setEnabled(False)
        self.read_button.setEnabled(False)
        self.write_button.setEnabled(False)
        self.erase_button.setEnabled(False)
        self.verify_button.setEnabled(False)
        self.dump_button.setEnabled(False)
        
    @pyqtSlot()
    def update_status(self):
        """Update status bar with current connection state"""
        if self.ch341.is_connected():
            self.connection_status.setText("Status: Connected")
        else:
            self.connection_status.setText("Status: Disconnected")
            
    @pyqtSlot()
    def detect_eeprom(self):
        """Detect connected EEPROM"""
        self.logger.info("Detecting EEPROM...")
        eeprom_info = self.ch341.detect_eeprom()
        
        if eeprom_info:
            # Find matching EEPROM size configuration
            detected_size = self.get_eeprom_size_by_name(eeprom_info["type"])
            if detected_size:
                # Update UI with detected type
                for i in range(self.eeprom_size_combo.count()):
                    if detected_size["name"] in self.eeprom_size_combo.itemText(i):
                        self.eeprom_size_combo.setCurrentIndex(i)
                        break
            
            msg = (f"Detected EEPROM:\n"
                  f"Type: {eeprom_info['type']}\n"
                  f"Size: {eeprom_info['size']} bytes\n"
                  f"Address: 0x{eeprom_info['address']:02X}")
            QMessageBox.information(self, "EEPROM Detected", msg)
        else:
            QMessageBox.warning(self, "Detection Failed", 
                              "No EEPROM detected or communication error.")
            
    @pyqtSlot()
    def read_eeprom(self):
        """Read EEPROM contents"""
        self.logger.info("Reading EEPROM...")
        self.statusBar().showMessage("Reading EEPROM...")
        
        data = self.ch341.read_eeprom()
        if data:
            self.hex_view.set_data(data)
            self.byte_editor.set_data(data)
            self.statusBar().showMessage("EEPROM read successfully", 3000)
        else:
            QMessageBox.warning(self, "Read Failed", 
                              "Failed to read EEPROM contents.")
            self.statusBar().showMessage("EEPROM read failed", 3000)
            
    @pyqtSlot()
    def write_eeprom(self):
        """Write data to EEPROM"""
        data = self.hex_view.get_data()
        if not data:
            QMessageBox.warning(self, "Write Failed", 
                              "No data to write.")
            return
            
        # Confirm write operation
        reply = QMessageBox.question(self, "Write Confirmation", 
                                   "Writing will overwrite existing EEPROM data. Continue?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logger.info("Writing EEPROM...")
            self.statusBar().showMessage("Writing EEPROM...")
            
            success = self.ch341.write_eeprom(data)
            if success:
                self.statusBar().showMessage("EEPROM written successfully", 3000)
            else:
                QMessageBox.warning(self, "Write Failed", 
                                  "Failed to write EEP ROM.")
                self.statusBar().showMessage("EEPROM write failed", 3000)
                
    @pyqtSlot()
    def erase_eeprom(self):
        """Erase EEPROM contents"""
        # Confirm erase operation
        reply = QMessageBox.question(self, "Erase Confirmation", 
                                   "This will erase all EEPROM data. Continue?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logger.info("Erasing EEPROM...")
            self.statusBar().showMessage("Erasing EEPROM...")
            
            success = self.ch341.erase_eeprom()
            if success:
                # Update views with empty data
                eeprom_idx = self.eeprom_size_combo.currentIndex()
                eeprom_size = EEPROM_SIZES[eeprom_idx]
                empty_data = bytearray([0xFF] * eeprom_size["bytes"])
                
                self.hex_view.set_data(empty_data)
                self.byte_editor.set_data(empty_data)
                
                self.statusBar().showMessage("EEPROM erased successfully", 3000)
            else:
                QMessageBox.warning(self, "Erase Failed", 
                                  "Failed to erase EEPROM.")
                self.statusBar().showMessage("EEPROM erase failed", 3000)
                
    @pyqtSlot()
    def verify_eeprom(self):
        """Verify EEPROM contents match current data"""
        expected_data = self.hex_view.get_data()
        if not expected_data:
            QMessageBox.warning(self, "Verify Failed", 
                              "No data to verify against.")
            return
            
        self.logger.info("Verifying EEPROM...")
        self.statusBar().showMessage("Verifying EEPROM...")
        
        success, mismatch = self.ch341.verify_eeprom(expected_data)
        if success:
            QMessageBox.information(self, "Verify Successful", 
                                 "EEPROM contents match expected data.")
            self.statusBar().showMessage("EEPROM verification successful", 3000)
        else:
            QMessageBox.warning(self, "Verify Failed", 
                              f"EEPROM contents don't match at address 0x{mismatch:04X}.")
            self.statusBar().showMessage("EEPROM verification failed", 3000)
            
    @pyqtSlot()
    def save_hex_file(self):
        """Save EEPROM data as Intel HEX file"""
        data = self.hex_view.get_data()
        if not data:
            QMessageBox.warning(self, "Save Failed", 
                              "No data to save.")
            return
            
        # Get save file name
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save HEX File", "", "Intel HEX Files (*.hex);;All Files (*)"
        )
        
        if file_name:
            from utils.hex_format import data_to_intel_hex
            
            try:
                with open(file_name, 'w') as f:
                    hex_data = data_to_intel_hex(data)
                    f.write(hex_data)
                    
                self.logger.info(f"Saved HEX file to {file_name}")
                self.statusBar().showMessage(f"Saved HEX file to {file_name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Save Failed", 
                                   f"Failed to save HEX file: {str(e)}")
                
    @pyqtSlot()
    def load_hex_file(self):
        """Load data from Intel HEX file"""
        # Get open file name
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open HEX File", "", "Intel HEX Files (*.hex);;All Files (*)"
        )
        
        if file_name:
            from utils.hex_format import intel_hex_to_data
            
            try:
                with open(file_name, 'r') as f:
                    hex_data = f.read()
                    
                data = intel_hex_to_data(hex_data)
                self.hex_view.set_data(data)
                self.byte_editor.set_data(data)
                
                self.logger.info(f"Loaded HEX file from {file_name}")
                self.statusBar().showMessage(f"Loaded HEX file from {file_name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Load Failed", 
                                   f"Failed to load HEX file: {str(e)}")