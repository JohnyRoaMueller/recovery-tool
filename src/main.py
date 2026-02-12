import tkinter as tk
from app.app import RecoveryApp

from pathlib import Path
from core.app_logging import setup_logging

def main() -> None:
    setup_logging(Path("logs"))
    root = tk.Tk()
    app = RecoveryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()