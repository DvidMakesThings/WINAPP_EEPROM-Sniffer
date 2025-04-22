"""Manager for CH341 USB-to-I2C adapter communication"""

import os
import time
import logging
from typing import Dict, List, Optional, Tuple, Union
from hardware.ch341_py_smbus import CH341  # Import the Python SMBus implementation

class CH341Manager:
    """Manager for CH341 USB-to-I2C adapter communication"""
    
    def __init__(self, logger):
        self.logger = logger
        self.device = None
        self.eeprom_size = None
        self.i2c_speed = None
        self.connected = False
        self.eeprom_addr = 0x50  # Default EEPROM address
        
    def is_connected(self):
        """Check if connected to CH341"""
        return self.connected
        
    def scan_i2c_bus(self):
        """Scan I2C bus for devices"""
        if not self.device:
            return None
            
        # Common EEPROM addresses
        eeprom_addresses = [0x50, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57]
        found_addresses = []
        
        for addr in eeprom_addresses:
            try:
                # Multiple detection attempts with delays
                for attempt in range(3):
                    if self.device.detect(addr):
                        found_addresses.append(addr)
                        self.logger.info(f"Found device at address 0x{addr:02X}")
                        break
                    time.sleep(0.01)  # 10ms delay between attempts
            except Exception as e:
                self.logger.debug(f"Scan error at address 0x{addr:02X}: {str(e)}")
                continue
                
        return found_addresses
        
    def detect_eeprom_type(self, addr):
        """Attempt to detect EEPROM type by probing memory access patterns"""
        if not self.device:
            return None
            
        try:
            # Try reading first byte with different addressing modes
            data = self.read_test_patterns(addr)
            if not data:
                return None
                
            # Analyze memory access patterns
            size = len(data)
            if size >= 4096:  # 32Kbit or larger
                return "24C32"
            elif size >= 2048:  # 16Kbit
                return "24C16"
            elif size >= 1024:  # 8Kbit
                return "24C08"
            elif size >= 512:  # 4Kbit
                return "24C04"
            elif size >= 256:  # 2Kbit
                return "24C02"
            else:  # 1Kbit
                return "24C01"
                
        except Exception as e:
            self.logger.debug(f"EEPROM type detection error: {str(e)}")
            
        return None
        
    def read_test_patterns(self, addr):
        """Read test patterns to determine EEPROM size"""
        try:
            # Try reading with 8-bit addressing
            data = bytearray()
            chunk_size = 8
            
            # Test different address ranges
            test_sizes = [128, 256, 512, 1024, 2048, 4096]
            
            for size in test_sizes:
                try:
                    # Try reading beyond current size
                    addr_high = (size - chunk_size) >> 8
                    addr_low = (size - chunk_size) & 0xFF
                    
                    # Multiple read attempts with delays
                    for attempt in range(3):
                        try:
                            if size > 2048:  # Use 16-bit addressing
                                self.device.write_i2c_block_data(addr, addr_high, [addr_low])
                            else:  # Use 8-bit addressing
                                self.device.write_i2c_block_data(addr, addr_low, [])
                                
                            time.sleep(0.002)  # 2ms delay
                            chunk = self.device.read_i2c_block_data(addr, None, chunk_size)
                            
                            if chunk is not None:
                                data.extend(chunk)
                                break
                        except Exception:
                            if attempt < 2:
                                time.sleep(0.01)  # 10ms delay between attempts
                            
                except Exception:
                    return data
                    
            return data
            
        except Exception:
            return None
            
    def connect(self, eeprom_size, i2c_speed):
        """Connect to CH341 device"""
        try:
            self.logger.info("Attempting to connect to CH341 device...")
            
            # Initialize CH341 device
            try:
                self.device = CH341()
                # Set I2C speed (in kHz)
                speed_khz = i2c_speed["freq"] // 1000
                self.device.set_speed(speed_khz)
                time.sleep(0.05)  # 50ms delay after speed change
            except ConnectionError as e:
                self.logger.error(f"CH341 device not found: {str(e)}")
                return False
                
            # Store configuration
            self.eeprom_size = eeprom_size
            self.i2c_speed = i2c_speed
            self.connected = True
            
            self.logger.info(f"Connected to CH341 with {i2c_speed['name']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to CH341: {str(e)}")
            self.disconnect()
            return False
            
    def disconnect(self):
        """Disconnect from CH341 device"""
        try:
            if self.connected and self.device:
                # Release USB device
                self.device.dev = None
                self.device = None
                self.connected = False
                self.eeprom_addr = None
                self.logger.info("Disconnected from CH341")
            return True
        except Exception as e:
            self.logger.error(f"Failed to disconnect from CH341: {str(e)}")
            return False
            
    def detect_eeprom(self):
        """Detect connected EEPROM"""
        if not self.connected or not self.device:
            self.logger.error("Not connected to CH341")
            return None
            
        try:
            # Multiple detection attempts
            for attempt in range(3):
                # Scan for EEPROM devices
                found_addresses = self.scan_i2c_bus()
                
                if found_addresses:
                    # Update working address
                    self.eeprom_addr = found_addresses[0]
                    self.logger.info(f"Found EEPROM at address 0x{self.eeprom_addr:02X}")
                    
                    # Try to detect EEPROM type
                    detected_type = self.detect_eeprom_type(self.eeprom_addr)
                    if detected_type:
                        self.logger.info(f"Detected EEPROM type: {detected_type}")
                        # Get size from detected type
                        size = 0
                        if "32" in detected_type:
                            size = 4096
                        elif "16" in detected_type:
                            size = 2048
                        elif "08" in detected_type:
                            size = 1024
                        elif "04" in detected_type:
                            size = 512
                        elif "02" in detected_type:
                            size = 256
                        else:
                            size = 128
                            
                        return {
                            "type": detected_type,
                            "size": size,
                            "address": self.eeprom_addr
                        }
                
                if attempt < 2:
                    time.sleep(0.1)  # 100ms delay between attempts
                    
            self.logger.warning("Could not detect EEPROM type")
            return None
                
        except Exception as e:
            self.logger.error(f"Failed to detect EEPROM: {str(e)}")
            return None
            
    def read_eeprom(self):
        """Read EEPROM contents"""
        if not self.connected or not self.device:
            self.logger.error("Not connected to CH341")
            return None
            
        try:
            data = bytearray()
            chunk_size = 8  # Reduced chunk size for better reliability
            total_size = self.eeprom_size["bytes"]
            
            # Multiple detection attempts
            for attempt in range(3):
                # Test EEPROM presence before reading
                if self.device.detect(self.eeprom_addr):
                    break
                time.sleep(0.1)  # 100ms delay between attempts
            else:
                self.logger.error(f"EEPROM not responding at address 0x{self.eeprom_addr:02X}")
                return None
                
            # For larger EEPROMs (>2KB), we need to handle the high address byte
            use_16bit_addr = total_size > 2048
            
            # Read EEPROM in small chunks with proper delays
            for base_addr in range(0, total_size, chunk_size):
                try:
                    # Multiple read attempts for each chunk
                    for attempt in range(3):
                        try:
                            # Send current address with proper format
                            if use_16bit_addr:
                                # For 16-bit addressing
                                high_addr = (base_addr >> 8) & 0xFF
                                low_addr = base_addr & 0xFF
                                self.device.write_i2c_block_data(self.eeprom_addr, high_addr, [low_addr])
                            else:
                                # For 8-bit addressing
                                self.device.write_i2c_block_data(self.eeprom_addr, base_addr & 0xFF, [])
                            
                            time.sleep(0.002)  # 2ms delay after address write
                            
                            chunk = self.device.read_i2c_block_data(self.eeprom_addr, None, chunk_size)
                            if chunk is not None:
                                data.extend(chunk)
                                break
                        except Exception as e:
                            self.logger.debug(f"Read retry {attempt + 1} failed at 0x{base_addr:04X}: {str(e)}")
                            if attempt < 2:
                                time.sleep(0.01)  # 10ms delay between retries
                    else:
                        self.logger.error(f"Failed to read EEPROM at address 0x{base_addr:04X} after 3 retries")
                        return None
                        
                    time.sleep(0.001)  # 1ms delay between chunks
                    
                except Exception as e:
                    self.logger.error(f"Error reading at address 0x{base_addr:04X}: {str(e)}")
                    return None
                    
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to read EEPROM: {str(e)}")
            return None
            
    def write_eeprom(self, data):
        """Write data to EEPROM"""
        if not self.connected or not self.device:
            self.logger.error("Not connected to CH341")
            return False
            
        try:
            if len(data) > self.eeprom_size["bytes"]:
                self.logger.error(f"Data size ({len(data)} bytes) exceeds EEPROM size ({self.eeprom_size['bytes']} bytes)")
                return False
                
            # Multiple detection attempts
            for attempt in range(3):
                # Test EEPROM presence before writing
                if self.device.detect(self.eeprom_addr):
                    break
                time.sleep(0.1)  # 100ms delay between attempts
            else:
                self.logger.error(f"EEPROM not responding at address 0x{self.eeprom_addr:02X}")
                return False
                
            # Use the EEPROM's page size for writing
            page_size = min(self.eeprom_size["page_size"], 8)  # Limit to 8 bytes for reliability
            total_size = self.eeprom_size["bytes"]
            use_16bit_addr = total_size > 2048
            
            # Write EEPROM in pages
            for base_addr in range(0, len(data), page_size):
                # Calculate actual bytes to write
                chunk_size = min(page_size, len(data) - base_addr)
                chunk = data[base_addr:base_addr + chunk_size]
                
                try:
                    if use_16bit_addr:
                        high_addr = (base_addr >> 8) & 0xFF
                        low_addr = base_addr & 0xFF
                        addr_bytes = [high_addr, low_addr]
                    else:
                        addr_bytes = [base_addr & 0xFF]
                    
                    # Write page with retry
                    for retry in range(3):
                        try:
                            # Write address and data
                            self.device.write_i2c_block_data(self.eeprom_addr, addr_bytes[0], 
                                                           (addr_bytes[1:] if len(addr_bytes) > 1 else []) + list(chunk))
                            
                            time.sleep(0.005)  # 5ms write cycle delay
                            
                            # Verify written data
                            self.device.write_i2c_block_data(self.eeprom_addr, addr_bytes[0], addr_bytes[1:] if len(addr_bytes) > 1 else [])
                            time.sleep(0.002)  # 2ms delay before read
                            readback = self.device.read_i2c_block_data(self.eeprom_addr, None, chunk_size)
                            
                            if readback == list(chunk):
                                break
                        except Exception as e:
                            self.logger.debug(f"Write retry {retry + 1} failed at 0x{base_addr:04X}: {str(e)}")
                            if retry < 2:
                                time.sleep(0.01)  # 10ms delay between retries
                    else:
                        self.logger.error(f"Failed to verify write at address 0x{base_addr:04X}")
                        return False
                    
                except Exception as e:
                    self.logger.error(f"Error writing at address 0x{base_addr:04X}: {str(e)}")
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write EEPROM: {str(e)}")
            return False
            
    def erase_eeprom(self):
        """Erase EEPROM contents (fill with 0xFF)"""
        if not self.connected or not self.device:
            self.logger.error("Not connected to CH341")
            return False
            
        try:
            # Multiple detection attempts
            for attempt in range(3):
                # Test EEPROM presence before erasing
                if self.device.detect(self.eeprom_addr):
                    break
                time.sleep(0.1)  # 100ms delay between attempts
            else:
                self.logger.error(f"EEPROM not responding at address 0x{self.eeprom_addr:02X}")
                return False
                
            data = bytearray([0xFF] * self.eeprom_size["bytes"])
            return self.write_eeprom(data)
        except Exception as e:
            self.logger.error(f"Failed to erase EEPROM: {str(e)}")
            return False
            
    def verify_eeprom(self, expected_data):
        """Verify EEPROM contents match expected data"""
        if not self.connected or not self.device:
            self.logger.error("Not connected to CH341")
            return False, 0
            
        try:
            # Multiple detection attempts
            for attempt in range(3):
                # Test EEPROM presence before verifying
                if self.device.detect(self.eeprom_addr):
                    break
                time.sleep(0.1)  # 100ms delay between attempts
            else:
                self.logger.error(f"EEPROM not responding at address 0x{self.eeprom_addr:02X}")
                return False, 0
                
            current_data = self.read_eeprom()
            if not current_data:
                return False, 0
                
            if len(expected_data) > len(current_data):
                self.logger.error(f"Expected data size ({len(expected_data)} bytes) exceeds EEPROM size ({len(current_data)} bytes)")
                return False, 0
                
            for i in range(len(expected_data)):
                if expected_data[i] != current_data[i]:
                    return False, i
                    
            return True, 0
        except Exception as e:
            self.logger.error(f"Failed to verify EEPROM: {str(e)}")
            return False, 0