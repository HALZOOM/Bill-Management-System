# Tech & Electronics Billing System

A desktop application for managing sales and generating invoices for electronics retail businesses.

## Features

- Point of Sale interface for product selection
- Customer information management
- Shopping cart with real-time calculations
- SQLite database for data storage
- Automated PDF invoice generation
- Sales history tracking

## Requirements

- Python 3.8+
- ReportLab library

## Installation

1. Install Python 3.8 or higher
2. Install the required library:
   ```
   pip install reportlab
   ```
3. Download the project files

## Usage

Run the application:
```
python main.py
```

- Add customer information
- Select products and quantities
- Save transactions to database
- Generate PDF invoices
- View sales history

## Files

- `main.py` - Application entry point
- `gui.py` - User interface
- `db.py` - Database operations
- `invoice.py` - PDF generation
- `bills.db` - Database file (auto-created)
- `invoices/` - Generated PDF invoices

## License

MIT License
