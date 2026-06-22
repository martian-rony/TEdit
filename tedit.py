import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk
import os

class Tedit:
    def __init__(self, root):
        self.root = root
        self.root.title("Untitled - Tedit")
        self.root.geometry("1100x700")

        self.colors = {
            "bg": "#1e1e1e",
            "fg": "#d4d4d4",
            "accent": "#37373d",
            "status_bg": "#007acc",
            "status_fg": "#ffffff",
            "cursor": "#ffffff",
            "keyword": "#569cd6",
            "string": "#ce9178",
            "comment": "#6a9955",
        }

        self.filename = None         
        self.tabs = []              
        self.setup_ui()
        self.bind_shortcuts()

    def setup_ui(self):
        self.root.configure(bg=self.colors["bg"])

        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N",
                              command=self.new_file)
        file_menu.add_command(label="Open", accelerator="Ctrl+O",
                              command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S",
                              command=self.save)
        file_menu.add_command(label="Save As", accelerator="Ctrl+Shift+S",
                              command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.menubar.add_cascade(label="Help", menu=help_menu)

        self.main_container = tk.Frame(self.root, bg=self.colors["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)


        self.create_tab()


        self.status_var = tk.StringVar()
        self.status_var.set(" Tedit | Ready")
        self.status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg=self.colors["status_bg"],
            fg=self.colors["status_fg"],
            anchor='w',
            font=("Segoe UI", 9),
            padx=10,
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)


    def create_tab(self, content=""):     
        frame = tk.Frame(self.notebook, bg=self.colors["bg"])

    
        text = tk.Text(
            frame,
            font=("Consolas", 13),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["cursor"],
            padx=10,
            pady=10,
            undo=True,
            borderwidth=0,
            highlightthickness=0,
        )
        text.pack(fill=tk.BOTH, expand=True)


        scrollbar = ttk.Scrollbar(frame, command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.configure(yscrollcommand=scrollbar.set)

   
        self.notebook.add(frame, text="Untitled")
        self.tabs.append(text)    

     
        if content:
            text.insert("1.0", content)

     
        self.apply_syntax_highlighting(text)

        text.bind("<Key>", self.on_content_changed)

        return text

    def new_file(self):
        self.create_tab()
        self.filename = None
        self.set_title()
        self.status_var.set(" Tedit | New File")

    def open_file(self):
        path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"),
                       ("Text Files", "*.txt"),
                       ("Python", "*.py")]
        )
        if not path:
            return
        with open(path, "r") as f:
            content = f.read()
        self.filename = path
        self.create_tab(content)
        self.notebook.select(self.notebook.tabs()[-1])
        self.set_title(self.filename)
        self.status_var.set(
            f" Tedit | Opened: {os.path.basename(path)}")

    def save(self):
        if not self.filename:
            self.save_as()
            return
        try:
            cur_tab_id = self.notebook.select()
            text_widget = self.tabs[self.notebook.index(cur_tab_id)]
            content = text_widget.get(1.0, tk.END).strip()
            with open(self.filename, "w") as f:
                f.write(content)
            self.status_var.set(" Tedit | File Saved")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    def save_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"),
                       ("Text Files", "*.txt"),
                       ("Python", "*.py")]
        )
        if not path:
            return
        self.filename = path
        self.save()
        self.set_title(self.filename)


    def bind_shortcuts(self):
        self.root.bind_all("<Control-n>", lambda e: self.new_file())
        self.root.bind_all("<Control-o>", lambda e: self.open_file())
        self.root.bind_all("<Control-s>", lambda e: self.save())
        self.root.bind_all("<Control-Shift-S>", lambda e: self.save_as())

    def on_content_changed(self, event=None):
        self.status_var.set(" Tedit | Modified*")
        cur_tab_id = self.notebook.select()
        text_widget = self.tabs[self.notebook.index(cur_tab_id)]
        self.apply_syntax_highlighting(text_widget)

    def set_title(self, name=None):
        title = f"{name} - Tedit" if name else "Untitled - Tedit"
        self.root.title(title)

    def show_about(self):
        messagebox.showinfo(
            "About Tedit",
            "Tedit v1.0\n\nA modernised, minimal text editor with tab support "
            "and simple syntax highlighting built with Python."
        )


    def apply_syntax_highlighting(self, widget):
        """Very simple Python syntax highlighting."""

        for tag in widget.tag_names():
            widget.tag_remove(tag, "1.0", tk.END)

        keywords = [
            "def", "class", "import", "from", "if", "else", "elif", "return",
            "try", "except", "finally", "for", "while", "with", "as", "pass",
            "break", "continue", "lambda", "yield", "global", "nonlocal",
            "assert", "raise"
        ]
        for kw in keywords:
            start = "1.0"
            while True:
                pos = widget.search(r"\b" + kw + r"\b", start,
                                    stopindex=tk.END, regexp=True)
                if not pos:
                    break
                end = f"{pos}+{len(kw)}c"
                widget.tag_add("keyword", pos, end)
                start = end
        widget.tag_config("keyword", foreground=self.colors["keyword"])

  
        start = "1.0"
        while True:
            pos = widget.search(r'"[^"\n]*"', start,
                                stopindex=tk.END, regexp=True)
            if not pos:
                break
            end = f"{pos}+{len(widget.get(pos, f'{pos} lineend'))}c"
            widget.tag_add("string", pos, end)
            start = end
        widget.tag_config("string", foreground=self.colors["string"])

        start = "1.0"
        while True:
            pos = widget.search(r"#.*", start,
                                stopindex=tk.END, regexp=True)
            if not pos:
                break
            line_end = widget.search("\n", pos, stopindex=tk.END)
            if not line_end:
                line_end = tk.END
            widget.tag_add("comment", pos, line_end)
            start = line_end
        widget.tag_config("comment", foreground=self.colors["comment"])

if __name__ == "__main__":
    root = tk.Tk()
    app = Tedit(root)
    root.mainloop()
