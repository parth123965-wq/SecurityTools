import struct

"""
Security Logic: JPG End-Of-File (EOF) Steganography
---------------------------------------------------
JPEG files use lossy Discrete Cosine Transform (DCT) compression. Standard LSB manipulation in JPEG images
corrupts or loses embedded data when re-saved or decoded.
Therefore, a safe and standardized practical method for JPEG steganography appends binary payload data directly
after the JPEG End-Of-File marker `0xFFD9`.
Image viewers display the JPEG image normally (ignoring data after EOF marker), while our program can read
and extract the binary metadata payload intact.

Payload Structure Appended at EOF:
  [8 bytes MAGIC_HEADER ("JPEG_STG")]
  [1 byte ENCRYPTED_FLAG (0x01 if password protected, 0x00 if plain)]
  [4 bytes PAYLOAD_SIZE (uint32 big-endian)]
  [N bytes PAYLOAD]
  [8 bytes FOOTER_MAGIC ("END_JPEG")]
"""

MAGIC_HEADER_JPG = b"JPEG_STG"
FOOTER_MAGIC_JPG = b"END_JPEG"
FLAG_PLAIN = b"\x00"
FLAG_ENCRYPTED = b"\x01"
JPEG_EOF_MARKER = b"\xFF\xD9"

def encode_jpg_eof(image_path: str, payload: bytes, is_encrypted: bool, output_path: str):
    """
    Append stego payload safely after JPEG EOF marker.
    """
    with open(image_path, "rb") as f:
        jpg_bytes = f.read()

    # Verify JPEG structure
    eof_pos = jpg_bytes.rfind(JPEG_EOF_MARKER)
    if eof_pos == -1:
        raise ValueError("Selected file is not a valid JPEG image.")

    # Base image up to EOF marker (including 0xFFD9)
    base_jpg = jpg_bytes[:eof_pos + len(JPEG_EOF_MARKER)]

    flag = FLAG_ENCRYPTED if is_encrypted else FLAG_PLAIN
    payload_size = struct.pack(">I", len(payload))
    
    stego_block = (
        MAGIC_HEADER_JPG +
        flag +
        payload_size +
        payload +
        FOOTER_MAGIC_JPG
    )

    with open(output_path, "wb") as f:
        f.write(base_jpg + stego_block)

def decode_jpg_eof(image_path: str) -> tuple[bytes, bool]:
    """
    Extract payload appended after JPEG EOF marker.
    Returns: tuple of (payload_bytes, is_encrypted_flag)
    """
    with open(image_path, "rb") as f:
        jpg_bytes = f.read()

    footer_pos = jpg_bytes.rfind(FOOTER_MAGIC_JPG)
    if footer_pos == -1:
        raise ValueError("No hidden stego payload detected in this JPG image.")

    magic_pos = jpg_bytes.rfind(MAGIC_HEADER_JPG, 0, footer_pos)
    if magic_pos == -1:
        raise ValueError("Corrupted or invalid stego payload structure in JPG.")

    header_offset = magic_pos + len(MAGIC_HEADER_JPG)
    flag_byte = jpg_bytes[header_offset:header_offset+1]
    is_encrypted = (flag_byte == FLAG_ENCRYPTED)

    size_offset = header_offset + 1
    payload_size = struct.unpack(">I", jpg_bytes[size_offset:size_offset+4])[0]

    payload_start = size_offset + 4
    payload_bytes = jpg_bytes[payload_start:payload_start+payload_size]

    if len(payload_bytes) != payload_size:
        raise ValueError("Stego JPEG payload is corrupted or incomplete.")

    return payload_bytes, is_encrypted
