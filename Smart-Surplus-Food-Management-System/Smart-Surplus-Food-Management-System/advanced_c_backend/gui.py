# Smart Surplus Food Management System - FRONTEND (Python Tkinter)
# DS through C - PBL project
#
# The GUI only takes input and shows output.
# All the data structures (linked list, queue, priority queue) are in backend.c

import ctypes
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# ---------- load the C library ----------

BASE = os.path.dirname(os.path.abspath(__file__))

if sys.platform.startswith("win"):
    LIB_NAME = "backend.dll"
elif sys.platform == "darwin":
    LIB_NAME = "backend.dylib"
else:
    LIB_NAME = "backend.so"

try:
    lib = ctypes.CDLL(os.path.join(BASE, LIB_NAME))
except OSError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "Backend not found",
        "Could not load " + LIB_NAME + ".\n\n"
        "Compile backend.c first by double-clicking build.bat (or see the README).",
    )
    sys.exit(1)

# tell Python the argument and return types of each C function
lib.add_food.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.add_food.restype = ctypes.c_int

lib.get_inventory.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.get_inventory.restype = None

lib.add_request.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int]
lib.add_request.restype = ctypes.c_int

lib.get_requests.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.get_requests.restype = None

lib.add_urgent_request.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
lib.add_urgent_request.restype = ctypes.c_int

lib.get_urgent_requests.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.get_urgent_requests.restype = None

lib.process_next.argtypes = [ctypes.c_char_p, ctypes.c_int]
lib.process_next.restype = ctypes.c_int

lib.clear_all.argtypes = []
lib.clear_all.restype = None

BUF_SIZE = 8192
PRIORITY_NAMES = {1: "Critical", 2: "High", 3: "Medium"}


def get_rows(func):
    """Call a C function that fills a text buffer and split it into rows."""
    buf = ctypes.create_string_buffer(BUF_SIZE)
    func(buf, BUF_SIZE)
    text = buf.value.decode("utf-8", errors="ignore").strip()
    if text == "":
        return []
    return [line.split("|") for line in text.split("\n")]


# ---------- the main window ----------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Surplus Food Management System")
        self.geometry("780x580")
        self.minsize(720, 540)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        tk.Label(
            self,
            text="Smart Surplus Food Management System",
            font=("Segoe UI", 16, "bold"),
            pady=10,
        ).pack()

        self.status = tk.StringVar(value="Ready")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.inventory_tab = ttk.Frame(notebook, padding=10)
        self.requests_tab = ttk.Frame(notebook, padding=10)
        self.serve_tab = ttk.Frame(notebook, padding=10)
        notebook.add(self.inventory_tab, text="  Inventory  ")
        notebook.add(self.requests_tab, text="  Requests  ")
        notebook.add(self.serve_tab, text="  Distribute Food  ")

        self.build_inventory_tab()
        self.build_requests_tab()
        self.build_serve_tab()

        tk.Label(self, textvariable=self.status, anchor="w", relief="sunken", padx=8).pack(
            fill="x", side="bottom"
        )

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.refresh()

    # ----- helpers -----

    def make_tree(self, parent, columns, widths, height=8):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        for col, w in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center")
        return tree

    def clean_text(self, value, label):
        """Check a text field. Returns the cleaned text or None if invalid."""
        value = value.strip()
        if value == "":
            messagebox.showwarning("Missing input", label + " cannot be empty.")
            return None
        if "|" in value:
            messagebox.showwarning("Invalid input", label + " cannot contain the | symbol.")
            return None
        if len(value.encode("utf-8")) > 29:
            messagebox.showwarning("Too long", label + " should be less than 30 characters.")
            return None
        return value

    def get_qty(self, value):
        """Check quantity. Returns an int or None if invalid."""
        try:
            qty = int(value)
        except ValueError:
            messagebox.showwarning("Invalid quantity", "Quantity must be a whole number.")
            return None
        if qty <= 0:
            messagebox.showwarning("Invalid quantity", "Quantity should be more than 0.")
            return None
        return qty

    # ----- inventory tab -----

    def build_inventory_tab(self):
        form = ttk.LabelFrame(self.inventory_tab, text="Add surplus food", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Food name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.food_name = ttk.Entry(form, width=25)
        self.food_name.grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Quantity (plates):").grid(row=0, column=2, sticky="w", padx=5)
        self.food_qty = ttk.Entry(form, width=10)
        self.food_qty.grid(row=0, column=3, padx=5)

        ttk.Button(form, text="Add Food", command=self.on_add_food).grid(row=0, column=4, padx=10)

        self.inventory_tree = self.make_tree(
            self.inventory_tab, ("Food", "Plates available"), (300, 150), height=14
        )
        self.inventory_tree.pack(fill="both", expand=True, pady=10)

    def on_add_food(self):
        name = self.clean_text(self.food_name.get(), "Food name")
        if name is None:
            return
        qty = self.get_qty(self.food_qty.get())
        if qty is None:
            return

        result = lib.add_food(name.encode("utf-8"), qty)
        if result == 1:
            self.status.set(name + " added to inventory")
        elif result == 2:
            self.status.set(name + " already existed, quantity increased")
        else:
            messagebox.showerror("Error", "Could not add food.")
            return

        self.food_name.delete(0, tk.END)
        self.food_qty.delete(0, tk.END)
        self.refresh()

    # ----- requests tab -----

    def build_requests_tab(self):
        form = ttk.LabelFrame(self.requests_tab, text="New request", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Your name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.req_person = ttk.Entry(form, width=20)
        self.req_person.grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Food:").grid(row=0, column=2, sticky="w", padx=5)
        self.req_food = ttk.Entry(form, width=20)
        self.req_food.grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Plates:").grid(row=0, column=4, sticky="w", padx=5)
        self.req_qty = ttk.Entry(form, width=8)
        self.req_qty.grid(row=0, column=5, padx=5)

        self.req_type = tk.StringVar(value="normal")
        ttk.Radiobutton(
            form, text="Normal", variable=self.req_type, value="normal", command=self.toggle_priority
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        ttk.Radiobutton(
            form, text="Urgent", variable=self.req_type, value="urgent", command=self.toggle_priority
        ).grid(row=1, column=2, sticky="w", padx=5)

        ttk.Label(form, text="Urgency level:").grid(row=1, column=3, sticky="e", padx=5)
        self.req_priority = ttk.Combobox(
            form, values=["1 - Critical", "2 - High", "3 - Medium"], width=12, state="disabled"
        )
        self.req_priority.current(0)
        self.req_priority.grid(row=1, column=4, columnspan=2, sticky="w", padx=5)

        ttk.Button(form, text="Submit Request", command=self.on_add_request).grid(
            row=2, column=0, columnspan=6, pady=8
        )

        ttk.Label(self.requests_tab, text="Normal queue (first come first served)").pack(anchor="w")
        self.normal_tree = self.make_tree(
            self.requests_tab, ("Person", "Food", "Plates"), (200, 200, 100), height=6
        )
        self.normal_tree.pack(fill="x", pady=(0, 8))

        ttk.Label(self.requests_tab, text="Urgent queue (priority queue)").pack(anchor="w")
        self.urgent_tree = self.make_tree(
            self.requests_tab, ("Person", "Food", "Plates", "Urgency"), (180, 180, 80, 100), height=6
        )
        self.urgent_tree.pack(fill="x")

    def toggle_priority(self):
        if self.req_type.get() == "urgent":
            self.req_priority.config(state="readonly")
        else:
            self.req_priority.config(state="disabled")

    def on_add_request(self):
        person = self.clean_text(self.req_person.get(), "Name")
        if person is None:
            return
        food = self.clean_text(self.req_food.get(), "Food")
        if food is None:
            return
        qty = self.get_qty(self.req_qty.get())
        if qty is None:
            return

        if self.req_type.get() == "urgent":
            level = int(self.req_priority.get()[0])
            result = lib.add_urgent_request(person.encode("utf-8"), food.encode("utf-8"), qty, level)
            self.status.set("Urgent request added for " + person)
        else:
            result = lib.add_request(person.encode("utf-8"), food.encode("utf-8"), qty)
            self.status.set("Normal request added for " + person)

        if result != 1:
            messagebox.showerror("Error", "Could not add request.")
            return

        self.req_person.delete(0, tk.END)
        self.req_food.delete(0, tk.END)
        self.req_qty.delete(0, tk.END)
        self.refresh()

    # ----- distribute tab -----

    def build_serve_tab(self):
        ttk.Label(
            self.serve_tab,
            text="Urgent requests are always served first, then normal requests.",
        ).pack(anchor="w")

        ttk.Button(self.serve_tab, text="Serve Next Request", command=self.on_serve).pack(pady=10)

        self.log = tk.Text(self.serve_tab, height=18, state="disabled", wrap="word")
        self.log.pack(fill="both", expand=True)

    def on_serve(self):
        buf = ctypes.create_string_buffer(300)
        done = lib.process_next(buf, 300)
        message = buf.value.decode("utf-8", errors="ignore")

        self.log.config(state="normal")
        self.log.insert(tk.END, message + "\n")
        self.log.see(tk.END)
        self.log.config(state="disabled")

        if done == 0:
            messagebox.showinfo("Nothing to do", "There are no pending requests.")
        self.status.set(message)
        self.refresh()

    # ----- refresh all tables from the C backend -----

    def refresh(self):
        for tree in (self.inventory_tree, self.normal_tree, self.urgent_tree):
            for item in tree.get_children():
                tree.delete(item)

        for row in get_rows(lib.get_inventory):
            self.inventory_tree.insert("", tk.END, values=row)

        for row in get_rows(lib.get_requests):
            self.normal_tree.insert("", tk.END, values=row)

        for row in get_rows(lib.get_urgent_requests):
            row[3] = PRIORITY_NAMES.get(int(row[3]), row[3])
            self.urgent_tree.insert("", tk.END, values=row)

    def on_close(self):
        lib.clear_all()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
