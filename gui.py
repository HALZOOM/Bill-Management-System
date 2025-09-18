"""
Main GUI application for the Tech & Electronics Billing System.
This module defines the BillApp class, which provides a Tkinter-based interface
for creating bills, managing a shopping cart, viewing past bills, and generating PDF invoices.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db import init_db, add_bill, fetch_bills, fetch_bill_items
from invoice import generate_invoice

# Define color and font constants for easy theming and consistency
COLORS = {
    "bg_primary": "#ecf0f1",
    "bg_dark": "#2c3e50",
    "green": "#27ae60",
    "blue": "#2980b9",
    "purple": "#8e44ad",
    "teal": "#16a085",
    "text_light": "white"
}

FONTS = {
    "title": ("Helvetica", 22, "bold"),
    "heading": ("Helvetica", 12, "bold"),
    "body": ("Helvetica", 11),
    "monospace": ("Courier New", 11)
}


class BillApp:
    """Main application class for the billing system GUI."""

    def __init__(self, root):
        """Initialize the application with the main window."""
        self.root = root
        self.root.title("Tech & Electronics Billing System")
        self._setup_main_window()

        # Initialize the database and application state
        init_db()
        self.cart = []
        self.selected_bill = None

        self._create_title_bar()
        main_frame = self._create_main_frame()
        self._create_input_section(main_frame)
        self._create_cart_section(main_frame)
        self._create_bills_section(main_frame)
        self._create_button_bar(main_frame)
        self.load_bills()

    def _setup_main_window(self):
        """Configure the main window's size and background."""
        try:
            self.root.state('zoomed')
        except Exception:
            width = self.root.winfo_screenwidth()
            height = self.root.winfo_screenheight()
            self.root.geometry(f"{width}x{height}+0+0")

        self.root.configure(bg=COLORS["bg_primary"])
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

    def _create_title_bar(self):
        """Create the application title bar."""
        self.title_label = tk.Label(
            self.root,
            text="🛒 Tech & Electronics Billing System",
            font=FONTS["title"],
            bg=COLORS["bg_dark"],
            fg=COLORS["text_light"],
            pady=15
        )
        self.title_label.grid(row=0, column=0, sticky="ew")

    def _create_main_frame(self):
        """Create and return the main content frame."""
        main_frame = tk.Frame(self.root, bg=COLORS["bg_primary"])
        main_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(1, weight=1)
        return main_frame

    def _create_input_section(self, parent):
        """Create the product selection and customer input section."""
        input_frame = tk.LabelFrame(
            parent,
            text="Add Products to Cart",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["bg_dark"],
            padx=15, pady=15
        )
        input_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        input_frame.columnconfigure(1, weight=1)  # Make the entry fields expandable

        # Customer name input.
        tk.Label(input_frame, text="Customer Name:", font=FONTS["body"], bg=COLORS["bg_primary"]).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.customer_entry = tk.Entry(input_frame, font=FONTS["body"], width=30)
        self.customer_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2, sticky="ew")

        # Product selection.
        tk.Label(input_frame, text="Product:", font=FONTS["body"], bg=COLORS["bg_primary"]).grid(
            row=1, column=0, sticky="w", pady=5
        )
        self.product_var = tk.StringVar()
        self.product_dropdown = ttk.Combobox(
            input_frame,
            textvariable=self.product_var,
            state="readonly",
            font=FONTS["body"],
            width=30
        )
        self.product_dropdown['values'] = [
            "Laptop - 800.00",
            "Smartphone - 500.00",
            "Tablet - 300.00",
            "Headphones - 100.00",
            "Smartwatch - 150.00",
            "Gaming Console - 600.00",
            "4K Monitor - 400.00",
            "Mechanical Keyboard - 120.00",
            "Wireless Mouse - 40.00",
            "External Hard Drive - 120.00"
        ]
        if self.product_dropdown['values']:
            self.product_dropdown.current(0)
        self.product_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Quantity input.
        tk.Label(input_frame, text="Quantity:", font=FONTS["body"], bg=COLORS["bg_primary"]).grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.qty_entry = tk.Entry(input_frame, font=FONTS["body"], width=10)
        self.qty_entry.insert(0, "1")  # Default quantity
        self.qty_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # "Add to cart" button.
        self.add_button = tk.Button(
            input_frame,
            text="Add to Cart",
            font=FONTS["body"],
            bg=COLORS["green"],
            fg="white",
            relief="flat",
            padx=15,
            pady=6,
            command=self.add_to_cart
        )
        self.add_button.grid(row=3, column=0, columnspan=2, pady=10)

    def _create_cart_section(self, parent):
        """Create the shopping cart display section."""
        cart_frame = tk.LabelFrame(
            parent,
            text="Shopping Cart",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["bg_dark"],
            padx=15,
            pady=15
        )
        cart_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        cart_frame.rowconfigure(0, weight=1)
        cart_frame.columnconfigure(0, weight=1)

        # listbox with scrollbar
        cart_container = tk.Frame(cart_frame)
        cart_container.grid(row=0, column=0, sticky="nsew")
        cart_container.rowconfigure(0, weight=1)
        cart_container.columnconfigure(0, weight=1)
        self.cart_list = tk.Listbox(cart_container, font=FONTS["monospace"])
        self.cart_list.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(cart_container, orient="vertical", command=self.cart_list.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.cart_list.configure(yscrollcommand=scrollbar.set)

    def _create_bills_section(self, parent):
        """Create the previous bills history section."""
        bills_frame = tk.LabelFrame(
            parent,
            text="Previous Bills",
            font=FONTS["heading"],
            bg=COLORS["bg_primary"],
            fg=COLORS["bg_dark"],
            padx=15,
            pady=15
        )
        bills_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=10)
        bills_frame.rowconfigure(0, weight=1)
        bills_frame.columnconfigure(0, weight=1)

        # Create treeview with scrollbar.
        tree_container = tk.Frame(bills_frame)
        tree_container.grid(row=0, column=0, sticky="nsew")
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        columns = ("ID", "Customer", "Date", "Total")
        self.bills_tree = ttk.Treeview(tree_container, columns=columns, show="headings", selectmode="browse")

        # configure column headings and widths
        column_widths = [50, 150, 150, 100]
        for col, width in zip(columns, column_widths):
            self.bills_tree.heading(col, text=col)
            self.bills_tree.column(col, width=width, anchor="center")

        self.bills_tree.grid(row=0, column=0, sticky="nsew")
        self.bills_tree.bind("<<TreeviewSelect>>", self.on_bill_select)

        tree_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.bills_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.bills_tree.configure(yscrollcommand=tree_scrollbar.set)

    def _create_button_bar(self, parent):
        """Create the button bar at the bottom of the application."""
        btn_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        self.save_button = tk.Button(
            btn_frame,
            text="Save Bill",
            command=self.save_bill,
            font=FONTS["body"],
            bg=COLORS["blue"],
            fg="white",
            padx=20,
            pady=8
        )
        self.save_button.grid(row=0, column=0, padx=10)

        self.export_button = tk.Button(
            btn_frame,
            text="Export PDF",
            command=self.export_invoice,
            font=FONTS["body"],
            bg=COLORS["purple"],
            fg="white",
            padx=20,
            pady=8
        )
        self.export_button.grid(row=0, column=1, padx=10)

        self.open_external_button = tk.Button(
            btn_frame,
            text="Open Invoice",
            command=self.open_invoice_external,
            font=FONTS["body"],
            bg=COLORS["teal"],
            fg="white",
            padx=20,
            pady=8
        )
        self.open_external_button.grid(row=0, column=2, padx=10)

    def add_to_cart(self):
        """Add the selected product and quantity to the shopping cart."""
        product_text = self.product_var.get()
        qty_text = self.qty_entry.get()

        if not product_text:
            messagebox.showerror("Error", "Please select a product.")
            return

        if not qty_text.isdigit() or int(qty_text) <= 0:
            messagebox.showerror("Error", "Please enter a valid quantity (1 or more).")
            return

        qty = int(qty_text)

        try:
            name, price_str = product_text.split(" - ")
            price = float(price_str)
        except ValueError:
            messagebox.showerror("Error", "Could not parse product information. Please select a valid product.")
            return

        self.cart.append((name, price, qty))
        self.cart_list.insert(tk.END, f"{name} × {qty} → ${price * qty:.2f}")

        self.qty_entry.delete(0, tk.END)
        self.qty_entry.insert(0, "1")  # defaul value

    def save_bill(self):
        """Save the current cart as a bill to the database."""
        customer = self.customer_entry.get().strip()
        if not customer:
            messagebox.showerror("Error", "Please enter a customer name.")
            return

        if not self.cart:
            messagebox.showerror("Error", "Your cart is empty. Add some products first.")
            return

        # current timestamp
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = sum(price * qty for _, price, qty in self.cart)

        try:
            bill_id = add_bill(customer, date_str, total, self.cart)
            self.selected_bill = (bill_id, customer, date_str, total)
            messagebox.showinfo("Bill Saved", f"Bill #{bill_id} saved successfully. Total: ${total:.2f}")
            self.cart.clear()
            self.cart_list.delete(0, tk.END)
            self.customer_entry.delete(0, tk.END)
            self.load_bills()

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save bill: {str(e)}")

    def load_bills(self):
        """Load all bills from the database into the history view."""
        try:
            rows = fetch_bills()
            for item in self.bills_tree.get_children():
                self.bills_tree.delete(item)

            for (bid, customer, date_str, total) in rows:
                self.bills_tree.insert("", tk.END, values=(
                    bid,
                    customer,
                    date_str,
                    f"${total:.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load bills: {str(e)}")

    def on_bill_select(self, event):
        """Handle selection of a bill from the history."""
        sel = self.bills_tree.selection()
        if not sel:
            self.selected_bill = None
            return

        item = sel[0]
        vals = self.bills_tree.item(item, "values")

        try:
            bid = int(vals[0])
            customer = vals[1]
            date_str = vals[2]
            total = float(vals[3].strip().replace("$", ""))

            self.selected_bill = (bid, customer, date_str, total)
        except (ValueError, IndexError) as e:
            messagebox.showerror("Error", f"Failed to parse bill information: {str(e)}")
            self.selected_bill = None

    def export_invoice(self):
        """Generate a PDF invoice for the selected bill."""
        if self.selected_bill:
            bid, customer, date_str, total = self.selected_bill
        else:
            rows = fetch_bills()
            if not rows:
                messagebox.showerror("Error", "No bills found in database.")
                return
            bid, customer, date_str, total = rows[0]

        try:
            items = fetch_bill_items(bid)
            filename = generate_invoice(bid, customer, date_str, total, items)
            messagebox.showinfo("Export Successful", f"Invoice saved as:\n{filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate invoice: {str(e)}")

    def open_invoice_external(self):
        """Open the selected bill's invoice with the system's default PDF viewer."""
        if self.selected_bill:
            bid, customer, date_str, total = self.selected_bill
        else:
            rows = fetch_bills()
            if not rows:
                messagebox.showerror("Error", "No bills found in database.")
                return
            bid, customer, date_str, total = rows[0]

        invoice_path = os.path.join("invoices", f"invoice_{bid}.pdf")

        if not os.path.exists(invoice_path):
            try:
                items = fetch_bill_items(bid)
                generate_invoice(bid, customer, date_str, total, items)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate invoice: {str(e)}")
                return

        if not os.path.exists(invoice_path):
            messagebox.showerror("Error", f"Invoice file missing for bill #{bid}")
            return

        # Open the PDF with the system's default viewer
        try:
            if os.name == 'nt':  # Windows
                os.startfile(invoice_path)
            elif os.name == 'posix':  # macOS or Linux
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                os.system(f'{opener} "{invoice_path}"')
            else:
                messagebox.showinfo("Invoice Generated", f"Invoice saved at:\n{invoice_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open invoice: {str(e)}")
