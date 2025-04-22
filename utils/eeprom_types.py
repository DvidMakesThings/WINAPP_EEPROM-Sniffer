"""EEPROM types, I2C speeds, addresses, addressing modes, timings, and manufacturer database"""

# EEPROM sizes for I2C EEPROMs (24Cxx series)
# Extracted and updated from chiplist.xml <I2C> section
EEPROM_SIZES = [
    {"name": "AT24C01 (1Kbit / 128 bytes)", "bits": 1024,    "bytes": 128,    "page_size": 1,   "addrtype": 0},
    {"name": "AT24RF08C (8Kbit / 1K bytes)",  "bits": 8192,    "bytes": 1024,   "page_size": 16,  "addrtype": 3},
    {"name": "24C01 (1Kbit / 128 bytes)",    "bits": 1024,    "bytes": 128,    "page_size": 8,   "addrtype": 1},
    {"name": "24C02 (2Kbit / 256 bytes)",    "bits": 2048,    "bytes": 256,    "page_size": 8,   "addrtype": 1},
    {"name": "24C04 (4Kbit / 512 bytes)",    "bits": 4096,    "bytes": 512,    "page_size": 16,  "addrtype": 2},
    {"name": "24C08 (8Kbit / 1K bytes)",     "bits": 8192,    "bytes": 1024,   "page_size": 16,  "addrtype": 3},
    {"name": "24C16 (16Kbit / 2K bytes)",   "bits": 16384,   "bytes": 2048,   "page_size": 16,  "addrtype": 4},
    {"name": "24C32 (32Kbit / 4K bytes)",   "bits": 32768,   "bytes": 4096,   "page_size": 32,  "addrtype": 5},
    {"name": "24C64 (64Kbit / 8K bytes)",   "bits": 65536,   "bytes": 8192,   "page_size": 32,  "addrtype": 5},
    {"name": "24C128 (128Kbit / 16K bytes)","bits": 131072,  "bytes": 16384,  "page_size": 64,  "addrtype": 5},
    {"name": "24C256 (256Kbit / 32K bytes)","bits": 262144,  "bytes": 32768,  "page_size": 64,  "addrtype": 5},
    {"name": "24C512 (512Kbit / 64K bytes)","bits": 524288,  "bytes": 65536,  "page_size": 128, "addrtype": 5},
    {"name": "24LC515 (512Kbit / 64K bytes)","bits": 524288,  "bytes": 65536,  "page_size": 64,  "addrtype": 5},
    {"name": "24C1024 (1Mbit / 128K bytes)","bits": 1048576, "bytes": 131072, "page_size": 256, "addrtype": 6},
    {"name": "24LC1025 (1Mbit / 128K bytes)","bits": 1048576, "bytes": 131072, "page_size": 128, "addrtype": 6},
    {"name": "24LC1026 (1Mbit / 128K bytes)","bits": 1048576, "bytes": 131072, "page_size": 128, "addrtype": 6},
    {"name": "M24M01 (1Mbit / 128K bytes)", "bits": 1048576, "bytes": 131072, "page_size": 256, "addrtype": 6},
    {"name": "M24M02 (2Mbit / 256K bytes)", "bits": 2097152, "bytes": 262144, "page_size": 256, "addrtype": 7},
    {"name": "24C2048 (2Mbit / 256K bytes)","bits": 2097152, "bytes": 262144, "page_size": 256, "addrtype": 7},
]

# I2C speeds
I2C_SPEEDS = [
    {"name": "20 kHz (Slowest)",      "freq": 20000},
    {"name": "50 kHz (Slow)",         "freq": 50000},
    {"name": "100 kHz (Standard)",    "freq": 100000},
    {"name": "400 kHz (Fast)",        "freq": 400000},
    {"name": "750 kHz (Fast+)",       "freq": 750000},
    {"name": "1 MHz (High-Speed)",    "freq": 1000000},
]

# Common EEPROM I2C addresses and their configurations
EEPROM_ADDRESSES = [
    {"address": 0x50, "description": "A0 = GND (0x50)"},
    {"address": 0x51, "description": "A0 = VCC (0x51)"},
    {"address": 0x52, "description": "A1 = GND, A0 = GND (0x52)"},
    {"address": 0x53, "description": "A1 = GND, A0 = VCC (0x53)"},
    {"address": 0x54, "description": "A1 = VCC, A0 = GND (0x54)"},
    {"address": 0x55, "description": "A1 = VCC, A0 = VCC (0x55)"},
    {"address": 0x56, "description": "A2 = GND, A1 = GND, A0 = GND (0x56)"},
    {"address": 0x57, "description": "A2 = GND, A1 = GND, A0 = VCC (0x57)"},
    {"address": 0x58, "description": "A2 = GND, A1 = VCC, A0 = GND (0x58)"},
    {"address": 0x59, "description": "A2 = GND, A1 = VCC, A0 = VCC (0x59)"},
    {"address": 0x5A, "description": "A2 = VCC, A1 = GND, A0 = GND (0x5A)"},
    {"address": 0x5B, "description": "A2 = VCC, A1 = GND, A0 = VCC (0x5B)"},
    {"address": 0x5C, "description": "A2 = VCC, A1 = VCC, A0 = GND (0x5C)"},
    {"address": 0x5D, "description": "A2 = VCC, A1 = VCC, A0 = VCC (0x5D)"},
]

# Address type definitions
ADDR_TYPES = {
    0: "Single byte addressing, no page writes",
    1: "Single byte addressing with page write support",
    2: "Two-bit slave address + 8-bit word address",
    3: "Three-bit slave address + 8-bit word address",
    4: "Four-bit slave address + 8-bit word address",
    5: "Static slave address + 16-bit word address",
    6: "Static slave address + 17-bit word address",
    7: "Static slave address + 18-bit word address",
}

# Timing parameters (typical EEPROM timings in microseconds)
TIMING_PARAMS = {
    "write_cycle": 5000,    # Time after write to become ready again
    "page_write": 5000,     # Typical time to write a full page
    "byte_write": 5000,     # Typical time to write a single byte
    "addr_setup": 100,      # Address setup time before clock
    "write_pulse": 100,     # Duration of the write pulse
    "read_cycle": 100       # Time to complete a read operation
}

# Manufacturer database
MANUFACTURERS = {
    "ATMEL": {
        "prefix": "AT24",
        "devices": ["24C01", "24C02", "24C04", "24C08", "24C16", "24C32", "24C64", "24C128", "24C256", "24C512", "24C1024"]
    },
    "MICROCHIP": {
        "prefix": "24LC",
        "devices": ["24LC01B", "24LC02B", "24LC04B", "24LC08B", "24LC16B", "24LC32A", "24LC64", "24LC128", "24LC256", "24LC512", "24LC1025"]
    },
    "ST": {
        "prefix": "M24",
        "devices": ["M24C01", "M24C02", "M24C04", "M24C08", "M24C16", "M24C32", "M24C64", "M24C128", "M24C256", "M24C512", "M24C1024"]
    },
    "ON_SEMI": {
        "prefix": "CAT24",
        "devices": ["CAT24C01", "CAT24C02", "CAT24C04", "CAT24C08", "CAT24C16", "CAT24C32", "CAT24C64", "CAT24C128", "CAT24C256", "CAT24C512"]
    },
    "ROHM": {
        "prefix": "BR24",
        "devices": ["BR24L01", "BR24L02", "BR24L04", "BR24L08", "BR24L16", "BR24G32", "BR24G64", "BR24G128", "BR24G256", "BR24G512"]
    }
}
