import sys
import sqlite3
import pandas as pd
import openpyxl
import re
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem,
                             QDialog, QTextEdit, QFormLayout, QLineEdit, QSizePolicy,
                             QMessageBox, QFileDialog, QComboBox, QDateEdit)

class BasicPricelist(QMainWindow):
    def __init__(self):
        """Initializes the GUI and database."""
        super().__init__()
        self.initUI()
        self.initDB()

    def initUI(self):
        """Sets up the user interface."""
        self.setWindowTitle('Basic Prices Manager v.1.0')
        self.setGeometry(100, 100, 1100, 700)

        main_layout = QVBoxLayout()

        # Buttons
        button_layout = QHBoxLayout()
        new_material_button = QPushButton('New Material')
        new_material_button.clicked.connect(self.open_new_material_window)
        button_layout.addWidget(new_material_button)

        edit_material_button = QPushButton('Edit Material')
        edit_material_button.clicked.connect(self.open_edit_material_window)
        button_layout.addWidget(edit_material_button)

        delete_button = QPushButton('Delete Material')
        delete_button.clicked.connect(self.delete_material)
        button_layout.addWidget(delete_button)

        rfq_button = QPushButton('RFQ')
        rfq_button.clicked.connect(self.open_rfq_window)
        button_layout.addWidget(rfq_button)

        export_button = QPushButton('Export to Excel')
        export_button.clicked.connect(self.export_to_excel)
        button_layout.addWidget(export_button)

        main_layout.addLayout(button_layout)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search materials...")
        self.search_input.textChanged.connect(self.search_materials)
        search_layout.addWidget(self.search_input)

        # Sort Options
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(
            ['Sort by Mat ID', 'Sort by Trade', 'Sort by Vendor', 'Sort by Material', 'Sort by Price'])
        self.sort_combo.currentIndexChanged.connect(self.sort_materials)
        search_layout.addWidget(self.sort_combo)

        main_layout.addLayout(search_layout)

        # Material List Table
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setColumnCount(10)  # Updated to 10 for new date column
        self.table.setHorizontalHeaderLabels(
            ['Mat ID', 'Trade', 'Material', 'Currency', 'Price', 'Unit', 'Vendor', 'Phone', 'Email', 'Price Date'])  # Added Price Date
        main_layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def initDB(self):
        """Initializes the SQLite database."""
        self.conn = sqlite3.connect('materials.db')
        self.c = self.conn.cursor()

        # Create the table only if it does not exist
        self.c.execute('''CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY,
            mat_id TEXT UNIQUE,
            trade TEXT,
            material_name TEXT,
            currency TEXT,
            price REAL,
            unit TEXT,
            vendor TEXT,
            vendor_phone TEXT,
            vendor_email TEXT,
            price_date TEXT  -- New column for price date
        )''')
        self.conn.commit()
        self.load_data()  # Load data after the table has been initialized

    def load_data(self):
        """Loads data from the database into the table."""
        self.c.execute('SELECT * FROM materials')
        rows = self.c.fetchall()
        self.table.setRowCount(len(rows))
        for row_num, row_data in enumerate(rows):
            for col_num, data in enumerate(row_data[1:]):  # Skip the id column
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def populate_table(self, rows):
        """Populates the table with data."""
        self.table.setRowCount(len(rows))
        for row_num, row_data in enumerate(rows):
            for col_num, data in enumerate(row_data[1:]):  # Skip the id column
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def search_materials(self):
        """Searches for materials based on user input."""
        search_text = self.search_input.text().lower()
        self.c.execute('SELECT * FROM materials')
        rows = self.c.fetchall()
        filtered_rows = [row for row in rows if search_text in row[1].lower() or  # Trade
                         search_text in row[2].lower() or  # Material name
                         search_text in row[3].lower()]  # Currency
        self.populate_table(filtered_rows)

    def sort_materials(self):
        """Sorts the materials based on the selected criteria."""
        sort_index = self.sort_combo.currentIndex()
        sort_column = 'mat_id'
        if sort_index == 1:
            sort_column = 'trade'
        elif sort_index == 2:
            sort_column = 'material_name'
        elif sort_index == 3:
            sort_column = 'price'

        self.c.execute(f'SELECT * FROM materials ORDER BY {sort_column}')
        rows = self.c.fetchall()
        self.populate_table(rows)

    def export_to_excel(self):
        """Exports the data to an Excel file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx);;All Files (*)")
        if not file_path:  # Check if a file path was provided
            return

        try:
            data = []
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item is not None else "")  # Handle None items safely
                data.append(row_data)

            df = pd.DataFrame(data,
                              columns=['Mat ID', 'Trade', 'Material', 'Currency', 'Price', 'Unit', 'Vendor', 'Phone',
                                       'Email', 'Price Date'])  # Updated column names
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Export Successful", f"Data exported successfully to {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred during export: {e}")

    def open_rfq_window(self):
        """Opens the RFQ window with the vendor's email and a template message."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a material to request a quotation.")
            return
        vendor_email = self.table.item(selected_row, 8).text()  # Adjusted for the new column
        vendor_material = self.table.item(selected_row, 2).text()  # Adjusted for the new column
        rfq_dialog = QDialog(self)
        rfq_dialog.setWindowTitle("Request For Quotation")
        rfq_dialog.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        email_label = QLabel(f"To: {vendor_email}")
        layout.addWidget(email_label)
        email_body = QTextEdit()
        email_body.setPlainText(
            f"Dear Vendor,\n\nI would like to request a quotation for the following materials...\n"
            f"1. {vendor_material}.\n\nBest regards,\n[Your Name]")
        layout.addWidget(email_body)
        rfq_dialog.setLayout(layout)

        rfq_dialog.exec()

    def open_new_material_window(self):
        """Opens a window to input a new material."""
        self.material_dialog = QDialog(self)
        self.material_dialog.setWindowTitle("New Material")
        self.material_dialog.setGeometry(200, 200, 300, 450)  # Updated height for new field

        layout = QFormLayout()
        self.trade_input = QLineEdit()
        self.material_name_input = QLineEdit()
        self.currency_input = QLineEdit()
        self.price_input = QLineEdit()
        self.unit_input = QLineEdit()
        self.vendor_input = QLineEdit()
        self.vendor_phone_input = QLineEdit()
        self.vendor_email_input = QLineEdit()
        self.price_date_input = QDateEdit()  # New date input field
        self.price_date_input.setDate(QDate.currentDate())  # Set default date to today
        self.price_date_input.setCalendarPopup(True)  # Show calendar popup for date selection

        layout.addRow('Trade:', self.trade_input)
        layout.addRow('Material:', self.material_name_input)
        layout.addRow('Currency:', self.currency_input)
        layout.addRow('Price:', self.price_input)
        layout.addRow('Unit:', self.unit_input)
        layout.addRow('Vendor:', self.vendor_input)
        layout.addRow('Vendor Phone:', self.vendor_phone_input)
        layout.addRow('Vendor Email:', self.vendor_email_input)
        layout.addRow('Price Date:', self.price_date_input)  # Add the date input field

        add_button = QPushButton("Add Material")
        add_button.clicked.connect(self.add_material)
        layout.addWidget(add_button)

        self.material_dialog.setLayout(layout)
        self.material_dialog.exec()

    def is_valid_email(self, email):
        """Checks if the given email follows a valid format."""
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(email_pattern, email) is not None

    def add_material(self):
        """Adds a new material to the database."""

        try:
            # Format price to two decimal places with commas, e.g., 1,000.00
            price = float(self.price_input.text())
            formatted_price = f"{price:,.2f}"
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number for the price.")
            return

        trade = self.trade_input.text()
        material_name = self.material_name_input.text()
        currency = self.currency_input.text()
        unit = self.unit_input.text()
        vendor = self.vendor_input.text()
        vendor_phone = self.vendor_phone_input.text()
        vendor_email = self.vendor_email_input.text()
        price_date = self.price_date_input.text()  # Get date as string

        # Validate email
        if not self.is_valid_email(vendor_email):
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address.")
            return

        # Generate new mat_id
        self.c.execute('SELECT MAX(mat_id) FROM materials')
        max_id = self.c.fetchone()[0]
        new_id = 1 if max_id is None else int(max_id.split('-')[1]) + 1
        mat_id = f'MAT-{new_id}'

        # Insert into the database
        self.c.execute('''INSERT INTO materials (mat_id, trade, material_name, currency, price, unit, vendor, vendor_phone, vendor_email, price_date) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (mat_id, trade, material_name, currency, formatted_price, unit, vendor, vendor_phone, vendor_email, price_date))
        self.conn.commit()
        self.load_data()  # Reload data to display updated list
        self.material_dialog.close()

    def open_edit_material_window(self):
        """Opens a window to edit the selected material."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a material to edit.")
            return

        # Get current values
        mat_id = self.table.item(selected_row, 0).text()
        trade = self.table.item(selected_row, 1).text()
        material_name = self.table.item(selected_row, 2).text()
        currency = self.table.item(selected_row, 3).text()
        price = self.table.item(selected_row, 4).text()
        unit = self.table.item(selected_row, 5).text()
        vendor = self.table.item(selected_row, 6).text()
        vendor_phone = self.table.item(selected_row, 7).text()
        vendor_email = self.table.item(selected_row, 8).text()
        price_date = self.table.item(selected_row, 9).text()  # Get price date

        self.material_dialog = QDialog(self)
        self.material_dialog.setWindowTitle("Edit Material")
        self.material_dialog.setGeometry(200, 200, 300, 450)  # Updated height for new field

        layout = QFormLayout()
        self.trade_input = QLineEdit(trade)
        self.material_name_input = QLineEdit(material_name)
        self.currency_input = QLineEdit(currency)
        self.price_input = QLineEdit(price)
        self.unit_input = QLineEdit(unit)
        self.vendor_input = QLineEdit(vendor)
        self.vendor_phone_input = QLineEdit(vendor_phone)
        self.vendor_email_input = QLineEdit(vendor_email)
        self.price_date_input = QDateEdit()  # New date input field
        self.price_date_input.setDate(pd.to_datetime(price_date, dayfirst=True))  # Set the date input from current value
        self.price_date_input.setCalendarPopup(True)  # Show calendar popup for date selection

        layout.addRow('Trade:', self.trade_input)
        layout.addRow('Material:', self.material_name_input)
        layout.addRow('Currency:', self.currency_input)
        layout.addRow('Price:', self.price_input)
        layout.addRow('Unit:', self.unit_input)
        layout.addRow('Vendor:', self.vendor_input)
        layout.addRow('Vendor Phone:', self.vendor_phone_input)
        layout.addRow('Vendor Email:', self.vendor_email_input)
        layout.addRow('Price Date:', self.price_date_input)  # Add the date input field

        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(lambda: self.update_material(mat_id))
        layout.addWidget(save_button)

        self.material_dialog.setLayout(layout)
        self.material_dialog.exec()

    def update_material(self, mat_id):
        """Updates the selected material in the database."""

        try:
            # Remove commas to safely convert to float
            price = float(self.price_input.text().replace(',', ''))
            formatted_price = f"{price:,.2f}"
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number for the price.")
            return

        trade = self.trade_input.text()
        material_name = self.material_name_input.text()
        currency = self.currency_input.text()
        unit = self.unit_input.text()
        vendor = self.vendor_input.text()
        vendor_phone = self.vendor_phone_input.text()
        vendor_email = self.vendor_email_input.text()
        price_date = self.price_date_input.text()  # Get updated date

        # Validate email
        if not self.is_valid_email(vendor_email):
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address.")
            return

        # Update in the database
        self.c.execute('''UPDATE materials SET trade=?, material_name=?, currency=?, price=?, unit=?, vendor=?, vendor_phone=?, vendor_email=?, price_date=? 
                          WHERE mat_id=?''',
                       (trade, material_name, currency, formatted_price, unit, vendor, vendor_phone, vendor_email, price_date, mat_id))
        self.conn.commit()
        self.load_data()  # Reload data to display updated list
        self.material_dialog.close()

    def delete_material(self):
        """Deletes the selected material from the database."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a material to delete.")
            return

        mat_id = self.table.item(selected_row, 0).text()
        reply = QMessageBox.question(self, 'Delete Material', 'Are you sure you want to delete this material?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.c.execute('DELETE FROM materials WHERE mat_id=?', (mat_id,))
            self.conn.commit()
            self.load_data()  # Reload data to reflect deletion

    def closeEvent(self, event):
        """Handles the window close event."""
        self.conn.close()  # Close the database connection
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BasicPricelist()
    window.show()
    sys.exit(app.exec())
