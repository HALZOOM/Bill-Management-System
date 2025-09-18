"""
The main function of the application.
It creates the Tk root window, instantiates the main app class, and starts the event loop.
"""

import tkinter as tk
from gui import BillApp


def main():
    root = tk.Tk()
    app = BillApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
