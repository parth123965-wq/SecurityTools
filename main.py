"""
ShieldStego Application Entry Point
------------------------------------
Starts the CustomTkinter Steganography Desktop Application inside the active Python virtual environment.
"""

from ui.main_window import MainWindow

def main():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
