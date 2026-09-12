import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from core import (
    decode_lsb,
    decode_jpg_eof,
    decrypt_payload,
    unwrap_payload_with_integrity,
    compute_sha256
)
from utils.validators import validate_image_file

class DecodeFrame(ctk.CTkFrame):
    """
    Dual-Layer Steganographic Decoder & Verification View
    ----------------------------------------------------
    Step 1: Extract concealed payload from carrier image (PNG LSB or JPG EOF).
    Step 2: Decrypt AES-128 Fernet ciphertext using authorized passphrase.
    Step 3: Verify SHA-256 integrity checksum to guarantee data authenticity.
    """
    def __init__(self, master, log_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.log_callback = log_callback
        
        self.selected_stego_path = None
        self.image_format = None
        self.extracted_text = ""
        
        self.setup_ui()

    def log(self, message: str, level: str = "INFO"):
        if self.log_callback:
            self.log_callback(message, level)

    def setup_ui(self):
        # Configure Grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Title Header
        title = ctk.CTkLabel(
            self,
            text="🔓 Dual-Layer Decoder: Extraction, Decryption & Verification",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00e676"
        )
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # Left Column: Stego Image Input & Passphrase
        self.left_card = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e1e1e", border_width=1, border_color="#2d2d2d")
        self.left_card.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        self.left_card.grid_columnconfigure(0, weight=1)

        img_section_title = ctk.CTkLabel(
            self.left_card,
            text="1. Stego-Image Carrier Input",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#e0e0e0"
        )
        img_section_title.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.btn_select_stego = ctk.CTkButton(
            self.left_card,
            text="🖼️ Select Stego PNG / JPG Image",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2b2b2b",
            hover_color="#3a3a3a",
            border_color="#00e676",
            border_width=1,
            height=40,
            command=self.select_stego_image
        )
        self.btn_select_stego.grid(row=1, column=0, padx=15, pady=10, sticky="ew")

        # Preview thumbnail label
        self.preview_label = ctk.CTkLabel(
            self.left_card,
            text="No Image Selected",
            width=260,
            height=170,
            fg_color="#121212",
            corner_radius=8,
            text_color="#777777"
        )
        self.preview_label.grid(row=2, column=0, padx=15, pady=5)

        # Image status label
        self.lbl_stego_info = ctk.CTkLabel(
            self.left_card,
            text="Status: Waiting for stego image...",
            font=ctk.CTkFont(size=12),
            text_color="#aaa"
        )
        self.lbl_stego_info.grid(row=3, column=0, padx=15, pady=4)

        # Decryption Passphrase Box (Layer 1 Key)
        pass_lbl = ctk.CTkLabel(
            self.left_card,
            text="Decryption Passphrase (Layer 1 Cipher):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e0e0e0"
        )
        pass_lbl.grid(row=4, column=0, padx=15, pady=(8, 2), sticky="w")

        self.ent_passphrase = ctk.CTkEntry(
            self.left_card,
            placeholder_text="Enter passphrase if encrypted with AES...",
            show="•",
            fg_color="#121212",
            border_color="#2d2d2d"
        )
        self.ent_passphrase.grid(row=5, column=0, padx=15, pady=(0, 10), sticky="ew")

        # Decode Action Button
        self.btn_decode = ctk.CTkButton(
            self.left_card,
            text="🔍 Extract, Decrypt & Verify",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#00e676",
            hover_color="#00c853",
            text_color="#000000",
            height=45,
            corner_radius=8,
            command=self.process_decoding
        )
        self.btn_decode.grid(row=6, column=0, padx=15, pady=(5, 20), sticky="ew")

        # Right Column: Extracted Message Display, Verification Badge & Export
        self.right_card = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e1e1e", border_width=1, border_color="#2d2d2d")
        self.right_card.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        self.right_card.grid_columnconfigure(0, weight=1)
        self.right_card.grid_rowconfigure(2, weight=1)

        result_header = ctk.CTkFrame(self.right_card, fg_color="transparent")
        result_header.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        result_header.grid_columnconfigure(0, weight=1)

        result_title = ctk.CTkLabel(
            result_header,
            text="2. Extracted Payload & Integrity Verification",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#e0e0e0"
        )
        result_title.grid(row=0, column=0, sticky="w")

        self.btn_save_txt = ctk.CTkButton(
            result_header,
            text="💾 Save to .txt",
            width=110,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#2b2b2b",
            hover_color="#3a3a3a",
            state="disabled",
            command=self.save_to_file
        )
        self.btn_save_txt.grid(row=0, column=1, sticky="e")

        # Integrity Status Badge Card
        self.badge_card = ctk.CTkFrame(self.right_card, fg_color="#141414", corner_radius=8, border_width=1, border_color="#2b2b2b")
        self.badge_card.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        self.badge_card.grid_columnconfigure(0, weight=1)

        self.lbl_integrity_badge = ctk.CTkLabel(
            self.badge_card,
            text="Integrity Status: Awaiting extraction",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#888888"
        )
        self.lbl_integrity_badge.grid(row=0, column=0, padx=10, pady=(6, 2), sticky="w")

        self.lbl_integrity_details = ctk.CTkLabel(
            self.badge_card,
            text="SHA-256 Digest: --",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color="#777777"
        )
        self.lbl_integrity_details.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="w")

        # Extracted Message Display Textbox
        self.txt_result = ctk.CTkTextbox(
            self.right_card,
            corner_radius=8,
            fg_color="#121212",
            border_width=1,
            border_color="#2d2d2d",
            font=ctk.CTkFont(size=13)
        )
        self.txt_result.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="nsew")

    def select_stego_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Stego Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not file_path:
            return

        valid, fmt, msg = validate_image_file(file_path)
        if not valid:
            messagebox.showerror("Invalid File", msg)
            self.log(f"Stego image check failed: {msg}", "ERROR")
            return

        self.selected_stego_path = file_path
        self.image_format = fmt

        self.lbl_stego_info.configure(
            text=f"Loaded: {os.path.basename(file_path)} ({fmt})",
            text_color="#00e676"
        )

        try:
            pil_img = Image.open(file_path)
            pil_img.thumbnail((240, 160))
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
            self.preview_label.configure(image=ctk_img, text="")
        except Exception as e:
            self.log(f"Failed to render thumbnail preview: {e}", "WARNING")

        self.lbl_integrity_badge.configure(text="Integrity Status: Ready to extract and verify", text_color="#00d2ff")
        self.lbl_integrity_details.configure(text="SHA-256 Digest: --", text_color="#777")
        self.log(f"Carrier loaded: {os.path.basename(file_path)} ({fmt})", "INFO")

    def process_decoding(self):
        if not self.selected_stego_path:
            messagebox.showwarning("Warning", "Please select a stego image first.")
            return

        self.log("Step 1: Extracting concealed payload from image carrier...", "PROCESS")

        try:
            # Step 1: Extract payload from carrier
            if self.image_format == "PNG":
                raw_payload, is_encrypted = decode_lsb(self.selected_stego_path)
            else:
                raw_payload, is_encrypted = decode_jpg_eof(self.selected_stego_path)

            self.log(f"Concealed block extracted: {len(raw_payload)} bytes. Encrypted: {is_encrypted}", "INFO")

            # Step 2: Decrypt AES cipher if encrypted
            if is_encrypted:
                passphrase = self.ent_passphrase.get().strip()
                if not passphrase:
                    messagebox.showwarning("Passphrase Required", "Layer 1 is protected by AES-128 encryption. Please enter the passphrase.")
                    self.log("Payload is encrypted, but no passphrase was provided.", "WARNING")
                    return
                
                decrypted_bytes = decrypt_payload(raw_payload, passphrase)
                self.log("Step 2: Successfully decrypted AES-128 ciphertext using PBKDF2HMAC key.", "SECURITY")
                payload_to_verify = decrypted_bytes
            else:
                payload_to_verify = raw_payload
                self.log("Step 2: Unencrypted payload detected (Layer 1 was bypassed).", "INFO")

            # Step 3: Integrity Check (SHA-256 unwrap and comparison)
            content_bytes, computed_sha256, stored_sha256, is_verified = unwrap_payload_with_integrity(payload_to_verify)
            extracted_text = content_bytes.decode('utf-8', errors='replace')

            if is_verified:
                self.lbl_integrity_badge.configure(
                    text="✅ INTEGRITY VERIFIED: Bit-Exact Authentic (SHA-256 Matched)",
                    text_color="#00e676"
                )
                self.badge_card.configure(border_color="#00e676")
                self.log(f"Step 3: SHA-256 Integrity Verified ({computed_sha256[:16]}...)", "SUCCESS")
            else:
                self.lbl_integrity_badge.configure(
                    text="⚠️ INTEGRITY COMPROMISED: SHA-256 Checksum Mismatch!",
                    text_color="#ff5252"
                )
                self.badge_card.configure(border_color="#ff5252")
                self.log("Step 3: Integrity verification failed! Payload has been altered.", "ERROR")

            self.lbl_integrity_details.configure(
                text=f"SHA-256: {computed_sha256}\nStored:   {stored_sha256}",
                text_color="#aaaaaa"
            )

            self.extracted_text = extracted_text
            self.txt_result.delete("1.0", "end")
            self.txt_result.insert("1.0", extracted_text)
            self.btn_save_txt.configure(state="normal")

            messagebox.showinfo(
                "Extraction & Verification Complete",
                f"Dual-Layer Recovery Complete!\n\n"
                f"Payload Size: {len(extracted_text)} characters\n"
                f"Decryption: {'AES-128 Fernet (Verified)' if is_encrypted else 'None'}\n"
                f"Integrity Status: {'AUTHENTIC (Checksum match)' if is_verified else 'TAMPERED / MISMATCH'}"
            )

        except Exception as e:
            self.lbl_integrity_badge.configure(
                text="❌ EXTRACTION / DECRYPTION FAILED",
                text_color="#ff5252"
            )
            self.badge_card.configure(border_color="#ff5252")
            messagebox.showerror("Extraction Error", f"Failed to extract, decrypt, or verify payload:\n{e}")
            self.log(f"Extraction failed: {e}", "ERROR")

    def save_to_file(self):
        if not self.extracted_text:
            return

        save_path = filedialog.asksaveasfilename(
            title="Save Extracted Message",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.extracted_text)
            messagebox.showinfo("Saved", f"Extracted payload saved to:\n{os.path.basename(save_path)}")
            self.log(f"Exported extracted message to {os.path.basename(save_path)}", "SUCCESS")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save text file: {e}")
