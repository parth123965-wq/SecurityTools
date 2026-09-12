import math
import os
from PIL import Image
import numpy as np

"""
Image Quality and Steganalysis Metrics
-------------------------------------
Computes mathematical distortion and imperceptibility metrics:
- Mean Squared Error (MSE)
- Peak Signal-to-Noise Ratio (PSNR in dB)
- Total and percentage of modified pixels
- Maximum color component delta (distortion threshold)
"""

def calculate_image_metrics(original_path: str, stego_path: str) -> dict:
    """
    Compare original carrier image and stego image.
    Returns dictionary with MSE, PSNR, modified pixels, and perceptual analysis.
    """
    if not os.path.exists(original_path) or not os.path.exists(stego_path):
        raise FileNotFoundError("One or both image paths do not exist.")

    with Image.open(original_path) as img1, Image.open(stego_path) as img2:
        img1_rgb = img1.convert("RGB")
        img2_rgb = img2.convert("RGB")

        if img1_rgb.size != img2_rgb.size:
            raise ValueError(
                f"Image dimensions do not match: Original is {img1_rgb.size}, "
                f"Stego is {img2_rgb.size}."
            )

        arr1 = np.array(img1_rgb, dtype=np.float64)
        arr2 = np.array(img2_rgb, dtype=np.float64)

        width, height = img1_rgb.size
        total_pixels = width * height
        total_channel_elements = total_pixels * 3

        # Channel-wise difference
        diff = arr1 - arr2
        abs_diff = np.abs(diff)
        squared_diff = diff ** 2

        # Mean Squared Error (MSE)
        mse = np.sum(squared_diff) / total_channel_elements

        # Peak Signal-to-Noise Ratio (PSNR)
        if mse == 0.0:
            psnr = float("inf")
            psnr_str = "Infinity (Bit-exact identical pixels)"
        else:
            psnr = 10.0 * math.log10((255.0 ** 2) / mse)
            psnr_str = f"{psnr:.2f} dB"

        # Modified pixel statistics
        pixel_diff_mask = np.any(arr1 != arr2, axis=2)
        modified_pixels = int(np.sum(pixel_diff_mask))
        modified_percentage = (modified_pixels / total_pixels) * 100.0 if total_pixels > 0 else 0.0

        max_delta = int(np.max(abs_diff)) if total_pixels > 0 else 0

        # Human Visual System (HVS) Perceptual Assessment
        if psnr == float("inf"):
            assessment = "Perfect Match: Zero pixel distortion (standard for JPG EOF appending)."
            badge_color = "#00e676"  # Green
        elif psnr >= 60.0:
            assessment = "Imperceptible: Modifications are mathematically invisible to the Human Visual System (HVS). Standard for high-grade steganography."
            badge_color = "#00e676"  # Green
        elif psnr >= 40.0:
            assessment = "Excellent Quality: Very minor noise, undetectable under normal human viewing."
            badge_color = "#00d2ff"  # Cyan
        elif psnr >= 30.0:
            assessment = "Moderate Quality: Slight artifacts may be visible under high magnification."
            badge_color = "#ffab40"  # Orange
        else:
            assessment = "Noticeable Distortion: Pixel changes exceed imperceptibility thresholds."
            badge_color = "#ff5252"  # Red

        return {
            "width": width,
            "height": height,
            "total_pixels": total_pixels,
            "mse": mse,
            "psnr": psnr,
            "psnr_str": psnr_str,
            "modified_pixels": modified_pixels,
            "modified_percentage": modified_percentage,
            "max_delta": max_delta,
            "assessment": assessment,
            "badge_color": badge_color
        }
