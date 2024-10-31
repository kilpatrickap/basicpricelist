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

        edit_material_button = QPushButton('Edit Material')
        edit_material_button.clicked.connect(self.open_edit_material_window)
        button_layout.addWidget(edit_material_button)

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

    def open_edit_material_window(self):
        """Opens a window to edit the selected material."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a material to edit.")
            return

        # Retrieve the data from the selected row
        mat_id = self.table.item(selected_row, 0).text()
        trade = self.table.item(selected_row, 1).text()
        material_name = self.table.item(selected_row, 2).text()
        currency = self.table.item(selected_row, 3).text()
        price = self.table.item(selected_row, 4).text()
        unit = self.table.item(selected_row, 5).text()
        vendor = self.table.item(selected_row, 6).text()
        vendor_phone = self.table.item(selected_row, 7).text()
        vendor_email = self.table.item(selected_row, 8).text()

        self.material_dialog = QDialog(self)
        self.material_dialog.setWindowTitle("Edit Material")
        self.material_dialog.setGeometry(200, 200, 300, 400)

        layout = QFormLayout()
        self.trade_input = QLineEdit(trade)
        self.material_name_input = QLineEdit(material_name)
        self.currency_input = QLineEdit(currency)
        self.price_input = QLineEdit(price)
        self.unit_input = QLineEdit(unit)
        self.vendor_input = QLineEdit(vendor)
        self.vendor_phone_input = QLineEdit(vendor_phone)
        self.vendor_email_input = QLineEdit(vendor_email)

        layout.addRow('Trade:', self.trade_input)
        layout.addRow('Material:', self.material_name_input)
        layout.addRow('Currency:', self.currency_input)
        layout.addRow('Price:', self.price_input)
        layout.addRow('Unit:', self.unit_input)
        layout.addRow('Vendor:', self.vendor_input)
        layout.addRow('Vendor Phone:', self.vendor_phone_input)
        layout.addRow('Vendor Email:', self.vendor_email_input)

        update_button = QPushButton('Update')
        update_button.clicked.connect(lambda: self.update_material(mat_id))
        layout.addWidget(update_button)

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

        self.c.execute('''INSERT OR REPLACE INTO materials (mat_id, trade, material_name, currency, price, unit, vendor, vendor_phone, vendor_email)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (material_name, trade, material_name, currency, price, unit, vendor, vendor_phone, vendor_email))

        self.conn.commit()
        self.load_data()  # Refresh data in the table
        self.material_dialog.close()

    def update_material(self, mat_id):
        """Updates an existing material in the database."""
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

        self.c.execute('''UPDATE materials
                        SET trade = ?, material_name = ?, currency = ?, price = ?, unit = ?, vendor = ?, vendor_phone = ?, vendor_email = ?
                        WHERE mat_id = ?''',
                       (trade, material_name, currency, price, unit, vendor, vendor_phone, vendor_email, mat_id))

        self.conn.commit()
        self.load_data()  # Refresh data in the table
        self.material_dialog.close()

    def delete_material(self):
        """Deletes the selected material from the database after user confirmation."""
        selected_row = self.table.currentRow()

        # Check if a material is selected
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a material before deleting.")
            return

        # Get the material ID of the selected row (assuming Mat ID is in the first column)
        mat_id_item = self.table.item(selected_row, 0)  # Adjust index if necessary
        if mat_id_item is None:
            QMessageBox.warning(self, "Selection Error", "Could not retrieve Mat ID for the selected material.")
            return

        mat_id = mat_id_item.text()  # Get the Mat ID

        # Confirmation dialog
        reply = QMessageBox.question(self, "Confirm Deletion",
                                     f"Are you sure you want to delete the material '{mat_id}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.c.execute('DELETE FROM materials WHERE mat_id = ?', (mat_id,))
                self.conn.commit()
                self.load_data()  # Refresh data in the table
                QMessageBox.information(self, "Success", f"Material '{mat_id}' deleted successfully.")
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred while deleting the material: {e}")

    def closeEvent(self, event):
        """Handles the closing of the main window."""
        self.conn.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = BasicPricelist()
    main_win.show()
    sys.exit(app.exec())
