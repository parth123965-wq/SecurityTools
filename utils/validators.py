import os
from PIL import Image
from core.lsb_handler import calculate_png_capacity

def validate_image_file(file_path: str) -> tuple[bool, str, str]:
    """
    Validate selected file format.
    Returns: (is_valid, format_type, message)
    """
    if not os.path.exists(file_path):
        return False, "", "Selected file does not exist."
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.png']:
        try:
            with Image.open(file_path) as img:
                if img.format.upper() != 'PNG':
                    return False, "PNG", "File extension is .png but file format is invalid."
            return True, "PNG", "Valid PNG image loaded."
        except Exception as e:
            return False, "", f"Failed to open image: {str(e)}"
            
    elif ext in ['.jpg', '.jpeg']:
        try:
            with Image.open(file_path) as img:
                if img.format.upper() not in ['JPEG', 'MPO']:
                    return False, "JPG", "File extension is .jpg/.jpeg but file format is invalid."
            return True, "JPG", "Valid JPEG image loaded."
        except Exception as e:
            return False, "", f"Failed to open image: {str(e)}"
    else:
        return False, "", "Unsupported format. Please select a PNG or JPG image."

def check_capacity(image_path: str, format_type: str, text_length_bytes: int) -> tuple[bool, str, float]:
    """
    Check if text payload fits inside chosen image capacity.
    Returns: (fits, warning_message, ratio_percentage)
    """
    if format_type == "PNG":
        info = calculate_png_capacity(image_path)
        max_bytes = info["max_payload_bytes"]
        if max_bytes == 0:
            return False, "Image dimensions are too small to hold stego metadata header.", 100.0
        
        ratio = (text_length_bytes / max_bytes) * 100
        if text_length_bytes > max_bytes:
            return False, f"Payload ({text_length_bytes} B) exceeds max PNG capacity ({max_bytes} B).", min(100.0, ratio)
        return True, f"Payload fits cleanly ({text_length_bytes} B / {max_bytes} B - {ratio:.1f}% capacity used).", ratio
    else:
        # JPG EOF appending has virtually unconstrained byte capacity (up to file size limits)
        max_bytes = 10 * 1024 * 1024  # 10 MB practical ceiling
        ratio = (text_length_bytes / max_bytes) * 100
        if text_length_bytes > max_bytes:
            return False, f"Payload ({text_length_bytes} B) exceeds practical 10MB JPG ceiling.", 100.0
        return True, f"JPG Payload OK ({text_length_bytes} B appended safely).", ratio
