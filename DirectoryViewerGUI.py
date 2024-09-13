import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from MetadataRetriever import list_files_and_folders

BG_COLOR = "#D9E3F1"

def create_icon():
    icon = tk.PhotoImage(width=128, height=128)
    folder_color = "#FFD700"
    outline_color = "#DAA520"

    for x in range(128):
        for y in range(128):
            if (20 <= x <= 108) and (50 <= y <= 108):
                icon.put(folder_color, (x, y))
            if (20 <= x <= 64) and (20 <= y <= 50):
                icon.put(folder_color, (x, y))
            if (20 <= x <= 108 and (50 <= y <= 51 or 108 <= y <= 109)) or (
                20 <= y <= 50 and (20 <= x <= 21 or 63 <= x <= 64)):
                icon.put(outline_color, (x, y))

    return icon

class DirectoryListerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Directory Lister")
        icon_image = create_icon()
        self.root.iconphoto(True, icon_image)
        self.create_style()
        self.create_widgets()
        self.sort_reverse = False

    def create_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        # Normal state configuration
        style.configure("Treeview.Heading", background="#5B62F4", foreground="white", relief=tk.FLAT)

        # Hover state configuration (change hover background color to black)
        style.map("Treeview.Heading",
                  background=[("active", "#4F55C9")],
                  foreground=[("active", "white")])

        style.configure('Flat.Treeview', relief=tk.FLAT, background="#F0F5FA", foreground="#8599C8")
        # Define scrollbar style
        style.configure("Custom.Vertical.TScrollbar",
                        background="#8599C8",
                        troughcolor=BG_COLOR,
                        gripcount=0,
                        bordercolor=BG_COLOR,
                        darkcolor=BG_COLOR,
                        lightcolor=BG_COLOR)

        # Configure Checkbutton Style
        style.configure("TCheckbutton",
                        background=BG_COLOR,
                        foreground="#7668A6")

        # Configure Frame Style
        style.configure("TFrame",
                        background=BG_COLOR)

        # Set root background color
        self.root.configure(bg=BG_COLOR)

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10", style="TFrame")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        tk.Label(frame, text="Directory:", bg=BG_COLOR).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        self.dir_entry = ttk.Entry(frame, width=70)
        self.dir_entry.grid(row=0, column=0, padx=5, pady=0, columnspan=2)
        browse_button = tk.Button(frame, text="Browse", command=self.browse_directory, bg="#FFA500", fg="white", relief=tk.FLAT)
        browse_button.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
        parent_button = tk.Button(frame, text="Go to Parent Folder", command=self.go_to_parent_folder, bg="#007BFF",
                                  fg="white", relief=tk.FLAT)
        parent_button.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.hash_var = tk.BooleanVar()
        hash_check = ttk.Checkbutton(frame, text="Include File Hash", variable=self.hash_var, style="TCheckbutton")
        hash_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        self.subfolder_var = tk.BooleanVar(value=False)
        subfolder_check = ttk.Checkbutton(frame, text="Include Subfolders", variable=self.subfolder_var, style="TCheckbutton")
        subfolder_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)

        generate_button = tk.Button(frame, text="Generate Report", command=self.generate_report, bg="#43CC29", fg="white", relief=tk.FLAT)
        generate_button.grid(row=7, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        vsb = tk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side='right', fill='y')
        hsb = tk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side='bottom', fill='x')

        columns = {
            "Type": 85,
            "Path": 450,
            "Creation Date": 125,
            "Modification Date": 125,
            "Size": 75,
            "Hash (SHA-256)": 150
        }
        self.tree = ttk.Treeview(tree_frame, columns=list(columns.keys()), show="headings", style="Treeview", yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column_func(c))
            self.tree.column(col, width=columns[col], anchor="w")

        self.tree.pack(side='left', fill='both', expand=True)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_to_clipboard)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_treeview_select)
        self.tree.bind("<Return>", self.on_treeview_select)
        self.tree.bind("<BackSpace>", lambda event: self.go_to_parent_folder())


    def go_to_parent_folder(self):
        current_directory = self.dir_entry.get()
        parent_directory = os.path.dirname(current_directory)
        if os.path.isdir(parent_directory):
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, parent_directory)

            # Uncheck 'Include Subfolders' and 'Calculate Hash'
            self.subfolder_var.set(False)
            self.hash_var.set(False)

            # Generate report for the parent directory
            self.generate_report()
        else:
            messagebox.showerror("Error", "No parent directory available.")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            self.tree.focus_set()
            self.generate_report()

    def generate_report(self):
        directory = self.dir_entry.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", "Selected path is not a directory")
            return

        include_hash = self.hash_var.get()
        include_subfolders = self.subfolder_var.get()

        data = list_files_and_folders(directory, include_hash, include_subfolders)
        self.tree.delete(*self.tree.get_children())

        for row in data:
            self.tree.insert("", tk.END, values=row)

        # Select the first item if there are any items
        if self.tree.get_children():
            self.tree.selection_set(self.tree.get_children()[0])
            self.tree.focus(self.tree.get_children()[0])

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def copy_to_clipboard(self):
        column_index = int(self.tree.identify_column(self.context_menu_click_x).split('#')[1]) - 1
        selected_items = self.tree.selection()

        clipboard_text = ""
        if selected_items:
            if len(selected_items) == 1:
                item_values = self.tree.item(selected_items[0], "values")
                if len(item_values) > column_index:
                    clipboard_text = item_values[column_index] + "\n"
            else:
                clipboard_text = "\n".join(" | ".join(self.tree.item(item, "values")) for item in selected_items) + "\n"

        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_text.strip())
        self.root.update()

    def sort_column_func(self, column):
        self.sort_reverse = not self.sort_reverse

        items = [(self.tree.item(item)["values"], item) for item in self.tree.get_children()]
        items.sort(key=lambda x: x[0][self.tree["columns"].index(column)], reverse=self.sort_reverse)

        for index, (values, item) in enumerate(items):
            self.tree.move(item, "", index)

    def on_treeview_select(self, event):
        # Get the x and y coordinates of the mouse click
        x, y = event.x, event.y

        # Identify the row and column of the click
        row_id = self.tree.identify_row(y)
        col_id = self.tree.identify_column(x)

        if row_id:
            # Get the values of the clicked row
            item_values = self.tree.item(row_id, "values")

            # Identify which column contains the path. Assuming 'Path' is the second column (index 1)
            path_column_index = 1  # Adjust this index if 'Path' is in a different column

            # Check if the clicked column contains the path
            if col_id == f"#{path_column_index + 1}":
                directory_path = item_values[path_column_index]
                if os.path.isdir(directory_path):
                    self.dir_entry.delete(0, tk.END)  # Clear current entry
                    self.dir_entry.insert(0, directory_path)  # Update with new path
                    # Uncheck 'Include Subfolders' and 'Calculate Hash'
                    self.subfolder_var.set(False)
                    self.hash_var.set(False)
                    self.generate_report()

    def run(self):
        self.root.mainloop()
