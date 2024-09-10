import tkinter as tk
from DirectoryViewerGUI import DirectoryListerGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = DirectoryListerGUI(root)
    app.run()
