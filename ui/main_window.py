import datetime
import customtkinter as ctk
from ui.encode_frame import EncodeFrame
from ui.decode_frame import DecodeFrame

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure Main Window
        self.title("ShieldStego - Information Security Practical Steganography Suite")
        self.geometry("1100x720")
        self.minsize(980, 640)

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
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#121212")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Logo / Header
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="🛡️ ShieldStego",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#00d2ff"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="PNG/JPG Steganography Tool",
            font=ctk.CTkFont(size=11),
            text_color="#777777"
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 25))

        # Navigation Buttons
        self.btn_nav_encode = ctk.CTkButton(
            self.sidebar_frame,
            text="🔒  Hide Data (Encoder)",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=8,
            fg_color="#00d2ff",
            text_color="#000000",
            hover_color="#0099cc",
            command=self.show_encode_tab
        )
        self.btn_nav_encode.grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        self.btn_nav_decode = ctk.CTkButton(
            self.sidebar_frame,
            text="🔓  Extract Data (Decoder)",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=8,
            fg_color="transparent",
            text_color="#ffffff",
            hover_color="#2b2b2b",
            command=self.show_decode_tab
        )
        self.btn_nav_decode.grid(row=3, column=0, padx=15, pady=8, sticky="ew")

        # Security Info / Credits Card at bottom of sidebar
        self.info_card = ctk.CTkFrame(self.sidebar_frame, fg_color="#1e1e1e", corner_radius=8)
        self.info_card.grid(row=5, column=0, padx=15, pady=20, sticky="ew")

        info_lbl = ctk.CTkLabel(
            self.info_card,
            text="🔒 Algorithms:\n• PNG: LSB 1-Bit Embed\n• JPG: Safe EOF Marker\n• Cipher: AES-128 Fernet",
            font=ctk.CTkFont(size=11),
            justify="left",
            text_color="#999999"
        )
        info_lbl.pack(padx=10, pady=10)

        # -------------------------------------------------------------
        # Main View Area (Right Container)
        # -------------------------------------------------------------
        self.main_container = ctk.CTkFrame(self, fg_color="#181818", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Instantiate Frames
        self.encode_frame = EncodeFrame(self.main_container, log_callback=self.log_message, fg_color="transparent")
        self.decode_frame = DecodeFrame(self.main_container, log_callback=self.log_message, fg_color="transparent")

        # Default View: Encode Frame
        self.encode_frame.grid(row=0, column=0, sticky="nsew")

        # -------------------------------------------------------------
        # Real-time Status Log Footer Drawer
        # -------------------------------------------------------------
        self.log_drawer = ctk.CTkFrame(self.main_container, height=120, fg_color="#121212", border_width=1, border_color="#2b2b2b")
        self.log_drawer.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.log_drawer.grid_columnconfigure(0, weight=1)

        log_header = ctk.CTkLabel(
            self.log_drawer,
            text="📋 Real-Time Security Log Console",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#888888"
        )
        log_header.grid(row=0, column=0, padx=10, pady=(5, 2), sticky="w")

        self.txt_log = ctk.CTkTextbox(
            self.log_drawer,
            height=80,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0a0a0a",
            text_color="#00e676",
            border_width=0
        )
        self.txt_log.grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")
        self.txt_log.configure(state="disabled")

        self.log_message("System initialized successfully. Ready for operations.", "SUCCESS")

    def show_encode_tab(self):
        self.decode_frame.grid_forget()
        self.encode_frame.grid(row=0, column=0, sticky="nsew")

        # Highlight sidebar buttons
        self.btn_nav_encode.configure(fg_color="#00d2ff", text_color="#000000")
        self.btn_nav_decode.configure(fg_color="transparent", text_color="#ffffff")

    def show_decode_tab(self):
        self.encode_frame.grid_forget()
        self.decode_frame.grid(row=0, column=0, sticky="nsew")

        # Highlight sidebar buttons
        self.btn_nav_decode.configure(fg_color="#00e676", text_color="#000000")
        self.btn_nav_encode.configure(fg_color="transparent", text_color="#ffffff")

    def log_message(self, message: str, level: str = "INFO"):
        """Format timestamped log messages to console drawer."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}\n"

        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", formatted)
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")
