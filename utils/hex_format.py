"""Intel HEX format utilities"""

def data_to_intel_hex(data, bytes_per_line=16):
    """Convert binary data to Intel HEX format
    
    Args:
        data (bytes or bytearray): Binary data to convert
        bytes_per_line (int): Number of bytes per line (default: 16)
        
    Returns:
        str: Intel HEX formatted string
    """
    lines = []
    
    for i in range(0, len(data), bytes_per_line):
        # Get chunk of data
        chunk = data[i:i + bytes_per_line]
        chunk_len = len(chunk)
        
        # Calculate checksum
        checksum = chunk_len  # Start with length byte
        checksum += (i >> 8) & 0xFF  # High byte of address
        checksum += i & 0xFF  # Low byte of address
        checksum += 0  # Record type (data)
        
        for b in chunk:
            checksum += b
            
        checksum = ((~checksum) + 1) & 0xFF  # Two's complement
        
        # Format line
        line = f":{chunk_len:02X}{i:04X}00"  # Start code, length, address, record type
        
        for b in chunk:
            line += f"{b:02X}"
            
        line += f"{checksum:02X}"  # Checksum
        lines.append(line)
        
    # Add end of file record
    lines.append(":00000001FF")
    
    return "\n".join(lines)

def intel_hex_to_data(hex_data):
    """Convert Intel HEX format to binary data
    
    Args:
        hex_data (str): Intel HEX formatted string
        
    Returns:
        bytearray: Binary data
    """
    data = bytearray()
    max_address = 0
    
    for line in hex_data.splitlines():
        line = line.strip()
        if not line:
            continue
            
        if line[0] != ':':
            raise ValueError(f"Invalid HEX line (missing start code): {line}")
            
        # Remove start code
        line = line[1:]
        
        # Parse line
        byte_count = int(line[0:2], 16)
        address = int(line[2:6], 16)
        record_type = int(line[6:8], 16)
        
        # End of file record
        if record_type == 1:
            break
            
        # Data record
        if record_type == 0:
            # Make sure data array is big enough
            if address + byte_count > max_address:
                max_address = address + byte_count
                if len(data) < max_address:
                    data.extend([0xFF] * (max_address - len(data)))
                    
            # Extract data bytes
            for i in range(byte_count):
                offset = 8 + i * 2
                byte = int(line[offset:offset + 2], 16)
                data[address + i] = byte
                
    return data