import sys
import os

# Add root folder to system path to ensure seamless modular imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.app import TouristRouteApp

def main():
    """
    Main entry point for the Tourist Route Planner desktop application.
    Initializes the GUI and runs the event processing loop.
    """
    try:
        app = TouristRouteApp()
        app.mainloop()
    except Exception as e:
        print(f"Application crash occurred: {e}")
        # Standard fallback alert
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Application Crash",
            f"An unexpected error occurred during execution:\n{e}\n\n"
            "Please ensure you have installed the correct packages listed in requirements.txt:\n"
            "pip install -r requirements.txt"
        )

if __name__ == "__main__":
    main()
