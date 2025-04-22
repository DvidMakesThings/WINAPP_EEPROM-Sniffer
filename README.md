# EEPROM Programmer

A modern Python application for interfacing with a CH341 USB-to-I2C adapter to manage EEPROMs.

## Features

- Modern dark-themed GUI with intuitive EEPROM management controls
- CH341 USB adapter integration for I2C communication
- Hex dump and ASCII representation of EEPROM contents
- Intel HEX format support for importing and exporting data
- EEPROM detection with size/address suggestions
- Single-byte and full-chip operations (read, write, erase)
- Configurable I2C speed and EEPROM size settings

## Requirements

- Python 3.6+
- PyQt6
- pyusb
- pyserial

## Installation

1. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

## Application Structure

- `main.py` - Main application entry point
- `ui/` - GUI components and styling
- `hardware/` - CH341 communication interface
- `utils/` - Utility modules for data formatting and logging

## Developer Notes

This application uses a simulated CH341 interface for development purposes.
For actual hardware interfacing, the CH341 communication code in `hardware/ch341_manager.py` 
would need to be replaced with actual USB communication using pyusb.

## License

MIT License