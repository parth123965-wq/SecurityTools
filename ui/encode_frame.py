import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from core import (
    encode_lsb,
    encode_jpg_eof,
    encrypt_payload,
    compute_sha256,
    wrap_payload_with_integrity
)
from utils.validators import validate_image_file, check_capacity

class EncodeFrame(ctk.CTkFrame):
    """
    Dual-Layer Steganographic Encoder
    --------------------------------
    Layer 1: Cryptographic Encryption (AES-128 Fernet + PBKDF2HMAC + SHA-256 Digest)
    Layer 2: Steganographic Concealment (Lossless 1-bit LSB or Safe JPG EOF)
    """
    def __init__(self, master, log_callback=None, nav_demo_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.log_callback = log_callback
        self.nav_demo_callback = nav_demo_callback
        
        self.selected_image_path = None
        self.image_format = None
        self.last_saved_stego_path = None
        
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
            text="🔒 Dual-Layer Encoder: Cipher-Embedded Steganography",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00d2ff"
        )
        title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")

        # Left Column: Image Selection & Details Card (Layer 2 Carrier)
        self.left_card = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e1e1e", border_width=1, border_color="#2d2d2d")
        self.left_card.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="nsew")
        self.left_card.grid_columnconfigure(0, weight=1)

        img_section_title = ctk.CTkLabel(
            self.left_card, 
            text="1. Carrier Image Selection (Layer 2)", 
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#e0e0e0"
        )
        img_section_title.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.btn_select_img = ctk.CTkButton(
            self.left_card,
            text="🖼️ Select Carrier PNG / JPG Image",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2b2b2b",
            hover_color="#3a3a3a",
            border_color="#00d2ff",
            border_width=1,
            height=40,
            command=self.select_image
        )
        self.btn_select_img.grid(row=1, column=0, padx=15, pady=10, sticky="ew")

        # Image preview box
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

        # Image details & algorithm display
        self.lbl_img_info = ctk.CTkLabel(
            self.left_card,
            text="Format: N/A | Algorithm: N/A",
            font=ctk.CTkFont(size=12),
            text_color="#aaa"
        )
        self.lbl_img_info.grid(row=3, column=0, padx=15, pady=4)

        # Capacity Progress Bar
        self.capacity_label = ctk.CTkLabel(
            self.left_card,
            text="Payload Capacity: 0% used",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#aaa"
        )
        self.capacity_label.grid(row=4, column=0, padx=15, pady=(8, 2), sticky="w")

        self.capacity_bar = ctk.CTkProgressBar(self.left_card, height=10, progress_color="#00e676")
        self.capacity_bar.grid(row=5, column=0, padx=15, pady=(0, 10), sticky="ew")
        self.capacity_bar.set(0.0)

        # Quick action / Quality analysis notice
        self.lbl_post_action = ctk.CTkLabel(
            self.left_card,
            text="🛡️ Dual-Layer: Encrypts first, then conceals in pixels.",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#00d2ff"
        )
        self.lbl_post_action.grid(row=6, column=0, padx=15, pady=(5, 15))

        # Right Column: Payload Text Input, Layer 1 Encryption & Integrity
        self.right_card = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e1e1e", border_width=1, border_color="#2d2d2d")
        self.right_card.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        self.right_card.grid_columnconfigure(0, weight=1)
        self.right_card.grid_rowconfigure(2, weight=1)

        text_section_title = ctk.CTkLabel(
            self.right_card,
            text="2. Sensitive Payload & Cryptographic Protection (Layer 1)",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#e0e0e0"
        )
        text_section_title.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        # Upload Text File bar
        file_input_frame = ctk.CTkFrame(self.right_card, fg_color="transparent")
        file_input_frame.grid(row=1, column=0, padx=15, pady=4, sticky="ew")
        file_input_frame.grid_columnconfigure(0, weight=1)

        lbl_input_type = ctk.CTkLabel(file_input_frame, text="Enter Secret Message or Import File:", font=ctk.CTkFont(size=12), text_color="#bbbbbb")
        lbl_input_type.grid(row=0, column=0, sticky="w")

        self.btn_import_file = ctk.CTkButton(
            file_input_frame,
            text="📂 Load .txt File",
            width=110,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="#2b2b2b",
            hover_color="#3a3a3a",
            command=self.import_txt_file
        )
        self.btn_import_file.grid(row=0, column=1, sticky="e")

        # Secret text area
        self.txt_secret = ctk.CTkTextbox(
            self.right_card,
            corner_radius=8,
            fg_color="#121212",
            border_width=1,
            border_color="#2d2d2d",
            font=ctk.CTkFont(size=13)
        )
        self.txt_secret.grid(row=2, column=0, padx=15, pady=8, sticky="nsew")
        self.txt_secret.bind("<KeyRelease>", self.on_text_change)

        # Integrity Hash Display Box
        hash_container = ctk.CTkFrame(self.right_card, fg_color="#141414", corner_radius=6)
        hash_container.grid(row=3, column=0, padx=15, pady=(0, 8), sticky="ew")
        hash_container.grid_columnconfigure(1, weight=1)

        lbl_hash_title = ctk.CTkLabel(hash_container, text="SHA-256 Hash:", font=ctk.CTkFont(size=11, weight="bold"), text_color="#888")
        lbl_hash_title.grid(row=0, column=0, padx=(8, 4), pady=4, sticky="w")

        self.lbl_sha_hash = ctk.CTkLabel(
            hash_container,
            text="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 (empty)",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color="#00d2ff"
        )
        self.lbl_sha_hash.grid(row=0, column=1, padx=4, pady=4, sticky="w")

        # Passphrase frame (Layer 1: AES-128-CBC + PBKDF2HMAC)
        pass_frame = ctk.CTkFrame(self.right_card, fg_color="transparent")
        pass_frame.grid(row=4, column=0, padx=15, pady=4, sticky="ew")
        pass_frame.grid_columnconfigure(1, weight=1)

        self.chk_encrypt = ctk.CTkCheckBox(
            pass_frame,
            text="Layer 1 AES Cipher:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00d2ff",
            command=self.toggle_passphrase_field
        )
        self.chk_encrypt.select()  # Checked by default for Dual-Layer Security
        self.chk_encrypt.grid(row=0, column=0, padx=(0, 10))

        self.ent_passphrase = ctk.CTkEntry(
            pass_frame,
            placeholder_text="Enter secret passphrase (PBKDF2HMAC 100k)...",
            show="•",
            state="normal",
            fg_color="#121212",
            border_color="#00d2ff"
        )
        self.ent_passphrase.grid(row=0, column=1, sticky="ew")

        # Process Action Button
        self.btn_encode = ctk.CTkButton(
            self.right_card,
            text="⚡ Encrypt & Conceal (Generate Stego-Image)",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#00d2ff",
            hover_color="#0099cc",
            text_color="#000000",
            height=45,
            corner_radius=8,
            command=self.process_encoding
        )
        self.btn_encode.grid(row=5, column=0, padx=15, pady=(10, 20), sticky="ew")

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Carrier Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not file_path:
            return
            
        valid, fmt, msg = validate_image_file(file_path)
        if not valid:
            messagebox.showerror("Invalid Image", msg)
            self.log(f"Image validation failed: {msg}", "ERROR")
            return
            
        self.selected_image_path = file_path
        self.image_format = fmt
        
        algo_text = "PNG 1-Bit LSB Embedding" if fmt == "PNG" else "JPG EOF Metadata Encapsulation"
        self.lbl_img_info.configure(
            text=f"Format: {fmt} | Algorithm: {algo_text}",
            text_color="#00d2ff"
        )
        
        # Display thumbnail preview
        try:
            pil_img = Image.open(file_path)
            pil_img.thumbnail((240, 160))
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
            self.preview_label.configure(image=ctk_img, text="")
        except Exception as e:
            self.log(f"Failed to render thumbnail: {e}", "WARNING")

        self.log(f"Loaded carrier image: {os.path.basename(file_path)} ({fmt})", "SUCCESS")
        self.update_capacity_meter()

    def import_txt_file(self):
        txt_path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not txt_path:
            return
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.txt_secret.delete("1.0", "end")
            self.txt_secret.insert("1.0", content)
            self.log(f"Imported {len(content.encode('utf-8'))} bytes from {os.path.basename(txt_path)}", "INFO")
            self.on_text_change()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read text file: {e}")

    def toggle_passphrase_field(self):
        if self.chk_encrypt.get() == 1:
            self.ent_passphrase.configure(state="normal", border_color="#00d2ff")
        else:
            self.ent_passphrase.configure(state="disabled", border_color="#2d2d2d")
            
    def on_text_change(self, event=None):
        secret_text = self.txt_secret.get("1.0", "end-1c")
        digest = compute_sha256(secret_text)
        self.lbl_sha_hash.configure(text=f"{digest[:32]}... ({digest[32:]})")
        self.update_capacity_meter()

    def update_capacity_meter(self, event=None):
        if not self.selected_image_path:
            return
            
        secret_text = self.txt_secret.get("1.0", "end-1c")
        # Estimate with integrity envelope overhead (~85 bytes) + Fernet encryption overhead (~100 bytes)
        estimated_bytes = len(secret_text.encode('utf-8')) + 185
        
        fits, msg, ratio = check_capacity(self.selected_image_path, self.image_format, estimated_bytes)
        
        ratio_norm = min(1.0, max(0.0, ratio / 100.0))
        self.capacity_bar.set(ratio_norm)
        
        if not fits:
            self.capacity_label.configure(text=f"⚠️ Capacity Exceeded: {ratio:.1f}%", text_color="#ff5252")
            self.capacity_bar.configure(progress_color="#ff5252")
        elif ratio > 80.0:
            self.capacity_label.configure(text=f"Capacity Used: {ratio:.1f}% (High)", text_color="#ffab40")
            self.capacity_bar.configure(progress_color="#ffab40")
        else:
            self.capacity_label.configure(text=f"Payload Capacity: {ratio:.1f}% used", text_color="#00e676")
            self.capacity_bar.configure(progress_color="#00e676")

    def process_encoding(self):
        if not self.selected_image_path:
            messagebox.showwarning("Warning", "Please select a carrier image first.")
            return

        secret_text = self.txt_secret.get("1.0", "end-1c").strip()
        if not secret_text:
            messagebox.showwarning("Warning", "Secret text payload cannot be empty.")
            return

        is_encrypted = (self.chk_encrypt.get() == 1)
        passphrase = self.ent_passphrase.get().strip()

        if is_encrypted and not passphrase:
            messagebox.showwarning("Warning", "Layer 1 encryption is enabled. Please enter a passphrase.")
            return

        # 1. Package payload with SHA-256 Integrity Envelope
        integrity_wrapped = wrap_payload_with_integrity(secret_text)
        orig_sha256 = compute_sha256(secret_text)

        # 2. Check Capacity
        estimated_size = len(integrity_wrapped) + (80 if is_encrypted else 0)
        fits, cap_msg, _ = check_capacity(self.selected_image_path, self.image_format, estimated_size)
        if not fits:
            messagebox.showerror("Capacity Limit Exceeded", cap_msg)
            self.log(cap_msg, "ERROR")
            return

        # 3. Layer 1: Cryptographic Encryption
        try:
            if is_encrypted:
                payload_bytes = encrypt_payload(integrity_wrapped, passphrase)
                self.log("Layer 1 applied: Payload encrypted with AES-128-CBC / Fernet and authenticated.", "SECURITY")
            else:
                payload_bytes = integrity_wrapped
                self.log("Payload packaged with SHA-256 integrity digest (Plain mode).", "INFO")
        except Exception as e:
            messagebox.showerror("Encryption Error", f"Layer 1 cryptographic failure: {e}")
            return

        # 4. Save dialog
        default_ext = ".png" if self.image_format == "PNG" else ".jpg"
        save_path = filedialog.asksaveasfilename(
            title="Save Stego-Image",
            defaultextension=default_ext,
            filetypes=[("PNG Image", "*.png"), ("JPG Image", "*.jpg")] if self.image_format == "PNG" else [("JPG Image", "*.jpg"), ("PNG Image", "*.png")]
        )
        if not save_path:
            return

        self.log(f"Layer 2 executing: Concealing {len(payload_bytes)} bytes into {self.image_format}...", "PROCESS")

        try:
            if self.image_format == "PNG":
                encode_lsb(self.selected_image_path, payload_bytes, is_encrypted, save_path)
            else:
                encode_jpg_eof(self.selected_image_path, payload_bytes, is_encrypted, save_path)

            self.last_saved_stego_path = save_path
            self.log(f"Stego-image generated successfully -> {os.path.basename(save_path)}", "SUCCESS")
            self.log(f"Embedded SHA-256 Checksum: {orig_sha256}", "SECURITY")

            messagebox.showinfo(
                "Shield Complete",
                f"Dual-Layer Stego Image Successfully Created!\n\n"
                f"File: {os.path.basename(save_path)}\n"
                f"Layer 1 (Cipher): {'AES-128 Fernet' if is_encrypted else 'None'}\n"
                f"Layer 2 (Stego): {self.image_format}\n"
                f"SHA-256 Digest: {orig_sha256[:24]}...\n\n"
                f"You can now analyze image quality metrics (PSNR/MSE) in the Defense Analysis tab."
            )
        except Exception as e:
            messagebox.showerror("Encoding Failed", f"An error occurred during steganography encoding:\n{e}")
            self.log(f"Encoding failed: {e}", "ERROR")
