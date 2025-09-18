"""
Database layer for the Tech & Electronics Billing System.

Handles all interactions with the SQLite database, including:
- Initializing the database schema
- Adding new bills and their line items
- Retrieving bill history and details
"""

import sqlite3

DB_FILE = "bills.db"


def init_db():
    """
    Initializes the database by creating the necessary tables if they don't exist.
    Called once at application startup.
    """

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT,
            date TEXT,
            total REAL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_id INTEGER,
            product TEXT,
            price REAL,
            quantity INTEGER,
            FOREIGN KEY(bill_id) REFERENCES bills(id)
        )
    """)

    conn.commit()
    conn.close()


def add_bill(customer, date, total, items):
    """
    Adds a new bill and its associated items to the database in a single transaction.

    Args:
        customer (str): The customer's name.
        date (str): The date of the bill.
        total (float): The total amount of the bill.
        items (list of tuples): List of (product, price, quantity) tuples.

    Returns:
        int: The ID of the newly created bill.
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bills (customer, date, total) VALUES (?, ?, ?)",
        (customer, date, total)
    )
    bill_id = cur.lastrowid
    for product, price, quantity in items:
        cur.execute(
            "INSERT INTO bill_items (bill_id, product, price, quantity) VALUES (?, ?, ?, ?)",
            (bill_id, product, price, quantity)
        )
    conn.commit()
    conn.close()
    return bill_id


def fetch_bills():
    """
    Fetches a list of all bills, sorted by most recent first.

    Returns:
        list of tuples: Each tuple contains (id, customer, date, total).
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT id, customer, date, total FROM bills ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def fetch_bill_items(bill_id):
    """
    Fetches all line items for a specific bill.

    Args:
        bill_id (int): The ID of the bill to retrieve items for.

    Returns:
        list of tuples: Each tuple contains (product, price, quantity).
    """
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute(
        "SELECT product, price, quantity FROM bill_items WHERE bill_id = ?",
        (bill_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows
