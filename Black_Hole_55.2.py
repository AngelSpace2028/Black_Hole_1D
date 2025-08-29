import binascii

# Compression mapping (31 values to 5-bit codes)
constants_map = {
    0: "00000", 256: "00001", 348: "00010", 512: "00011", 687: "00100",
    999: "00101", 1024: "00110", 1156: "00111", 1500: "01000", 1987: "01001",
    2048: "01010", 2555: "01011", 3000: "01100", 3567: "01101", 4000: "01110",
    4096: "01111", 4999: "10000", 5120: "10001", 6000: "10010", 6666: "10011",
    7000: "10100", 7500: "10101", 7777: "10110", 8000: "10111", 8500: "11000",
    8888: "11001", 9000: "11010", 9999: "11011", 10000: "11100", 11000: "11101",
    11136: "11110"
}

# Reverse mapping for decompression
mapping = {v: k for k, v in constants_map.items()}

def compress_block(block):
    """Compress a 25-bit block if possible."""
    if len(block) != 25:
        return "11111" + block  # Mark as uncompressed
    
    num = int(block, 2)
    if num in constants_map:
        return constants_map[num]  # Use 5-bit code
    
    return "11111" + block  # Mark as uncompressed

def decompress_block(block):
    """Decompress a block."""
    if len(block) == 5 and block in mapping:
        return format(mapping[block], "025b")  # Reconstruct from 5-bit code
    elif block.startswith("11111") and len(block) > 5:
        return block[5:]  # Return original data
    return block  # Return as-is

def compress_data(data):
    """Compress data one time."""
    blocks = [data[i:i+25] for i in range(0, len(data), 25)]
    compressed_blocks = []
    
    for block in blocks:
        compressed_blocks.append(compress_block(block))
    
    return "".join(compressed_blocks)

def decompress_data(data, original_bits):
    """Decompress data one time."""
    result = []
    i = 0
    
    while i < len(data):
        if i + 5 <= len(data) and data[i:i+5] == "11111":
            # Uncompressed block (5-bit header + 25-bit data)
            if i + 30 <= len(data):
                block = data[i:i+30]
                result.append(block[5:])
                i += 30
            else:
                # Handle partial block at end
                result.append(data[i+5:])
                break
        else:
            # Compressed block (5-bit code)
            if i + 5 <= len(data):
                block = data[i:i+5]
                result.append(decompress_block(block))
                i += 5
            else:
                # Handle trailing bits
                result.append(data[i:])
                break
    
    decompressed = "".join(result)
    
    # Trim to original length
    if len(decompressed) > original_bits:
        decompressed = decompressed[:original_bits]
    elif len(decompressed) < original_bits:
        decompressed = decompressed.ljust(original_bits, '0')
    
    return decompressed

def main():
    file_name = input("File name: ")
    
    if not file_name.endswith(".b"):
        # COMPRESSION MODE
        try:
            with open(file_name, "rb") as f:
                data = f.read()
            
            if not data:
                print("Empty file")
                return
            
            original_bits = len(data) * 8
            
            # Convert to binary string
            hex_data = binascii.hexlify(data)
            binary_data = bin(int(hex_data, 16))[2:].zfill(original_bits)
            
            # Compress one time
            compressed = compress_data(binary_data)
            
            # Prepare metadata
            orig_len_bin = format(original_bits, "032b")
            comp_len_bin = format(len(compressed), "032b")
            
            # Create output with metadata
            output_binary = f"1{orig_len_bin}{comp_len_bin}{compressed}"
            
            # Pad to complete bytes
            padding = (8 - len(output_binary) % 8) % 8
            output_binary += "0" * padding
            
            # Convert to bytes
            output_bytes = int(output_binary, 2).to_bytes(len(output_binary) // 8, byteorder="big")
            
            # Write compressed file
            with open(file_name + ".b", "wb") as f:
                f.write(output_bytes)
            
            print(f"Compressed: {len(data)} → {len(output_bytes)} bytes")
            
        except Exception as e:
            print(f"Compression error: {e}")
    
    else:
        # DECOMPRESSION MODE
        try:
            with open(file_name, "rb") as f:
                data = f.read()
            
            # Convert to binary string
            hex_data = binascii.hexlify(data)
            total_bits = len(data) * 8
            binary_data = bin(int(hex_data, 16))[2:].zfill(total_bits)
            
            # Extract metadata
            if len(binary_data) < 65:  # 1 + 32 + 32 = 65 bits minimum
                print("Invalid compressed file")
                return
            
            version = binary_data[0]
            orig_len = int(binary_data[1:33], 2)
            comp_len = int(binary_data[33:65], 2)
            
            # Get compressed data
            compressed_data = binary_data[65:65+comp_len]
            
            # Decompress one time
            decompressed = decompress_data(compressed_data, orig_len)
            
            # Convert back to bytes
            byte_length = (orig_len + 7) // 8
            output_bytes = int(decompressed, 2).to_bytes(byte_length, byteorder="big")
            
            # Write decompressed file
            output_filename = file_name[:-2] if file_name.endswith(".b") else file_name + ".dec"
            with open(output_filename, "wb") as f:
                f.write(output_bytes)
            
            print(f"Decompressed successfully: {len(data)} → {len(output_bytes)} bytes")
            
        except Exception as e:
            print(f"Decompression error: {e}")

if __name__ == "__main__":
    main()
