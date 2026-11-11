"""
Smart Surplus Food Management System
DS through C - PBL project (GUI App)

HOW TO RUN:   python app.py

WHAT IS INSIDE THIS FILE (top to bottom):
  PART 1 - Data structures  (linked list, queue, priority queue)
  PART 2 - App logic        (add food, serve food, save and load)
  PART 3 - The window       (buttons, tables, pages)
"""

import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox


# =====================================================================
# PART 1 - DATA STRUCTURES
# =====================================================================

# ---------- LINKED LIST (used for the food inventory) ----------
# Think of a train. Every coach (node) holds some food and
# knows which coach is next. The "head" is the first coach.

class FoodNode:
    def __init__(self, name, qty):
        self.name = name      # food name, like "Rice"
        self.qty = qty        # how many plates
        self.next = None      # the next coach (None means this is the last one)


class FoodList:
    def __init__(self):
        self.head = None      # empty train at the start

    def find(self, name):
        """Walk along the train and look for this food."""
        node = self.head
        while node is not None:
            if node.name.lower() == name.lower():
                return node
            node = node.next
        return None

    def add(self, name, qty):
        """Add food. If it is already there, only add more plates."""
        node = self.find(name)
        if node is not None:
            node.qty = node.qty + qty
            return "updated"

        new_node = FoodNode(name, qty)
        if self.head is None:
            self.head = new_node          # first coach
        else:
            last = self.head
            while last.next is not None:  # go to the last coach
                last = last.next
            last.next = new_node          # attach the new coach at the end
        return "added"

    def remove(self, name):
        """Remove a food from the train."""
        previous = None
        node = self.head
        while node is not None:
            if node.name.lower() == name.lower():
                if previous is None:
                    self.head = node.next         # removing the first coach
                else:
                    previous.next = node.next     # skip over this coach
                return True
            previous = node
            node = node.next
        return False

    def to_list(self):
        """Make a normal list so the window can show it in a table."""
        items = []
        node = self.head
        while node is not None:
            items.append((node.name, node.qty))
            node = node.next
        return items


# ---------- REQUEST NODE (used by both queues) ----------

class RequestNode:
    def __init__(self, person, food, qty, priority):
        self.person = person      # who wants the food
        self.food = food          # which food
        self.qty = qty            # how many plates
        self.priority = priority  # 0 = normal, 1 = Critical, 2 = High, 3 = Medium
        self.next = None


# ---------- QUEUE (used for normal requests) ----------
# Think of a line at a ticket window. The person who comes first
# is served first (First Come, First Served).
# New people join at the REAR (back). Served people leave from the FRONT.

class NormalQueue:
    def __init__(self):
        self.front = None
        self.rear = None

    def enqueue(self, person, food, qty):
        """Join the line at the back."""
        node = RequestNode(person, food, qty, 0)
        if self.rear is None:             # line was empty
            self.front = node
            self.rear = node
        else:
            self.rear.next = node
            self.rear = node

    def dequeue(self):
        """Take the person at the front of the line."""
        if self.front is None:
            return None
        node = self.front
        self.front = node.next
        if self.front is None:            # line became empty
            self.rear = None
        return node

    def to_list(self):
        items = []
        node = self.front
        while node is not None:
            items.append((node.person, node.food, node.qty))
            node = node.next
        return items


# ---------- PRIORITY QUEUE (used for urgent requests) ----------
# Think of a hospital emergency room. The most serious patient is
# treated first, even if someone else came earlier.
# Smaller number = more urgent (1 = Critical, 2 = High, 3 = Medium).
# If two people have the same number, the one who came first goes first.

class UrgentQueue:
    def __init__(self):
        self.head = None

    def insert(self, person, food, qty, priority):
        """Put the request at the right place in the line."""
        node = RequestNode(person, food, qty, priority)

        # more urgent than everyone? then go to the very front
        if self.head is None or priority < self.head.priority:
            node.next = self.head
            self.head = node
            return

        # otherwise walk ahead until we find our place
        current = self.head
        while current.next is not None and current.next.priority <= priority:
            current = current.next
        node.next = current.next
        current.next = node

    def dequeue(self):
        """Take the most urgent request."""
        if self.head is None:
            return None
        node = self.head
        self.head = node.next
        return node

    def to_list(self):
        items = []
        node = self.head
        while node is not None:
            items.append((node.person, node.food, node.qty, node.priority))
            node = node.next
        return items


# =====================================================================
# PART 2 - APP LOGIC
# =====================================================================

# these three are the "brain" of the app
foods = FoodList()
normal_requests = NormalQueue()
urgent_requests = UrgentQueue()

PRIORITY_NAMES = {1: "Critical", 2: "High", 3: "Medium"}

# the app saves everything in this file, so data is still there next time
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


def save_data():
    """Write everything into data.json."""
    data = {
        "foods": foods.to_list(),
        "normal": normal_requests.to_list(),
        "urgent": urgent_requests.to_list(),
    }
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except OSError:
        pass  # if saving fails, the app still keeps working


def load_data():
    """Read data.json (if it exists) and fill the data structures."""
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        for name, qty in data["foods"]:
            foods.add(name, qty)
        for person, food, qty in data["normal"]:
            normal_requests.enqueue(person, food, qty)
        for person, food, qty, priority in data["urgent"]:
            urgent_requests.insert(person, food, qty, priority)
    except (OSError, ValueError, KeyError, TypeError):
        pass  # broken file? just start fresh


def serve_one():
    """
    Serve ONE request. Urgent requests always go first.
    Gives back two things: (kind, message)
      kind = "ok" (fully served), "partial" (some plates only),
             "fail" (food not available), "none" (no requests)
    """
    request = urgent_requests.dequeue()
    tag = "URGENT"
    if request is None:
        request = normal_requests.dequeue()
        tag = "NORMAL"
    if request is None:
        return "none", "No pending requests."

    food = foods.find(request.food)
    if food is None:
        return "fail", "[" + tag + "] " + request.person + " asked for " + request.food + " - not available. Request closed."

    # give what is asked, or whatever is left
    give = min(food.qty, request.qty)
    food.qty = food.qty - give
    food_name = food.name
    if food.qty == 0:
        foods.remove(food_name)       # stock finished, remove it from the list

    if give == request.qty:
        return "ok", "[" + tag + "] " + request.person + " got " + str(give) + " plates of " + food_name + "."
    return "partial", ("[" + tag + "] " + request.person + " wanted " + str(request.qty) +
                       " plates of " + food_name + " but only " + str(give) + " were left.")


# =====================================================================
# PART 3 - THE WINDOW
# =====================================================================

# colours of the app
GREEN_DARK = "#1b4332"
GREEN = "#2d6a4f"
GREEN_LIGHT = "#d8f3dc"
BG = "#f1f5f2"
WHITE = "#ffffff"
ORANGE = "#e76f51"
BLUE = "#2a6f97"
RED = "#c1121f"
GRAY = "#6c757d"
GOLD = "#e9a820"

FONT = "Segoe UI"


def make_button(parent, text, command, color=GREEN):
    """A flat coloured button."""
    return tk.Button(
        parent, text=text, command=command, bg=color, fg="white",
        activebackground=GREEN_DARK, activeforeground="white",
        relief="flat", borderwidth=0, cursor="hand2",
        font=(FONT, 10, "bold"), padx=16, pady=7,
    )


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Surplus Food Management System")
        self.geometry("1050x680")
        self.minsize(960, 620)
        self.configure(bg=BG)

        self.shown_foods = []                  # foods currently shown in the table
        self.status = tk.StringVar(value="Welcome! Add some food to begin.")

        self.setup_styles()
        self.build_status_bar()
        self.build_sidebar()
        self.build_pages()

        load_data()
        self.show_page("dashboard")
        self.refresh_all()

    # ------------------------------------------------------------
    # look and feel
    # ------------------------------------------------------------

    def setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", rowheight=28, font=(FONT, 10),
                        background=WHITE, fieldbackground=WHITE)
        style.configure("Treeview.Heading", font=(FONT, 10, "bold"),
                        background=GREEN, foreground="white")
        style.map("Treeview.Heading", background=[("active", GREEN_DARK)])
        style.map("Treeview", background=[("selected", GREEN_LIGHT)],
                  foreground=[("selected", "black")])

    def build_status_bar(self):
        tk.Label(self, textvariable=self.status, anchor="w", bg=WHITE, fg=GRAY,
                 font=(FONT, 9), padx=12, pady=5).pack(side="bottom", fill="x")

    def set_status(self, text):
        self.status.set(text)

    # ------------------------------------------------------------
    # left menu (sidebar)
    # ------------------------------------------------------------

    def build_sidebar(self):
        sidebar = tk.Frame(self, bg=GREEN_DARK, width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="SURPLUS FOOD\nMANAGER", bg=GREEN_DARK, fg="white",
                 font=(FONT, 15, "bold"), justify="left").pack(anchor="w", padx=20, pady=(28, 30))

        self.nav_buttons = {}
        menu = [("dashboard", "Dashboard"), ("inventory", "Food Inventory"),
                ("requests", "Requests"), ("serve", "Serve Food")]
        for key, label in menu:
            button = tk.Button(
                sidebar, text=label, command=lambda k=key: self.show_page(k),
                bg=GREEN_DARK, fg="white", activebackground=GREEN, activeforeground="white",
                relief="flat", borderwidth=0, cursor="hand2", anchor="w",
                font=(FONT, 11), padx=22, pady=12,
            )
            button.pack(fill="x")
            self.nav_buttons[key] = button

        # buttons at the bottom of the sidebar
        tk.Button(sidebar, text="Reset All Data", command=self.reset_all, bg=RED, fg="white",
                  activebackground=GREEN_DARK, activeforeground="white", relief="flat",
                  borderwidth=0, cursor="hand2", font=(FONT, 10, "bold"),
                  pady=8).pack(side="bottom", fill="x", padx=15, pady=(6, 18))
        tk.Button(sidebar, text="Load Sample Data", command=self.load_sample, bg=GREEN, fg="white",
                  activebackground=GREEN_DARK, activeforeground="white", relief="flat",
                  borderwidth=0, cursor="hand2", font=(FONT, 10, "bold"),
                  pady=8).pack(side="bottom", fill="x", padx=15)

    def show_page(self, key):
        """Show one page and light up its button in the menu."""
        self.pages[key].tkraise()
        for name, button in self.nav_buttons.items():
            button.config(bg=GREEN if name == key else GREEN_DARK)

    # ------------------------------------------------------------
    # small building blocks
    # ------------------------------------------------------------

    def page_title(self, parent, text):
        tk.Label(parent, text=text, bg=BG, fg=GREEN_DARK,
                 font=(FONT, 20, "bold")).pack(anchor="w", pady=(0, 12))

    def make_card(self, parent, title, color):
        card = tk.Frame(parent, bg=color, padx=20, pady=14)
        value = tk.Label(card, text="0", bg=color, fg="white", font=(FONT, 28, "bold"))
        value.pack(anchor="w")
        tk.Label(card, text=title, bg=color, fg="white", font=(FONT, 11)).pack(anchor="w")
        return card, value

    def make_table(self, parent, columns, widths):
        holder = tk.Frame(parent, bg=WHITE)
        tree = ttk.Treeview(holder, columns=columns, show="headings", height=8)
        for column, width in zip(columns, widths):
            tree.heading(column, text=column)
            tree.column(column, width=width, anchor="center")
        scroll = ttk.Scrollbar(holder, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)
        return holder, tree

    def make_log(self, parent, height):
        box = tk.Text(parent, height=height, state="disabled", wrap="word", bg=WHITE,
                      relief="flat", padx=10, pady=8, font=("Consolas", 10))
        box.tag_config("ok", foreground="#1b7f3b")
        box.tag_config("partial", foreground="#c76a00")
        box.tag_config("fail", foreground=RED)
        box.tag_config("none", foreground=GRAY)
        box.tag_config("info", foreground=BLUE)
        return box

    def write_log(self, text, kind="info"):
        """Write one line (with time) in both activity logs."""
        line = datetime.now().strftime("%H:%M:%S") + "   " + text + "\n"
        for box in (self.dash_log, self.serve_log):
            box.config(state="normal")
            box.insert("end", line, kind)
            box.see("end")
            box.config(state="disabled")

    # ------------------------------------------------------------
    # checking what the user typed
    # ------------------------------------------------------------

    def check_name(self, text, label):
        """Returns True if the text is OK, otherwise shows a message."""
        if text == "":
            messagebox.showwarning("Missing", label + " cannot be empty.")
            return False
        if len(text) > 30:
            messagebox.showwarning("Too long", label + " should be 30 letters or less.")
            return False
        return True

    def check_qty(self, text):
        """Returns the number of plates, or None if it is wrong."""
        try:
            qty = int(text)
        except ValueError:
            messagebox.showwarning("Wrong number", "Plates must be a whole number, like 10.")
            return None
        if qty <= 0:
            messagebox.showwarning("Wrong number", "Plates must be more than 0.")
            return None
        return qty

    # ------------------------------------------------------------
    # build all pages
    # ------------------------------------------------------------

    def build_pages(self):
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.pages = {}
        for key in ("dashboard", "inventory", "requests", "serve"):
            page = tk.Frame(self.content, bg=BG, padx=26, pady=20)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[key] = page

        self.build_dashboard(self.pages["dashboard"])
        self.build_inventory(self.pages["inventory"])
        self.build_requests(self.pages["requests"])
        self.build_serve(self.pages["serve"])

    # ----- DASHBOARD PAGE -----

    def build_dashboard(self, page):
        self.page_title(page, "Dashboard")

        row = tk.Frame(page, bg=BG)
        row.pack(fill="x")
        card1, self.card_types = self.make_card(row, "Food types", GREEN)
        card2, self.card_plates = self.make_card(row, "Total plates", BLUE)
        card3, self.card_normal = self.make_card(row, "Normal requests", GOLD)
        card4, self.card_urgent = self.make_card(row, "Urgent requests", ORANGE)
        for card in (card1, card2, card3, card4):
            card.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(page, text="Quick actions", bg=BG, fg=GREEN_DARK,
                 font=(FONT, 13, "bold")).pack(anchor="w", pady=(22, 8))
        buttons = tk.Frame(page, bg=BG)
        buttons.pack(anchor="w")
        make_button(buttons, "Add Food", lambda: self.show_page("inventory")).pack(side="left", padx=(0, 10))
        make_button(buttons, "New Request", lambda: self.show_page("requests"), BLUE).pack(side="left", padx=(0, 10))
        make_button(buttons, "Serve Next Request", self.serve_next, ORANGE).pack(side="left")

        tk.Label(page, text="Recent activity", bg=BG, fg=GREEN_DARK,
                 font=(FONT, 13, "bold")).pack(anchor="w", pady=(22, 8))
        self.dash_log = self.make_log(page, 9)
        self.dash_log.pack(fill="both", expand=True)

    # ----- INVENTORY PAGE -----

    def build_inventory(self, page):
        self.page_title(page, "Food Inventory")

        form = tk.Frame(page, bg=WHITE, padx=16, pady=14)
        form.pack(fill="x")
        tk.Label(form, text="Food name", bg=WHITE, font=(FONT, 10)).grid(row=0, column=0, sticky="w")
        tk.Label(form, text="Plates", bg=WHITE, font=(FONT, 10)).grid(row=0, column=1, sticky="w", padx=(14, 0))
        self.food_name = ttk.Entry(form, width=28, font=(FONT, 11))
        self.food_name.grid(row=1, column=0, pady=(4, 0))
        self.food_qty = ttk.Entry(form, width=10, font=(FONT, 11))
        self.food_qty.grid(row=1, column=1, padx=(14, 0), pady=(4, 0))
        make_button(form, "Add Food", self.add_food).grid(row=1, column=2, padx=(16, 0), pady=(4, 0))
        self.food_qty.bind("<Return>", lambda event: self.add_food())

        bar = tk.Frame(page, bg=BG)
        bar.pack(fill="x", pady=(16, 8))
        tk.Label(bar, text="Search:", bg=BG, font=(FONT, 10)).pack(side="left")
        self.search = ttk.Entry(bar, width=26, font=(FONT, 11))
        self.search.pack(side="left", padx=8)
        self.search.bind("<KeyRelease>", lambda event: self.refresh_inventory())
        make_button(bar, "Delete Selected", self.delete_food, RED).pack(side="right")

        holder, self.food_tree = self.make_table(page, ("No.", "Food", "Plates available"), (60, 300, 160))
        holder.pack(fill="both", expand=True)

    def add_food(self):
        name = self.food_name.get().strip()
        if not self.check_name(name, "Food name"):
            return
        qty = self.check_qty(self.food_qty.get().strip())
        if qty is None:
            return

        result = foods.add(name, qty)
        if result == "added":
            message = name + " added to the inventory."
        else:
            message = name + " was already there, so the plates were increased."
        self.write_log(message, "info")
        self.set_status(message)

        self.food_name.delete(0, "end")
        self.food_qty.delete(0, "end")
        self.food_name.focus()
        self.refresh_all()

    def delete_food(self):
        selected = self.food_tree.selection()
        if not selected:
            messagebox.showinfo("Select first", "Click on a food in the table first.")
            return
        position = self.food_tree.index(selected[0])
        name = self.shown_foods[position][0]
        if messagebox.askyesno("Delete", "Delete " + name + " from the inventory?"):
            foods.remove(name)
            self.write_log(name + " deleted from the inventory.", "info")
            self.set_status(name + " deleted.")
            self.refresh_all()

    # ----- REQUESTS PAGE -----

    def build_requests(self, page):
        self.page_title(page, "Requests")

        form = tk.Frame(page, bg=WHITE, padx=16, pady=14)
        form.pack(fill="x")

        tk.Label(form, text="Your name", bg=WHITE, font=(FONT, 10)).grid(row=0, column=0, sticky="w")
        tk.Label(form, text="Food wanted", bg=WHITE, font=(FONT, 10)).grid(row=0, column=1, sticky="w", padx=(14, 0))
        tk.Label(form, text="Plates", bg=WHITE, font=(FONT, 10)).grid(row=0, column=2, sticky="w", padx=(14, 0))
        self.req_person = ttk.Entry(form, width=20, font=(FONT, 11))
        self.req_person.grid(row=1, column=0, pady=(4, 0))
        self.req_food = ttk.Combobox(form, width=20, font=(FONT, 11))
        self.req_food.grid(row=1, column=1, padx=(14, 0), pady=(4, 0))
        self.req_qty = ttk.Entry(form, width=8, font=(FONT, 11))
        self.req_qty.grid(row=1, column=2, padx=(14, 0), pady=(4, 0))

        self.req_type = tk.StringVar(value="normal")
        type_row = tk.Frame(form, bg=WHITE)
        type_row.grid(row=2, column=0, columnspan=4, sticky="w", pady=(12, 0))
        for text, value in (("Normal request", "normal"), ("Urgent request", "urgent")):
            tk.Radiobutton(type_row, text=text, value=value, variable=self.req_type,
                           command=self.toggle_urgency, bg=WHITE, activebackground=WHITE,
                           font=(FONT, 10)).pack(side="left", padx=(0, 14))
        tk.Label(type_row, text="Urgency:", bg=WHITE, font=(FONT, 10)).pack(side="left")
        self.req_level = ttk.Combobox(type_row, values=["1 - Critical", "2 - High", "3 - Medium"],
                                      width=12, state="disabled", font=(FONT, 10))
        self.req_level.current(0)
        self.req_level.pack(side="left", padx=8)

        make_button(form, "Submit Request", self.add_request, BLUE).grid(row=1, column=3, padx=(16, 0), pady=(4, 0))

        tables = tk.Frame(page, bg=BG)
        tables.pack(fill="both", expand=True, pady=(16, 0))
        tables.grid_columnconfigure(0, weight=1)
        tables.grid_columnconfigure(1, weight=1)
        tables.grid_rowconfigure(1, weight=1)

        tk.Label(tables, text="Normal queue (first come, first served)", bg=BG, fg=GREEN_DARK,
                 font=(FONT, 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))
        tk.Label(tables, text="Urgent queue (most urgent first)", bg=BG, fg=GREEN_DARK,
                 font=(FONT, 11, "bold")).grid(row=0, column=1, sticky="w", padx=(12, 0), pady=(0, 6))

        holder1, self.normal_tree = self.make_table(tables, ("No.", "Person", "Food", "Plates"), (40, 100, 100, 60))
        holder1.grid(row=1, column=0, sticky="nsew")
        holder2, self.urgent_tree = self.make_table(tables, ("No.", "Person", "Food", "Plates", "Urgency"),
                                                    (40, 90, 90, 55, 80))
        holder2.grid(row=1, column=1, sticky="nsew", padx=(12, 0))

    def toggle_urgency(self):
        if self.req_type.get() == "urgent":
            self.req_level.config(state="readonly")
        else:
            self.req_level.config(state="disabled")

    def add_request(self):
        person = self.req_person.get().strip()
        food = self.req_food.get().strip()
        if not self.check_name(person, "Name"):
            return
        if not self.check_name(food, "Food"):
            return
        qty = self.check_qty(self.req_qty.get().strip())
        if qty is None:
            return

        if self.req_type.get() == "urgent":
            level = int(self.req_level.get()[0])
            urgent_requests.insert(person, food, qty, level)
            message = "Urgent request (" + PRIORITY_NAMES[level] + ") added for " + person + "."
        else:
            normal_requests.enqueue(person, food, qty)
            message = "Normal request added for " + person + "."
        self.write_log(message, "info")
        self.set_status(message)

        self.req_person.delete(0, "end")
        self.req_food.set("")
        self.req_qty.delete(0, "end")
        self.refresh_all()

    # ----- SERVE PAGE -----

    def build_serve(self, page):
        self.page_title(page, "Serve Food")
        tk.Label(page, text="Urgent requests are always served first. Then normal requests, in order.",
                 bg=BG, fg=GRAY, font=(FONT, 10)).pack(anchor="w", pady=(0, 12))

        buttons = tk.Frame(page, bg=BG)
        buttons.pack(anchor="w", pady=(0, 12))
        make_button(buttons, "Serve Next Request", self.serve_next, GREEN).pack(side="left", padx=(0, 10))
        make_button(buttons, "Serve All Requests", self.serve_all, BLUE).pack(side="left", padx=(0, 10))
        make_button(buttons, "Clear Log", self.clear_log, GRAY).pack(side="left")

        self.serve_log = self.make_log(page, 15)
        self.serve_log.pack(fill="both", expand=True)

    def serve_next(self):
        kind, message = serve_one()
        self.write_log(message, kind)
        self.set_status(message)
        self.refresh_all()

    def serve_all(self):
        count = 0
        while True:
            kind, message = serve_one()
            if kind == "none":
                break
            self.write_log(message, kind)
            count = count + 1
        if count == 0:
            self.write_log("No pending requests.", "none")
            self.set_status("No pending requests.")
        else:
            self.write_log("Done! " + str(count) + " requests served.", "info")
            self.set_status("Done! " + str(count) + " requests served.")
        self.refresh_all()

    def clear_log(self):
        for box in (self.dash_log, self.serve_log):
            box.config(state="normal")
            box.delete("1.0", "end")
            box.config(state="disabled")

    # ------------------------------------------------------------
    # sample data and reset
    # ------------------------------------------------------------

    def load_sample(self):
        for name, qty in (("Rice", 30), ("Dal", 20), ("Roti", 50), ("Paneer", 10)):
            foods.add(name, qty)
        normal_requests.enqueue("Ravi", "Rice", 10)
        normal_requests.enqueue("Sita", "Dal", 25)
        normal_requests.enqueue("Mohan", "Paneer", 5)
        urgent_requests.insert("Hospital", "Roti", 20, 1)
        urgent_requests.insert("Orphanage", "Rice", 15, 2)
        self.write_log("Sample data loaded.", "info")
        self.set_status("Sample data loaded. Try the Serve Food page!")
        self.refresh_all()

    def reset_all(self):
        if not messagebox.askyesno("Reset", "This deletes ALL food and requests. Are you sure?"):
            return
        foods.head = None
        normal_requests.front = None
        normal_requests.rear = None
        urgent_requests.head = None
        self.clear_log()
        self.set_status("Everything was reset.")
        self.refresh_all()

    # ------------------------------------------------------------
    # refresh: update every table and number from the data structures
    # ------------------------------------------------------------

    def refresh_all(self):
        self.refresh_inventory()
        self.refresh_requests()
        self.refresh_dashboard()
        self.req_food.config(values=[name for name, qty in foods.to_list()])
        save_data()

    def refresh_inventory(self):
        for item in self.food_tree.get_children():
            self.food_tree.delete(item)
        words = self.search.get().strip().lower()
        self.shown_foods = []
        for name, qty in foods.to_list():
            if words in name.lower():
                self.shown_foods.append((name, qty))
        number = 1
        for name, qty in self.shown_foods:
            self.food_tree.insert("", "end", values=(number, name, qty))
            number = number + 1

    def refresh_requests(self):
        for item in self.normal_tree.get_children():
            self.normal_tree.delete(item)
        for item in self.urgent_tree.get_children():
            self.urgent_tree.delete(item)

        number = 1
        for person, food, qty in normal_requests.to_list():
            self.normal_tree.insert("", "end", values=(number, person, food, qty))
            number = number + 1

        number = 1
        for person, food, qty, priority in urgent_requests.to_list():
            self.urgent_tree.insert("", "end", values=(number, person, food, qty, PRIORITY_NAMES[priority]))
            number = number + 1

    def refresh_dashboard(self):
        items = foods.to_list()
        self.card_types.config(text=str(len(items)))
        self.card_plates.config(text=str(sum(qty for name, qty in items)))
        self.card_normal.config(text=str(len(normal_requests.to_list())))
        self.card_urgent.config(text=str(len(urgent_requests.to_list())))


if __name__ == "__main__":
    App().mainloop()
