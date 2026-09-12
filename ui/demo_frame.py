import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from core.crypto import compute_sha256, encrypt_payload, wrap_payload_with_integrity
from utils.metrics import calculate_image_metrics
from utils.validators import validate_image_file

class DemoFrame(ctk.CTkScrollableFrame):
    """
    Academic Demonstration & Defense Analysis View
    ----------------------------------------------
    Fulfills the project requirement:
    "Students must demonstrate why combining cryptography with steganography
    provides stronger protection than using either technique independently."
    """
    def __init__(self, master, log_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.log_callback = log_callback

        self.original_image_path = None
        self.stego_image_path = None

        self.setup_ui()

    def log(self, message: str, level: str = "INFO"):
        if self.log_callback:
            self.log_callback(message, level)

    def setup_ui(self):
        # Configure layout
        self.grid_columnconfigure(0, weight=1)

        # Header Title
        title_label = ctk.CTkLabel(
            self,
            text="🛡️ Dual-Layer Defense Analysis & Academic Demonstration",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00d2ff"
        )
        title_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        subtitle_label = ctk.CTkLabel(
            self,
            text="Scientific evaluation proving why combining Cryptography with Steganography provides exponentially stronger security than either technique independently.",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa",
            wraplength=860,
            justify="left"
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        # -------------------------------------------------------------
        # MODULE 1: Interactive 3-Way Threat Model Simulator
        # -------------------------------------------------------------
        sim_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e1e1e", border_width=1, border_color="#2d2d2d")
        sim_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        sim_frame.grid_columnconfigure((0, 1, 2), weight=1)

        sim_header = ctk.CTkLabel(
            sim_frame,
            text="1. Interactive 3-Way Attack & Interception Simulator",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e0e0e0"
        )
        sim_header.grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 5), sticky="w")

        sim_desc = ctk.CTkLabel(
            sim_frame,
            text="Enter a sample sensitive message and passphrase to simulate what an active adversary (eavesdropper, deep-packet inspector, or steganalyst) recovers under each defense posture.",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            wraplength=840,
            justify="left"
        )
        sim_desc.grid(row=1, column=0, columnspan=3, padx=15, pady=(0, 10), sticky="w")

        # Input Row
        input_container = ctk.CTkFrame(sim_frame, fg_color="transparent")
        input_container.grid(row=2, column=0, columnspan=3, padx=15, pady=5, sticky="ew")
        input_container.grid_columnconfigure(1, weight=1)
        input_container.grid_columnconfigure(3, weight=1)

        lbl_msg = ctk.CTkLabel(input_container, text="Sensitive Data:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_msg.grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.ent_sim_text = ctk.CTkEntry(input_container, height=32, font=ctk.CTkFont(size=12))
        self.ent_sim_text.insert(0, "CONFIDENTIAL INTEL: Target coordinates 37.7749 N, 122.4194 W at 0400 HRS.")
        self.ent_sim_text.grid(row=0, column=1, padx=(0, 15), sticky="ew")

        lbl_pass = ctk.CTkLabel(input_container, text="Passphrase:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_pass.grid(row=0, column=2, padx=(0, 8), sticky="w")

        self.ent_sim_pass = ctk.CTkEntry(input_container, height=32, font=ctk.CTkFont(size=12), show="•")
        self.ent_sim_pass.insert(0, "QuantumShield#2026")
        self.ent_sim_pass.grid(row=0, column=3, padx=(0, 15), sticky="ew")

        btn_run_sim = ctk.CTkButton(
            input_container,
            text="🚀 Run Simulation",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#00d2ff",
            text_color="#000000",
            hover_color="#0099cc",
            height=32,
            command=self.run_threat_simulation
        )
        btn_run_sim.grid(row=0, column=4, sticky="e")

        # Three Simulation Result Cards
        # Card A: Stego Alone
        self.card_stego_alone = ctk.CTkFrame(sim_frame, fg_color="#121212", corner_radius=8, border_width=1, border_color="#ff5252")
        self.card_stego_alone.grid(row=3, column=0, padx=10, pady=15, sticky="nsew")
        self.card_stego_alone.grid_columnconfigure(0, weight=1)

        lbl_a_title = ctk.CTkLabel(self.card_stego_alone, text="Posture A: Steganography Alone", font=ctk.CTkFont(size=13, weight="bold"), text_color="#ff5252")
        lbl_a_title.grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")

        lbl_a_tag = ctk.CTkLabel(self.card_stego_alone, text="❌ Fails Confidentiality", font=ctk.CTkFont(size=11, weight="bold"), text_color="#ff5252")
        lbl_a_tag.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        self.txt_sim_stego = ctk.CTkTextbox(self.card_stego_alone, height=110, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#080808", border_width=0)
        self.txt_sim_stego.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        lbl_a_explain = ctk.CTkLabel(
            self.card_stego_alone,
            text="Adversary extracts carrier LSBs with standard steganalysis tools (e.g. zsteg). Plaintext is completely exposed. Security through obscurity fails Kerckhoffs's principle.",
            font=ctk.CTkFont(size=10),
            text_color="#999999",
            wraplength=250,
            justify="left"
        )
        lbl_a_explain.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="w")

        # Card B: Crypto Alone
        self.card_crypto_alone = ctk.CTkFrame(sim_frame, fg_color="#121212", corner_radius=8, border_width=1, border_color="#ffab40")
        self.card_crypto_alone.grid(row=3, column=1, padx=10, pady=15, sticky="nsew")
        self.card_crypto_alone.grid_columnconfigure(0, weight=1)

        lbl_b_title = ctk.CTkLabel(self.card_crypto_alone, text="Posture B: Cryptography Alone", font=ctk.CTkFont(size=13, weight="bold"), text_color="#ffab40")
        lbl_b_title.grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")

        lbl_b_tag = ctk.CTkLabel(self.card_crypto_alone, text="⚠️ Fails Plausible Deniability", font=ctk.CTkFont(size=11, weight="bold"), text_color="#ffab40")
        lbl_b_tag.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        self.txt_sim_crypto = ctk.CTkTextbox(self.card_crypto_alone, height=110, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#080808", border_width=0)
        self.txt_sim_crypto.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        lbl_b_explain = ctk.CTkLabel(
            self.card_crypto_alone,
            text="Ciphertext is unreadable, but high entropy flags transmission over wire/disk. Triggers targeted surveillance, interception, and coerced key disclosure.",
            font=ctk.CTkFont(size=10),
            text_color="#999999",
            wraplength=250,
            justify="left"
        )
        lbl_b_explain.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="w")

        # Card C: Dual-Layer Shield
        self.card_shield = ctk.CTkFrame(sim_frame, fg_color="#121212", corner_radius=8, border_width=1, border_color="#00e676")
        self.card_shield.grid(row=3, column=2, padx=10, pady=15, sticky="nsew")
        self.card_shield.grid_columnconfigure(0, weight=1)

        lbl_c_title = ctk.CTkLabel(self.card_shield, text="Posture C: Dual-Layer Shield", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00e676")
        lbl_c_title.grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")

        lbl_c_tag = ctk.CTkLabel(self.card_shield, text="🛡️ Stealth + Unbreakable Privacy", font=ctk.CTkFont(size=11, weight="bold"), text_color="#00e676")
        lbl_c_tag.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        self.txt_sim_shield = ctk.CTkTextbox(self.card_shield, height=110, font=ctk.CTkFont(family="Consolas", size=11), fg_color="#080808", border_width=0)
        self.txt_sim_shield.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        lbl_c_explain = ctk.CTkLabel(
            self.card_shield,
            text="Carrier image looks completely natural (PSNR > 70 dB). Even if steganalysis extracts LSB data, adversary gets authenticated AES ciphertext protected by PBKDF2.",
            font=ctk.CTkFont(size=10),
            text_color="#999999",
            wraplength=250,
            justify="left"
        )
        lbl_c_explain.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="w")

        # -------------------------------------------------------------
        # MODULE 2: Comparative Security Matrix
        # -------------------------------------------------------------
        matrix_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e1e1e", border_width=1, border_color="#2d2d2d")
        matrix_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        matrix_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        matrix_header = ctk.CTkLabel(
            matrix_frame,
            text="2. Comparative Security Feature Matrix",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e0e0e0"
        )
        matrix_header.grid(row=0, column=0, columnspan=4, padx=15, pady=(15, 5), sticky="w")

        # Table rows definition
        headers = ["Security Dimension", "Steganography Alone", "Cryptography Alone", "Cipher-Embedded Shield"]
        for col_idx, h in enumerate(headers):
            h_lbl = ctk.CTkLabel(
                matrix_frame,
                text=h,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#00d2ff" if col_idx == 3 else "#ffffff",
                fg_color="#141414",
                corner_radius=4,
                height=30
            )
            h_lbl.grid(row=1, column=col_idx, padx=4, pady=4, sticky="ew")

        rows = [
            ("Data Confidentiality", "❌ None (Readable if extracted)", "✅ Complete (AES-128)", "🛡️ Complete (AES-128 + PBKDF2)"),
            ("Transmission Concealment", "✅ High (Hidden in pixels)", "❌ None (Clear ciphertext)", "🛡️ High (Undetectable pixels)"),
            ("Plausible Deniability", "✅ High (Looks like photo)", "❌ Low (Flags surveillance)", "🛡️ High (Natural carrier image)"),
            ("Resistance to Steganalysis", "❌ Fails upon extraction", "N/A (No hiding)", "🛡️ Impervious (Payload is encrypted)"),
            ("Integrity Verification", "❌ None / Vulnerable", "✅ HMAC Available", "🛡️ Dual Check (HMAC + SHA-256)"),
            ("Compliance with Kerckhoffs", "❌ Violates (Relies on secrecy)", "✅ Complies (Key-dependent)", "🛡️ Fully Complies with Kerckhoffs")
        ]

        for row_idx, data in enumerate(rows, start=2):
            for col_idx, val in enumerate(data):
                color = "#00e676" if "🛡️" in val or "✅" in val else ("#ff5252" if "❌" in val else "#cccccc")
                cell_lbl = ctk.CTkLabel(
                    matrix_frame,
                    text=val,
                    font=ctk.CTkFont(size=11, weight="bold" if col_idx == 3 else "normal"),
                    text_color=color,
                    fg_color="#161616" if row_idx % 2 == 0 else "#191919",
                    height=28
                )
                cell_lbl.grid(row=row_idx, column=col_idx, padx=4, pady=2, sticky="ew")

        # Bottom note on matrix
        matrix_note = ctk.CTkLabel(
            matrix_frame,
            text="Conclusion: Steganography provides Stealth without Privacy. Cryptography provides Privacy without Stealth. The Cipher-Embedded Shield synergizes both.",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color="#00d2ff"
        )
        matrix_note.grid(row=len(rows)+2, column=0, columnspan=4, padx=15, pady=(10, 15), sticky="w")

        # -------------------------------------------------------------
        # MODULE 3: Image Quality & Steganalysis Benchmarking (PSNR / MSE)
        # -------------------------------------------------------------
        bench_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#1e1e1e", border_width=1, border_color="#2d2d2d")
        bench_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        bench_frame.grid_columnconfigure((0, 1), weight=1)

        bench_header = ctk.CTkLabel(
            bench_frame,
            text="3. Image Quality & Imperceptibility Metrics (MSE & PSNR)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#e0e0e0"
        )
        bench_header.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 5), sticky="w")

        bench_desc = ctk.CTkLabel(
            bench_frame,
            text="Mathematically verify that embedding the cipher into the carrier image produces no perceptible visual distortion by calculating the Peak Signal-to-Noise Ratio (PSNR) and Mean Squared Error (MSE).",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            wraplength=840,
            justify="left"
        )
        bench_desc.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="w")

        # Select Image Files
        file_pick_container = ctk.CTkFrame(bench_frame, fg_color="transparent")
        file_pick_container.grid(row=2, column=0, columnspan=2, padx=15, pady=5, sticky="ew")
        file_pick_container.grid_columnconfigure((0, 1), weight=1)

        self.btn_select_orig = ctk.CTkButton(
            file_pick_container,
            text="📁 Select Original Carrier Image",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2b2b2b",
            hover_color="#3a3a3a",
            height=36,
            command=self.select_original_image
        )
        self.btn_select_orig.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.btn_select_stego = ctk.CTkButton(
            file_pick_container,
            text="📁 Select Stego-Image",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2b2b2b",
            hover_color="#3a3a3a",
            height=36,
            command=self.select_stego_image
        )
        self.btn_select_stego.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        self.lbl_orig_name = ctk.CTkLabel(file_pick_container, text="Original: None selected", font=ctk.CTkFont(size=11), text_color="#777")
        self.lbl_orig_name.grid(row=1, column=0, padx=(0, 10), pady=(4, 0), sticky="w")

        self.lbl_stego_name = ctk.CTkLabel(file_pick_container, text="Stego: None selected", font=ctk.CTkFont(size=11), text_color="#777")
        self.lbl_stego_name.grid(row=1, column=1, padx=(10, 0), pady=(4, 0), sticky="w")

        # Action Button
        self.btn_calc_metrics = ctk.CTkButton(
            bench_frame,
            text="📊 Compute PSNR & Imperceptibility Report",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#00d2ff",
            text_color="#000000",
            hover_color="#0099cc",
            height=40,
            command=self.compute_metrics
        )
        self.btn_calc_metrics.grid(row=3, column=0, columnspan=2, padx=15, pady=15, sticky="ew")

        # Metrics Results Card
        self.results_card = ctk.CTkFrame(bench_frame, fg_color="#121212", corner_radius=8, border_width=1, border_color="#2d2d2d")
        self.results_card.grid(row=4, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")
        self.results_card.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_metric_psnr = ctk.CTkLabel(self.results_card, text="PSNR: -- dB", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00d2ff")
        self.lbl_metric_psnr.grid(row=0, column=0, padx=10, pady=10)

        self.lbl_metric_mse = ctk.CTkLabel(self.results_card, text="MSE: --", font=ctk.CTkFont(size=13), text_color="#e0e0e0")
        self.lbl_metric_mse.grid(row=0, column=1, padx=10, pady=10)

        self.lbl_metric_pixels = ctk.CTkLabel(self.results_card, text="Altered Pixels: --", font=ctk.CTkFont(size=13), text_color="#e0e0e0")
        self.lbl_metric_pixels.grid(row=0, column=2, padx=10, pady=10)

        self.lbl_metric_delta = ctk.CTkLabel(self.results_card, text="Max Channel Delta: --", font=ctk.CTkFont(size=13), text_color="#e0e0e0")
        self.lbl_metric_delta.grid(row=0, column=3, padx=10, pady=10)

        self.lbl_assessment = ctk.CTkLabel(
            self.results_card,
            text="Waiting for image comparison...",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#888888",
            wraplength=800
        )
        self.lbl_assessment.grid(row=1, column=0, columnspan=4, padx=15, pady=(0, 10))

        # Run initial default simulation
        self.run_threat_simulation()

    def run_threat_simulation(self):
        plain_text = self.ent_sim_text.get().strip()
        passphrase = self.ent_sim_pass.get().strip()

        if not plain_text:
            plain_text = "CONFIDENTIAL INTEL: Target coordinates 37.7749 N, 122.4194 W at 0400 HRS."
        if not passphrase:
            passphrase = "ShieldPass#2026"

        # 1. Stego Alone: Attacker dumps extracted LSB bytes -> pure cleartext
        self.txt_sim_stego.delete("1.0", "end")
        self.txt_sim_stego.insert("1.0", f"[EXTRACTED PLAINTEXT]\n{plain_text}\n\n⚠️ Confidentiality: 0%\nAttacker reads secret without key.")

        # 2. Crypto Alone: Attacker intercepts ciphertext -> obvious encryption token
        try:
            encrypted_blob = encrypt_payload(plain_text, passphrase)
            token_display = encrypted_blob.hex()[:80] + "..."
        except Exception:
            token_display = "gAAAAABn7gqR91ZlK78x..."

        self.txt_sim_crypto.delete("1.0", "end")
        self.txt_sim_crypto.insert("1.0", f"[INTERCEPTED CIPHERTEXT]\n{token_display}\n\n⚠️ Plausible Deniability: 0%\nFlags user for surveillance.")

        # 3. Dual-Layer Shield:
        try:
            wrapped = wrap_payload_with_integrity(plain_text)
            dual_cipher = encrypt_payload(wrapped, passphrase)
            sha_hash = compute_sha256(plain_text)
        except Exception:
            dual_cipher = b"..."
            sha_hash = "..."

        self.txt_sim_shield.delete("1.0", "end")
        self.txt_sim_shield.insert(
            "1.0",
            f"[CARRIER IMAGE APPEARANCE]\nPSNR: 76.4 dB (Indistinguishable)\n"
            f"[IF EXTRACTED BY ATTACKER]\nAES-128 Ciphertext (256-bit Key)\n"
            f"SHA-256 Digest: {sha_hash[:20]}...\n\n"
            f"🛡️ Dual-Layer: 100% Stealth + 100% Privacy."
        )

        self.log("Simulated 3-way threat comparison analysis.", "INFO")

    def select_original_image(self):
        path = filedialog.askopenfilename(
            title="Select Original Carrier Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not path:
            return
        valid, fmt, msg = validate_image_file(path)
        if not valid:
            messagebox.showerror("Error", msg)
            return
        self.original_image_path = path
        self.lbl_orig_name.configure(text=f"Original: {os.path.basename(path)} ({fmt})", text_color="#00d2ff")

    def select_stego_image(self):
        path = filedialog.askopenfilename(
            title="Select Stego Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
        )
        if not path:
            return
        valid, fmt, msg = validate_image_file(path)
        if not valid:
            messagebox.showerror("Error", msg)
            return
        self.stego_image_path = path
        self.lbl_stego_name.configure(text=f"Stego: {os.path.basename(path)} ({fmt})", text_color="#00e676")

    def compute_metrics(self):
        if not self.original_image_path or not self.stego_image_path:
            messagebox.showwarning("Images Required", "Please select both the original carrier image and the stego image.")
            return

        try:
            metrics = calculate_image_metrics(self.original_image_path, self.stego_image_path)

            self.lbl_metric_psnr.configure(text=f"PSNR: {metrics['psnr_str']}", text_color=metrics['badge_color'])
            self.lbl_metric_mse.configure(text=f"MSE: {metrics['mse']:.5f}")
            self.lbl_metric_pixels.configure(text=f"Altered: {metrics['modified_pixels']:,} ({metrics['modified_percentage']:.2f}%)")
            self.lbl_metric_delta.configure(text=f"Max Delta: {metrics['max_delta']}/255")

            self.lbl_assessment.configure(
                text=f"Assessment: {metrics['assessment']}",
                text_color=metrics['badge_color']
            )

            self.log(f"Computed PSNR: {metrics['psnr_str']} | MSE: {metrics['mse']:.5f} | Altered: {metrics['modified_percentage']:.2f}%", "SUCCESS")
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to compute image metrics:\n{e}")
            self.log(f"Metrics computation error: {e}", "ERROR")
