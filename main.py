import tkinter as tk
from app.gui_view import MainApp

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()