"""
Generates a PDF invoice and saves it to the "invoices" folder.

Args:
    bill_id (str): The unique identifier for the bill.
    customer (str): The name of the customer.
    date (str): The date of the invoice.
    total (float): The total amount of money that the customer must pay.
    items (list of tuples): A list where each tuple contains (product_name, unit_price, quantity).
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_invoice(bill_id, customer, date, total, items):
    os.makedirs("invoices", exist_ok=True)
    filename = os.path.join("invoices", f"invoice_{bill_id}.pdf")

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, height - 50, "Tech & Electronics Invoice")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Bill ID: {bill_id}")
    c.drawString(50, height - 120, f"Customer: {customer}")
    c.drawString(50, height - 140, f"Date: {date}")

    c.drawString(50, height - 180, "Product")
    c.drawString(300, height - 180, "Price")
    c.drawString(400, height - 180, "Quantity")
    c.drawString(500, height - 180, "Subtotal")

    y = height - 200
    for product, price, quantity in items:
        c.drawString(50, y, str(product))
        c.drawString(300, y, f"${price:.2f}")
        c.drawString(400, y, str(quantity))
        c.drawString(500, y, f"${price * quantity:.2f}")
        y -= 20

        # Add new page.
        if y < 100:
            c.showPage()
            y = height - 50

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 30, f"Grand Total: ${total:.2f}")

    c.save()
    return filename
