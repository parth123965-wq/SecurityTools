import datetime
import customtkinter as ctk
from ui.encode_frame import EncodeFrame
from ui.decode_frame import DecodeFrame
from ui.demo_frame import DemoFrame

class MainWindow(ctk.CTk):
    """
    Cipher-Embedded Steganographic Shield
    ------------------------------------
    Main Desktop UI Shell coordinating:
    1. Dual-Layer Encoder (Cryptographic Cipher + Stego Concealment)
    2. Dual-Layer Decoder (Concealment Extraction + AES Decryption + SHA-256 Integrity Verification)
    3. Defense Analysis & Demonstration Module (Threat Simulator, Matrix, PSNR/MSE Quality Metrics)
    """
    def __init__(self):
        super().__init__()

        # Configure Main Window
        self.title("Cipher-Embedded Steganographic Shield — Dual-Layer Security Suite")
        self.geometry("1140x740")
        self.minsize(1020, 680)

        # Set Modern Dark Aesthetics
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.setup_ui_layout()

    def setup_ui_layout(self):
        # Configure Root Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # Left Navigation Sidebar
        # -------------------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color="#121212")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Logo / Header
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="🛡️ StegoShield",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#00d2ff"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 3))

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Cipher-Embedded Steganography\nDual-Layer Defense System",
            font=ctk.CTkFont(size=10),
            text_color="#888888",
            justify="center"
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Navigation Buttons
        self.btn_nav_encode = ctk.CTkButton(
            self.sidebar_frame,
            text="🔒  Dual-Layer Encoder",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=8,
            fg_color="#00d2ff",
            text_color="#000000",
            hover_color="#0099cc",
            command=self.show_encode_tab
        )
        self.btn_nav_encode.grid(row=2, column=0, padx=15, pady=6, sticky="ew")

        self.btn_nav_decode = ctk.CTkButton(
            self.sidebar_frame,
            text="🔓  Extractor & Decryptor",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=8,
            fg_color="transparent",
            text_color="#ffffff",
            hover_color="#2b2b2b",
            command=self.show_decode_tab
        )
        self.btn_nav_decode.grid(row=3, column=0, padx=15, pady=6, sticky="ew")

        self.btn_nav_demo = ctk.CTkButton(
            self.sidebar_frame,
            text="📊  Defense Analysis & Demo",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=8,
            fg_color="transparent",
            text_color="#ffffff",
            hover_color="#2b2b2b",
            command=self.show_demo_tab
        )
        self.btn_nav_demo.grid(row=4, column=0, padx=15, pady=6, sticky="ew")

        # Security Info / Credits Card at bottom of sidebar
        self.info_card = ctk.CTkFrame(self.sidebar_frame, fg_color="#1a1a1a", corner_radius=8)
        self.info_card.grid(row=6, column=0, padx=15, pady=20, sticky="ew")

        info_lbl = ctk.CTkLabel(
            self.info_card,
            text="🛡️ Dual-Layer Architecture:\n• Layer 1: AES-128 Fernet\n  + PBKDF2 (100k iter)\n  + SHA-256 Digest\n• Layer 2: PNG LSB / JPG EOF\n• Metrics: MSE & PSNR (dB)",
            font=ctk.CTkFont(size=11),
            justify="left",
            text_color="#aaaaaa"
        )
        info_lbl.pack(padx=10, pady=10)

        # -------------------------------------------------------------
        # Main View Area (Right Container)
        # -------------------------------------------------------------
        self.main_container = ctk.CTkFrame(self, fg_color="#181818", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # Real-time Status Log Footer Drawer (Created first so frames can log)
        # -------------------------------------------------------------
        self.log_drawer = ctk.CTkFrame(self.main_container, height=110, fg_color="#121212", border_width=1, border_color="#2b2b2b")
        self.log_drawer.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.log_drawer.grid_columnconfigure(0, weight=1)

        log_header = ctk.CTkLabel(
            self.log_drawer,
            text="📋 Real-Time Security Operations Console",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#888888"
        )
        log_header.grid(row=0, column=0, padx=10, pady=(4, 2), sticky="w")

        self.txt_log = ctk.CTkTextbox(
            self.log_drawer,
            height=70,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0a0a0a",
            text_color="#00e676",
            border_width=0
        )
        self.txt_log.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="ew")
        self.txt_log.configure(state="disabled")

        # -------------------------------------------------------------
        # Instantiate Feature Frames
        # -------------------------------------------------------------
        self.encode_frame = EncodeFrame(
            self.main_container,
            log_callback=self.log_message,
            nav_demo_callback=self.show_demo_tab,
            fg_color="transparent"
        )
        self.decode_frame = DecodeFrame(
            self.main_container,
            log_callback=self.log_message,
            fg_color="transparent"
        )
        self.demo_frame = DemoFrame(
            self.main_container,
            log_callback=self.log_message,
            fg_color="transparent"
        )

        # Default View: Encode Frame
        self.encode_frame.grid(row=0, column=0, sticky="nsew")

        self.log_message("Cipher-Embedded Steganographic Shield initialized. Ready.", "SYSTEM")

    def hide_all_frames(self):
        self.encode_frame.grid_forget()
        self.decode_frame.grid_forget()
        self.demo_frame.grid_forget()

    def show_encode_tab(self):
        self.hide_all_frames()
        self.encode_frame.grid(row=0, column=0, sticky="nsew")

        self.btn_nav_encode.configure(fg_color="#00d2ff", text_color="#000000")
        self.btn_nav_decode.configure(fg_color="transparent", text_color="#ffffff")
        self.btn_nav_demo.configure(fg_color="transparent", text_color="#ffffff")

    def show_decode_tab(self):
        self.hide_all_frames()
        self.decode_frame.grid(row=0, column=0, sticky="nsew")

        self.btn_nav_decode.configure(fg_color="#00e676", text_color="#000000")
        self.btn_nav_encode.configure(fg_color="transparent", text_color="#ffffff")
        self.btn_nav_demo.configure(fg_color="transparent", text_color="#ffffff")

    def show_demo_tab(self):
        self.hide_all_frames()
        self.demo_frame.grid(row=0, column=0, sticky="nsew")

        self.btn_nav_demo.configure(fg_color="#ffab40", text_color="#000000")
        self.btn_nav_encode.configure(fg_color="transparent", text_color="#ffffff")
        self.btn_nav_decode.configure(fg_color="transparent", text_color="#ffffff")

    def log_message(self, message: str, level: str = "INFO"):
        """Format timestamped log messages to console drawer."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}\n"

        if hasattr(self, "txt_log") and self.txt_log is not None:
            self.txt_log.configure(state="normal")
            self.txt_log.insert("end", formatted)
            self.txt_log.see("end")
            self.txt_log.configure(state="disabled")
