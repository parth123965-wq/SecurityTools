import struct
from PIL import Image

"""
Security Logic: PNG LSB (Least Significant Bit) Steganography
--------------------------------------------------------------
LSB Steganography works by altering the lowest order bit of image color values (RGB channels).
Since changing the LSB changes a pixel component value by at most 1 (e.g. 240 -> 241), the visual change is imperceptible to the human eye.

Binary Payload Layout:
  [8 bytes MAGIC_HEADER ("STEGO_PNG")]
  [1 byte ENCRYPTED_FLAG (0x01 if password protected, 0x00 if plain text)]
  [4 bytes PAYLOAD_LENGTH (uint32 big-endian)]
  [N bytes PAYLOAD]
"""

MAGIC_HEADER = b"STEG_PNG"  # 8 bytes
FLAG_PLAIN = b"\x00"
FLAG_ENCRYPTED = b"\x01"
HEADER_SIZE = len(MAGIC_HEADER) + 1 + 4  # 13 bytes total header overhead

def calculate_png_capacity(image_path: str) -> dict:
    """
    Calculate maximum byte capacity for secret payload inside PNG image.
    Each pixel has 3 usable color channels (R, G, B), each embedding 1 bit.
    Total usable bits = width * height * 3.
    Total usable bytes = (width * height * 3) // 8.
    """
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        width, height = img.size
        total_bits = width * height * 3
        total_bytes = total_bits // 8
        max_payload_bytes = max(0, total_bytes - HEADER_SIZE)
        return {
            "width": width,
            "height": height,
            "total_capacity_bytes": total_bytes,
            "max_payload_bytes": max_payload_bytes,
            "header_overhead_bytes": HEADER_SIZE
        }

def bytes_to_bits(data: bytes) -> str:
    """Convert bytes array to a string of '0' and '1' characters."""
    return ''.join(f'{b:08b}' for b in data)

def bits_to_bytes(bit_string: str) -> bytes:
    """Convert a string of '0' and '1' characters back to bytes array."""
    byte_list = [int(bit_string[i:i+8], 2) for i in range(0, len(bit_string), 8)]
    return bytes(byte_list)

def encode_lsb(image_path: str, payload: bytes, is_encrypted: bool, output_path: str):
    """
    Embed payload bytes into PNG image using LSB substitution.
    """
    capacity_info = calculate_png_capacity(image_path)
    if len(payload) > capacity_info["max_payload_bytes"]:
        raise ValueError(
            f"Payload size ({len(payload)} bytes) exceeds maximum capacity "
            f"({capacity_info['max_payload_bytes']} bytes) of selected image."
        )

    flag = FLAG_ENCRYPTED if is_encrypted else FLAG_PLAIN
    length_header = struct.pack(">I", len(payload))
    full_data = MAGIC_HEADER + flag + length_header + payload

    bit_sequence = bytes_to_bits(full_data)
    bit_index = 0
    total_bits = len(bit_sequence)

    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            if bit_index >= total_bits:
                break
            
            r, g, b = pixels[x, y]
            
            # Embed in R channel LSB
            if bit_index < total_bits:
                r = (r & ~1) | int(bit_sequence[bit_index])
                bit_index += 1
                
            # Embed in G channel LSB
            if bit_index < total_bits:
                g = (g & ~1) | int(bit_sequence[bit_index])
                bit_index += 1
                
            # Embed in B channel LSB
            if bit_index < total_bits:
                b = (b & ~1) | int(bit_sequence[bit_index])
                bit_index += 1
                
            pixels[x, y] = (r, g, b)
            
        if bit_index >= total_bits:
            break

    # Save as lossless PNG
    img.save(output_path, format="PNG")

def decode_lsb(image_path: str) -> tuple[bytes, bool]:
    """
    Extract embedded payload from LSB of PNG image.
    Returns: tuple of (payload_bytes, is_encrypted_flag)
    """
    img = Image.open(image_path).convert('RGB')
    pixels = img.load()
    width, height = img.size

    extracted_bits = []
    
    # Extract header bits first
    header_bits_needed = HEADER_SIZE * 8
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            extracted_bits.append(str(r & 1))
            if len(extracted_bits) == header_bits_needed:
                break
                
            extracted_bits.append(str(g & 1))
            if len(extracted_bits) == header_bits_needed:
                break
                
            extracted_bits.append(str(b & 1))
            if len(extracted_bits) == header_bits_needed:
                break
                
        if len(extracted_bits) >= header_bits_needed:
            break

    header_bytes = bits_to_bytes(''.join(extracted_bits[:header_bits_needed]))
    
    magic = header_bytes[:8]
    if magic != MAGIC_HEADER:
        raise ValueError("No hidden stego payload detected in this image.")
        
    flag_byte = header_bytes[8:9]
    is_encrypted = (flag_byte == FLAG_ENCRYPTED)
    
    payload_length = struct.unpack(">I", header_bytes[9:13])[0]
    total_payload_bits_needed = payload_length * 8
    
    # Extract remaining payload bits
    all_bits = []
    bits_read = 0
    total_target_bits = header_bits_needed + total_payload_bits_needed

    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            
            for ch in (r, g, b):
                if bits_read >= header_bits_needed:
                    all_bits.append(str(ch & 1))
                bits_read += 1
                if len(all_bits) == total_payload_bits_needed:
                    break
            if len(all_bits) == total_payload_bits_needed:
                break
        if len(all_bits) == total_payload_bits_needed:
            break

    if len(all_bits) < total_payload_bits_needed:
        raise ValueError("Stego image file appears truncated or corrupted.")

    payload_bytes = bits_to_bytes(''.join(all_bits))
    return payload_bytes, is_encrypted
