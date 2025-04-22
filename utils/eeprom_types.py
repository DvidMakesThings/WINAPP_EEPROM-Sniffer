"""EEPROM types and I2C speeds definitions"""

# EEPROM sizes
EEPROM_SIZES = [
    {"name": "24C01 (1Kbit / 128 bytes)", "bits": 1024, "bytes": 128, "page_size": 8},
    {"name": "24C02 (2Kbit / 256 bytes)", "bits": 2048, "bytes": 256, "page_size": 8},
    {"name": "24C04 (4Kbit / 512 bytes)", "bits": 4096, "bytes": 512, "page_size": 16},
    {"name": "24C08 (8Kbit / 1K bytes)", "bits": 8192, "bytes": 1024, "page_size": 16},
    {"name": "24C16 (16Kbit / 2K bytes)", "bits": 16384, "bytes": 2048, "page_size": 16},
    {"name": "24C32 (32Kbit / 4K bytes)", "bits": 32768, "bytes": 4096, "page_size": 32},
    {"name": "24C64 (64Kbit / 8K bytes)", "bits": 65536, "bytes": 8192, "page_size": 32},
    {"name": "24C128 (128Kbit / 16K bytes)", "bits": 131072, "bytes": 16384, "page_size": 64},
    {"name": "24C256 (256Kbit / 32K bytes)", "bits": 262144, "bytes": 32768, "page_size": 64},
    {"name": "24C512 (512Kbit / 64K bytes)", "bits": 524288, "bytes": 65536, "page_size": 128},
    {"name": "24C1024 (1Mbit / 128K bytes)", "bits": 1048576, "bytes": 131072, "page_size": 128}
]

# I2C speeds
I2C_SPEEDS = [
    {"name": "20 kHz (Slowest)", "freq": 20000},
    {"name": "50 kHz (Slow)", "freq": 50000},
    {"name": "100 kHz (Standard)", "freq": 100000},
    {"name": "400 kHz (Fast)", "freq": 400000},
    {"name": "750 kHz (Fast+)", "freq": 750000}
]

# Common EEPROM I2C addresses
EEPROM_ADDRESSES = [
    {"address": 0x50, "description": "A0 = GND (0x50)"},
    {"address": 0x51, "description": "A0 = VCC (0x51)"},
    {"address": 0x52, "description": "A1 = GND, A0 = GND (0x52)"},
    {"address": 0x53, "description": "A1 = GND, A0 = VCC (0x53)"},
    {"address": 0x54, "description": "A1 = VCC, A0 = GND (0x54)"},
    {"address": 0x55, "description": "A1 = VCC, A0 = VCC (0x55)"},
    {"address": 0x56, "description": "A2 = GND, A1 = GND, A0 = GND (0x56)"},
    {"address": 0x57, "description": "A2 = GND, A1 = GND, A0 = VCC (0x57)"}
]