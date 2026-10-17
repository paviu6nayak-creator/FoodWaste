import tkinter as tk
from tkinter import ttk, messagebox

from database import (
    create_table,
    add_record,
    get_records,
    delete_record,
    get_summary
)

from analytics import (
    show_category_chart,
    show_reason_chart
)

from insights import (
    get_insights,
    calculate_score
)


# --------------------------------------------------
# COLORS - BABY PINK & NUDE THEME
# --------------------------------------------------

BG = "#FFF7F4"          # Soft cream
SIDEBAR = "#F8DDE1"     # Baby pink
GREEN = "#D98F9A"       # Dusty rose
DARK_GREEN = "#A96873"  # Dark rose
WHITE = "#FFFFFF"       # White cards
TEXT = "#594B4B"        # Soft brown text
PEACH = "#E8C7B5"       # Nude / skin tone
LIGHT_GREEN = "#FCECEF" # Very light pink
RED = "#D77A7A"         # Soft red


# --------------------------------------------------
# MAIN WINDOW
# --------------------------------------------------

create_table()

root = tk.Tk()
root.title("FoodWise - Food Waste Tracker")
root.geometry("1150x700")
root.minsize(1000, 650)
root.configure(bg=BG)


# --------------------------------------------------
# STYLE
# --------------------------------------------------

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background=WHITE,
    foreground=TEXT,
    rowheight=35,
    fieldbackground=WHITE,
    font=("Segoe UI", 10)
)

style.configure(
    "Treeview.Heading",
    background=GREEN,
    foreground=WHITE,
    font=("Segoe UI", 10, "bold")
)

style.configure(
    "TCombobox",
    padding=8,
    font=("Segoe UI", 10)
)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()


def create_title(parent, title, subtitle):

    tk.Label(
        parent,
        text=title,
        font=("Segoe UI", 25, "bold"),
        bg=BG,
        fg=DARK_GREEN
    ).pack(anchor="w")

    tk.Label(
        parent,
        text=subtitle,
        font=("Segoe UI", 11),
        bg=BG,
        fg="#68736C"
    ).pack(anchor="w", pady=(3, 20))


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

def show_dashboard():

    clear_content()

    create_title(
        content_frame,
        "Good Evening! 👋",
        "Let's reduce today's food waste."
    )

    total_quantity, money_loss, records = get_summary()
    score = calculate_score()

    cards = tk.Frame(
        content_frame,
        bg=BG
    )

    cards.pack(fill="x")

    create_card(
        cards,
        "TOTAL WASTE",
        f"{total_quantity:.2f} kg",
        "🍱"
    )

    create_card(
        cards,
        "ESTIMATED LOSS",
        f"₹ {money_loss:.2f}",
        "💰"
    )

    create_card(
        cards,
        "WASTE RECORDS",
        str(records),
        "📋"
    )

    create_card(
        cards,
        "WASTE SCORE",
        f"{score}/100",
        "🌱"
    )

    # Insights section

    tk.Label(
        content_frame,
        text="Smart Insights",
        font=("Segoe UI", 18, "bold"),
        bg=BG,
        fg=DARK_GREEN
    ).pack(anchor="w", pady=(30, 10))

    insight_box = tk.Frame(
        content_frame,
        bg=WHITE,
        padx=20,
        pady=15
    )

    insight_box.pack(fill="x")

    for insight in get_insights():

        tk.Label(
            insight_box,
            text=insight,
            font=("Segoe UI", 11),
            bg=WHITE,
            fg=TEXT,
            anchor="w"
        ).pack(fill="x", pady=7)


def create_card(parent, title, value, icon):

    card = tk.Frame(
        parent,
        bg=WHITE,
        width=220,
        height=120
    )

    card.pack(
        side="left",
        padx=(0, 15),
        fill="both",
        expand=True
    )

    card.pack_propagate(False)

    tk.Label(
        card,
        text=icon,
        font=("Segoe UI Emoji", 20),
        bg=WHITE
    ).pack(anchor="w", padx=15, pady=(10, 0))

    tk.Label(
        card,
        text=title,
        font=("Segoe UI", 9, "bold"),
        bg=WHITE,
        fg="#78827A"
    ).pack(anchor="w", padx=15)

    tk.Label(
        card,
        text=value,
        font=("Segoe UI", 19, "bold"),
        bg=WHITE,
        fg=DARK_GREEN
    ).pack(anchor="w", padx=15)


# --------------------------------------------------
# ADD WASTE
# --------------------------------------------------

def show_add_waste():

    clear_content()

    create_title(
        content_frame,
        "Add Food Waste Record",
        "Record what was wasted today."
    )

    form = tk.Frame(
        content_frame,
        bg=WHITE,
        padx=30,
        pady=25
    )

    form.pack(fill="x")

    # Food name
    tk.Label(
        form,
        text="Food Name",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0, sticky="w", pady=8)

    food_entry = tk.Entry(
        form,
        font=("Segoe UI", 11),
        bg="#FAFAF7",
        relief="solid",
        bd=1
    )

    food_entry.grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="ew",
        ipady=8
    )

    # Category
    tk.Label(
        form,
        text="Category",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=2, column=0, sticky="w", pady=(18, 8))

    category_box = ttk.Combobox(
        form,
        values=[
            "Rice",
            "Vegetables",
            "Fruits",
            "Dairy",
            "Bread",
            "Meat",
            "Snacks",
            "Other"
        ],
        state="readonly"
    )

    category_box.grid(
        row=3,
        column=0,
        sticky="ew",
        padx=(0, 15)
    )

    # Quantity
    tk.Label(
        form,
        text="Quantity (kg)",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=2, column=1, sticky="w", pady=(18, 8))

    quantity_entry = tk.Entry(
        form,
        font=("Segoe UI", 11),
        bg="#FAFAF7",
        relief="solid",
        bd=1
    )

    quantity_entry.grid(
        row=3,
        column=1,
        sticky="ew"
    )

    # Price
    tk.Label(
        form,
        text="Price per kg (₹)",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=4, column=0, sticky="w", pady=(18, 8))

    price_entry = tk.Entry(
        form,
        font=("Segoe UI", 11),
        bg="#FAFAF7",
        relief="solid",
        bd=1
    )

    price_entry.grid(
        row=5,
        column=0,
        sticky="ew",
        padx=(0, 15)
    )

    # Reason
    tk.Label(
        form,
        text="Reason",
        bg=WHITE,
        fg=TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=4, column=1, sticky="w", pady=(18, 8))

    reason_box = ttk.Combobox(
        form,
        values=[
            "Excess preparation",
            "Leftover",
            "Spoiled",
            "Expired",
            "Overcooked",
            "Other"
        ],
        state="readonly"
    )

    reason_box.grid(
        row=5,
        column=1,
        sticky="ew"
    )

    form.columnconfigure(0, weight=1)
    form.columnconfigure(1, weight=1)

    def save():

        food = food_entry.get().strip()
        category = category_box.get()
        quantity = quantity_entry.get().strip()
        price = price_entry.get().strip()
        reason = reason_box.get()

        if not food or not category or not quantity or not price or not reason:
            messagebox.showwarning(
                "Missing Information",
                "Please fill all fields."
            )
            return

        try:
            quantity_value = float(quantity)
            price_value = float(price)

            if quantity_value <= 0 or price_value < 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Input",
                "Enter valid numbers for quantity and price."
            )

            return

        add_record(
            food,
            category,
            quantity_value,
            "kg",
            price_value,
            reason
        )

        messagebox.showinfo(
            "Success",
            "Food waste record added successfully!"
        )

        show_dashboard()

    tk.Button(
        form,
        text="＋  Add Record",
        command=save,
        bg=GREEN,
        fg=WHITE,
        activebackground=DARK_GREEN,
        activeforeground=WHITE,
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        padx=20,
        pady=10,
        cursor="hand2"
    ).grid(
        row=6,
        column=0,
        columnspan=2,
        pady=25
    )


# --------------------------------------------------
# RECORDS
# --------------------------------------------------

def show_records():

    clear_content()

    create_title(
        content_frame,
        "Waste Records",
        "View and manage your recorded food waste."
    )

    table_frame = tk.Frame(
        content_frame,
        bg=WHITE
    )

    table_frame.pack(fill="both", expand=True)

    columns = (
        "ID",
        "Food",
        "Category",
        "Quantity",
        "Unit",
        "Price",
        "Reason",
        "Date"
    )

    tree = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings"
    )

    for column in columns:

        tree.heading(
            column,
            text=column
        )

        tree.column(
            column,
            width=100,
            anchor="center"
        )

    tree.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    for record in get_records():

        tree.insert(
            "",
            "end",
            values=record
        )

    def delete_selected():

        selected = tree.selection()

        if not selected:

            messagebox.showwarning(
                "Select Record",
                "Please select a record first."
            )

            return

        item = tree.item(selected[0])

        record_id = item["values"][0]

        answer = messagebox.askyesno(
            "Delete Record",
            "Are you sure you want to delete this record?"
        )

        if answer:

            delete_record(record_id)

            show_records()

    tk.Button(
        content_frame,
        text="🗑 Delete Selected",
        command=delete_selected,
        bg=RED,
        fg=WHITE,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        padx=15,
        pady=8
    ).pack(
        anchor="e",
        pady=10
    )


# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

def show_analytics():

    clear_content()

    create_title(
        content_frame,
        "Waste Analytics",
        "Understand where your food waste is coming from."
    )

    button_frame = tk.Frame(
        content_frame,
        bg=BG
    )

    button_frame.pack(pady=40)

    tk.Button(
        button_frame,
        text="📊 Category Analysis",
        command=show_category_chart,
        bg=GREEN,
        fg=WHITE,
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        padx=25,
        pady=15
    ).pack(
        side="left",
        padx=10
    )

    tk.Button(
        button_frame,
        text="🥧 Waste Reasons",
        command=show_reason_chart,
        bg=PEACH,
        fg=TEXT,
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        padx=25,
        pady=15
    ).pack(
        side="left",
        padx=10
    )

    # Score card

    score = calculate_score()

    score_frame = tk.Frame(
        content_frame,
        bg=WHITE,
        padx=40,
        pady=30
    )

    score_frame.pack(
        fill="x",
        padx=30
    )

    tk.Label(
        score_frame,
        text="🌱 Your Waste Reduction Score",
        font=("Segoe UI", 17, "bold"),
        bg=WHITE,
        fg=DARK_GREEN
    ).pack()

    tk.Label(
        score_frame,
        text=f"{score}/100",
        font=("Segoe UI", 35, "bold"),
        bg=WHITE,
        fg=GREEN
    ).pack(pady=10)

    if score >= 85:
        status = "Excellent progress!"
    elif score >= 70:
        status = "Good progress!"
    elif score >= 50:
        status = "There is room for improvement."
    else:
        status = "Let's work on reducing waste."

    tk.Label(
        score_frame,
        text=status,
        font=("Segoe UI", 11),
        bg=WHITE,
        fg=TEXT
    ).pack()


# --------------------------------------------------
# INSIGHTS
# --------------------------------------------------

def show_insights():

    clear_content()

    create_title(
        content_frame,
        "Smart Insights 💡",
        "Suggestions based on your recorded waste patterns."
    )

    for insight in get_insights():

        box = tk.Frame(
            content_frame,
            bg=WHITE,
            padx=20,
            pady=15
        )

        box.pack(
            fill="x",
            pady=7
        )

        tk.Label(
            box,
            text=insight,
            font=("Segoe UI", 11),
            bg=WHITE,
            fg=TEXT,
            anchor="w"
        ).pack(
            fill="x"
        )


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

sidebar = tk.Frame(
    root,
    bg=SIDEBAR,
    width=230
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(False)


tk.Label(
    sidebar,
    text="🌱 FoodWise",
    font=("Segoe UI", 22, "bold"),
    bg=SIDEBAR,
    fg=DARK_GREEN
).pack(
    pady=(30, 3)
)

tk.Label(
    sidebar,
    text="Smart Food Waste Management",
    font=("Segoe UI", 9),
    bg=SIDEBAR,
    fg="#68736C"
).pack(
    pady=(0, 30)
)


def sidebar_button(text, command):

    tk.Button(
        sidebar,
        text=text,
        command=command,
        bg=SIDEBAR,
        fg=TEXT,
        activebackground=GREEN,
        activeforeground=WHITE,
        font=("Segoe UI", 11),
        anchor="w",
        relief="flat",
        padx=25,
        pady=12,
        cursor="hand2"
    ).pack(
        fill="x",
        padx=10,
        pady=3
    )


sidebar_button("🏠   Dashboard", show_dashboard)
sidebar_button("➕   Add Waste", show_add_waste)
sidebar_button("📋   Waste Records", show_records)
sidebar_button("📊   Analytics", show_analytics)
sidebar_button("💡   Smart Insights", show_insights)


tk.Label(
    sidebar,
    text="",
    bg=SIDEBAR
).pack(expand=True)


tk.Label(
    sidebar,
    text="FoodWise v1.0",
    font=("Segoe UI", 9),
    bg=SIDEBAR,
    fg="#78827A"
).pack(pady=15)


# --------------------------------------------------
# CONTENT AREA
# --------------------------------------------------

content_frame = tk.Frame(
    root,
    bg=BG
)

content_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=35,
    pady=30
)


# Start with dashboard
show_dashboard()

root.mainloop()