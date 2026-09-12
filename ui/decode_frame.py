import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from core import decode_lsb, decode_jpg_eof, decrypt_payload
from utils.validators import validate_image_file

class DecodeFrame(ctk.CTkFrame):
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
            text="🔓 Extract Hidden Data from Image (Decoder)",
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
            text="1. Select Stego-Image",
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
            height=180,
            fg_color="#121212",
            corner_radius=8,
            text_color="#777777"
        )
        self.preview_label.grid(row=2, column=0, padx=15, pady=10)

        # Image status label
        self.lbl_stego_info = ctk.CTkLabel(
            self.left_card,
            text="Status: Waiting for stego image...",
            font=ctk.CTkFont(size=12),
            text_color="#aaa"
        )
        self.lbl_stego_info.grid(row=3, column=0, padx=15, pady=5)

        # Decryption Passphrase Box
        pass_lbl = ctk.CTkLabel(
            self.left_card,
            text="Decryption Passphrase (if encrypted):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e0e0e0"
        )
        pass_lbl.grid(row=4, column=0, padx=15, pady=(10, 2), sticky="w")

        self.ent_passphrase = ctk.CTkEntry(
            self.left_card,
            placeholder_text="Enter passphrase if message is encrypted...",
            show="•",
            fg_color="#121212",
            border_color="#2d2d2d"
        )
        self.ent_passphrase.grid(row=5, column=0, padx=15, pady=(0, 10), sticky="ew")

        # Decode Action Button
        self.btn_decode = ctk.CTkButton(
            self.left_card,
            text="🔍 Extract Hidden Data",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#00e676",
            hover_color="#00c853",
            text_color="#000000",
            height=45,
            corner_radius=8,
            command=self.process_decoding
        )
        self.btn_decode.grid(row=6, column=0, padx=15, pady=(10, 20), sticky="ew")

        # Right Column: Extracted Message Display & Export Options
        self.right_card = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e1e1e", border_width=1, border_color="#2d2d2d")
        self.right_card.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="nsew")
        self.right_card.grid_columnconfigure(0, weight=1)
        self.right_card.grid_rowconfigure(1, weight=1)

        result_header = ctk.CTkFrame(self.right_card, fg_color="transparent")
        result_header.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        result_header.grid_columnconfigure(0, weight=1)

        result_title = ctk.CTkLabel(
            result_header,
            text="2. Extracted Payload Result",
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

        # Extracted Message Display Textbox
        self.txt_result = ctk.CTkTextbox(
            self.right_card,
            corner_radius=8,
            fg_color="#121212",
            border_width=1,
            border_color="#2d2d2d",
            font=ctk.CTkFont(size=13)
        )
        self.txt_result.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")

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

        self.log(f"Ready to extract data from {os.path.basename(file_path)}", "INFO")

    def process_decoding(self):
        if not self.selected_stego_path:
            messagebox.showwarning("Warning", "Please select a stego image first.")
            return

        self.log("Extracting stego payload from image...", "PROCESS")

        try:
            if self.image_format == "PNG":
                raw_payload, is_encrypted = decode_lsb(self.selected_stego_path)
            else:
                raw_payload, is_encrypted = decode_jpg_eof(self.selected_stego_path)

            if is_encrypted:
                passphrase = self.ent_passphrase.get().strip()
                if not passphrase:
                    messagebox.showwarning("Passphrase Required", "This payload is encrypted with AES. Please enter the passphrase.")
                    self.log("Payload is encrypted, but no passphrase was provided.", "WARNING")
                    return
                
                extracted_text = decrypt_payload(raw_payload, passphrase)
                self.log("Decrypted secret text using AES passphrase.", "SECURITY")
            else:
                extracted_text = raw_payload.decode('utf-8')
                self.log("Extracted unencrypted secret text.", "SUCCESS")

            self.extracted_text = extracted_text
            self.txt_result.delete("1.0", "end")
            self.txt_result.insert("1.0", extracted_text)
            self.btn_save_txt.configure(state="normal")

            messagebox.showinfo("Extraction Complete", f"Successfully extracted hidden data!\nSize: {len(raw_payload)} bytes")
            self.log(f"Data extraction complete. Payload length: {len(raw_payload)} bytes.", "SUCCESS")

        except Exception as e:
            messagebox.showerror("Extraction Error", f"Failed to extract or decrypt payload:\n{e}")
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
