import sys
import sqlite3
import pandas as pd
import openpyxl
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem,
                             QDialog, QTextEdit, QFormLayout, QLineEdit, QSizePolicy,
                             QMessageBox, QFileDialog)

class BasicPricelist(QMainWindow):
    def __init__(self):
        """Initializes the GUI and database."""
        super().__init__()
        self.initUI()
        self.initDB()

    def initUI(self):
        """Sets up the user interface."""
        self.setWindowTitle('Basic Pricelist')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # Material List Table
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            ['Mat ID', 'Trade', 'Material', 'Currency', 'Price', 'Unit', 'Vendor', 'Phone', 'Email'])
        main_layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()
        new_material_button = QPushButton('New Material')
        new_material_button.clicked.connect(self.open_new_material_window)
        button_layout.addWidget(new_material_button)
        export_button = QPushButton('Export to Excel')
        export_button.clicked.connect(self.export_to_excel)
        button_layout.addWidget(export_button)
        rfq_button = QPushButton('RFQ')
        rfq_button.clicked.connect(self.open_rfq_window)
        button_layout.addWidget(rfq_button)
        delete_button = QPushButton('Delete Material')
        delete_button.clicked.connect(self.delete_material)
        button_layout.addWidget(delete_button)
        main_layout.addLayout(button_layout)

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
            vendor_email TEXT
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
                                       'Email'])
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
        rfq_dialog = QDialog(self)
        rfq_dialog.setWindowTitle("Request For Quotation")
        rfq_dialog.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()
        email_label = QLabel(f"To: {vendor_email}")
        layout.addWidget(email_label)
        email_body = QTextEdit()
        email_body.setPlainText(
            "Dear Vendor,\n\nI would like to request a quotation for the following materials...\n\nBest regards,\n[Your Name]")
        layout.addWidget(email_body)
        rfq_dialog.setLayout(layout)

        rfq_dialog.exec()

    def open_new_material_window(self):
        """Opens a window to input a new material."""
        self.material_dialog = QDialog(self)
        self.material_dialog.setWindowTitle("New Material")
        self.material_dialog.setGeometry(200, 200, 300, 400)

        layout = QFormLayout()
        self.trade_input = QLineEdit()
        self.material_name_input = QLineEdit()
        self.currency_input = QLineEdit()
        self.price_input = QLineEdit()
        self.unit_input = QLineEdit()
        self.vendor_input = QLineEdit()
        self.vendor_phone_input = QLineEdit()
        self.vendor_email_input = QLineEdit()

        layout.addRow('Trade:', self.trade_input)
        layout.addRow('Material:', self.material_name_input)
        layout.addRow('Currency:', self.currency_input)
        layout.addRow('Price:', self.price_input)
        layout.addRow('Unit:', self.unit_input)
        layout.addRow('Vendor:', self.vendor_input)
        layout.addRow('Vendor Phone:', self.vendor_phone_input)
        layout.addRow('Vendor Email:', self.vendor_email_input)

        add_button = QPushButton('Add')
        add_button.clicked.connect(self.add_or_update_material)
        layout.addWidget(add_button)

        self.material_dialog.setLayout(layout)
        self.material_dialog.exec()

    def add_or_update_material(self):
        """Adds or updates a material in the database."""
        try:
            price = float(self.price_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number for the price.")
            return

        trade = self.trade_input.text().strip()
        material_name = self.material_name_input.text().strip()
        currency = self.currency_input.text().strip()
        unit = self.unit_input.text().strip()
        vendor = self.vendor_input.text().strip()
        vendor_phone = self.vendor_phone_input.text().strip()
        vendor_email = self.vendor_email_input.text().strip()

        if not all([trade, material_name, currency, unit, vendor, vendor_phone, vendor_email]):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        mat_id = f'MAT-{self.get_next_id()}'

        try:
            self.c.execute('''INSERT INTO materials (mat_id, trade, material_name, currency, price, unit, vendor, vendor_phone, vendor_email)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (mat_id, trade, material_name, currency, price, unit, vendor, vendor_phone, vendor_email))
            QMessageBox.information(self, "Success", "Material added successfully.")
            self.material_dialog.close()  # Close the dialog
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Database Error", "A material with this ID already exists.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

        self.conn.commit()
        self.load_data()

    def delete_material(self):
        """Deletes the selected material from the database."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a material to delete.")
            return

        mat_id_item = self.table.item(selected_row, 0)
        if mat_id_item is None:
            QMessageBox.warning(self, "Selection Error", "Could not find the selected material.")
            return

        mat_id = mat_id_item.text()  # Get the Mat ID
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this material?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.c.execute('DELETE FROM materials WHERE mat_id=?', (mat_id,))
                self.conn.commit()
                QMessageBox.information(self, "Success", "Material deleted successfully.")
                self.load_data()  # Refresh the table data after deletion
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred while deleting the material: {e}")

    def get_next_id(self):
        """Gets the next material ID based on the highest current ID."""
        self.c.execute('SELECT MAX(id) FROM materials')
        max_id = self.c.fetchone()[0]
        return (max_id + 1) if max_id is not None else 1

    def closeEvent(self, event):
        """Closes the database connection when the application is closed."""
        self.conn.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = BasicPricelist()
    main_win.show()
    sys.exit(app.exec())
