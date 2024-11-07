import sys
import sqlite3
import pandas as pd
import openpyxl
import re
import pycountry
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem,
                             QDialog, QTextEdit, QFormLayout, QLineEdit, QSizePolicy,
                             QMessageBox, QFileDialog, QComboBox, QDateEdit, QRadioButton, QButtonGroup)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

        # Add a "User" button next to the "New Material" button
        user_button = QPushButton("User")
        user_button.clicked.connect(self.open_user_info_window)
        button_layout.addWidget(user_button)

        new_material_button = QPushButton('New Material')
        new_material_button.clicked.connect(self.open_new_material_window)
        button_layout.addWidget(new_material_button)

        edit_material_button = QPushButton('Edit Material')
        edit_material_button.clicked.connect(self.open_edit_material_window)
        button_layout.addWidget(edit_material_button)

        duplicate_button = QPushButton('Duplicate Material')
        duplicate_button.clicked.connect(self.duplicate_material)
        button_layout.insertWidget(2, duplicate_button)  # Inserts Duplicate Material between Edit and Delete

        delete_button = QPushButton('Delete Material')
        delete_button.clicked.connect(self.delete_material)
        button_layout.addWidget(delete_button)

        rfq_button = QPushButton('RFP')
        rfq_button.clicked.connect(self.open_rfp_window)
        button_layout.addWidget(rfq_button)

        export_button = QPushButton('Export to Excel')
        export_button.clicked.connect(self.export_to_excel)
        button_layout.addWidget(export_button)

        main_layout.addLayout(button_layout)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for MAT-IDs, Trades, Materials and Vendors...")
        self.search_input.textChanged.connect(self.search_materials)
        search_layout.addWidget(self.search_input)

        # Sort Options
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(
            ['Sort by Mat ID', 'Sort by Trade', 'Sort by Material', 'Sort by Price', 'Sort by Vendor'])
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
        """Initializes the SQLite database for materials and users."""
        # Initialize materials database
        self.conn = sqlite3.connect('materials.db')
        self.c = self.conn.cursor()
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
            price_date TEXT
        )''')
        self.conn.commit()
        self.load_data()

        # Initialize users database
        self.users_conn = sqlite3.connect('users.db')
        self.users_c = self.users_conn.cursor()
        self.users_c.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            user_code TEXT UNIQUE,
            name TEXT,
            company TEXT,
            position TEXT,
            phone TEXT,
            email TEXT
        )''')

        # Check if 'is_default' column exists; if not, add it
        try:
            self.users_c.execute("ALTER TABLE users ADD COLUMN is_default INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            # Column already exists, no need to add it
            pass

        self.users_conn.commit()

    def open_user_info_window(self):
        """Displays options for New User and Existing User, with a responsive Submit button."""
        user_type_dialog = QDialog(self)
        user_type_dialog.setWindowTitle("Select User Type")
        user_type_dialog.setGeometry(200, 200, 200, 100)

        layout = QVBoxLayout()

        # Radio buttons for selecting user type
        new_user_radio = QRadioButton("New User")
        existing_user_radio = QRadioButton("Existing User")

        # Add the radio buttons to a button group for exclusive selection
        button_group = QButtonGroup(user_type_dialog)
        button_group.addButton(new_user_radio)
        button_group.addButton(existing_user_radio)

        layout.addWidget(new_user_radio)
        layout.addWidget(existing_user_radio)

        # Responsive layout for the Submit button
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Spacer on the left
        submit_button = QPushButton("Next")
        submit_button.clicked.connect(lambda: self.check_user_type_selection(new_user_radio,existing_user_radio, user_type_dialog))
        # Else if the existing_user_radio is selected, open the show_existing_user_window

        button_layout.addWidget(submit_button)  # Center button
        button_layout.addStretch()  # Spacer on the right

        layout.addLayout(button_layout)  # Add button layout to the main layout
        user_type_dialog.setLayout(layout)
        user_type_dialog.exec()

    def check_user_type_selection(self, new_user_radio, existing_user_radio, user_type_dialog):
        """Checks which radio button is selected and opens the appropriate window."""
        if new_user_radio.isChecked():
            user_type_dialog.close()  # Close the selection dialog
            self.show_user_information_dialog()  # Open the user information window
        elif existing_user_radio.isChecked():  # Check if the existing user radio is selected
            user_type_dialog.close()  # Close the selection dialog
            self.show_existing_user_window()  # Open the existing user window

    def show_existing_user_window(self):
        """Shows the list of all existing users with 'Make Default', 'Edit', and 'Delete' buttons."""
        user_list_dialog = QDialog(self)
        user_list_dialog.setWindowTitle("Existing Users")
        user_list_dialog.setGeometry(200, 200, 450, 200)

        table_widget = QTableWidget()
        table_widget.setRowCount(0)
        table_widget.setColumnCount(3)
        table_widget.setHorizontalHeaderLabels(["User ID", "Name", "Make Default"])

        # Fetch and populate data
        self.users_c.execute("SELECT user_id, name FROM users")
        users = self.users_c.fetchall()
        for row_idx, user in enumerate(users):
            table_widget.insertRow(row_idx)
            table_widget.setItem(row_idx, 0, QTableWidgetItem(f"UserID-{user[0]}"))
            table_widget.setItem(row_idx, 1, QTableWidgetItem(user[1]))

            make_default_button = QPushButton("Default")
            make_default_button.clicked.connect(lambda checked, user_id=user[0]: self.make_default_user(user_id))
            table_widget.setCellWidget(row_idx, 2, make_default_button)

        # Set up layouts
        main_layout = QHBoxLayout()
        main_layout.addWidget(table_widget)

        # Edit and Delete button layout
        button_layout = QVBoxLayout()
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda: self.open_edit_user_window(table_widget))
        button_layout.addWidget(edit_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_selected_user(table_widget))  # Assuming delete function
        button_layout.addWidget(delete_button)

        button_layout.addStretch()  # Spacer at the bottom
        main_layout.addLayout(button_layout)

        user_list_dialog.setLayout(main_layout)
        user_list_dialog.exec()

    def delete_selected_user(self, table_widget):
        """Deletes the selected user from the database and removes the row from the table."""
        # Get the selected row
        selected_row = table_widget.currentRow()

        # Check if a row is selected
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a user to delete.")
            return

        # Retrieve the user ID and name from the selected row
        user_id_item = table_widget.item(selected_row, 0)
        user_name_item = table_widget.item(selected_row, 1)
        user_id = user_id_item.text().split('-')[1]  # Extracts the numeric ID
        user_name = user_name_item.text()  # Gets the user's name

        # Confirm deletion with the user's name
        reply = QMessageBox.question(self, "Delete User", f"Delete {user_name} from the existing users?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Delete user from the database
            self.users_c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self.users_conn.commit()

            # Remove the row from the table
            table_widget.removeRow(selected_row)

            QMessageBox.information(self, "User Deleted", f"{user_name} has been deleted successfully.")

    def open_edit_user_window(self, table_widget):
        """Opens a dialog to edit the selected user's information or prompts if no selection."""
        selected_row = table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a user to edit.")
            return

        # Retrieve selected user ID
        user_id_item = table_widget.item(selected_row, 0)
        user_id = user_id_item.text().split('-')[1]  # Extracts numeric ID

        # Fetch current user information from the database
        self.users_c.execute("SELECT name, company, position, phone, email FROM users WHERE user_id = ?", (user_id,))
        user_data = self.users_c.fetchone()
        current_name, current_company, current_position, current_phone, current_email = user_data

        # Open edit dialog with current user information
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle("Edit User")
        edit_dialog.setGeometry(300, 300, 300, 200)

        layout = QFormLayout()

        name_input = QLineEdit()
        name_input.setText(current_name)
        company_input = QLineEdit()
        company_input.setText(current_company)
        position_input = QLineEdit()
        position_input.setText(current_position)
        phone_input = QLineEdit()
        phone_input.setText(current_phone)
        email_input = QLineEdit()
        email_input.setText(current_email)

        layout.addRow("Name :", name_input)
        layout.addRow("Company :", company_input)
        layout.addRow("Position :", position_input)
        layout.addRow("Phone :", phone_input)
        layout.addRow("Email :", email_input)

        save_button = QPushButton(" Save ")
        save_button.clicked.connect(lambda: self.save_user_edits(
            user_id, name_input.text(), company_input.text(),
            position_input.text(), phone_input.text(),
            email_input.text(), edit_dialog, table_widget, selected_row
        ))
        layout.addWidget(save_button)
        edit_dialog.setLayout(layout)
        edit_dialog.exec()

    def save_user_edits(self, user_id, name, company, position, phone, email, dialog, table_widget, row):
        """Saves the edited user information to the database and updates the table."""
        # Update the users table with the new values
        self.users_c.execute(
            "UPDATE users SET name = ?, company = ?, position = ?, phone = ?, email = ? WHERE user_id = ?",
            (name, company, position, phone, email, user_id)
        )
        self.users_conn.commit()
        QMessageBox.information(self, "Update", f"User {user_id} updated successfully!")

        # Update the table widget with the new values
        table_widget.setItem(row, 1, QTableWidgetItem(name))  # Update name column in the table
        # Add additional columns as needed if you display more fields

        dialog.close()

    def make_default_user(self, user_id):
        """Sets the selected user as the default user after confirming with the user."""
        try:
            # Retrieve the user's name based on user_id
            self.users_c.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
            user_name = self.users_c.fetchone()

            if user_name:  # Ensure the user was found
                user_name = user_name[0]  # Extract the name from the tuple

                # Show confirmation dialog
                reply = QMessageBox.question(
                    self,
                    "Confirm Default User",
                    f"Are you sure you want to make {user_name} the current default user?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                # Proceed only if the user confirmed
                if reply == QMessageBox.StandardButton.Yes:
                    # Clear any existing default user
                    self.users_c.execute("UPDATE users SET is_default = 0 WHERE is_default = 1")

                    # Set the new default user
                    self.users_c.execute("UPDATE users SET is_default = 1 WHERE user_id = ?", (user_id,))
                    self.users_conn.commit()

                    QMessageBox.information(self, "Default User", f"{user_name} has been set as the default user.")
            else:
                QMessageBox.warning(self, "User Not Found", "The selected user does not exist.")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred: {e}")

    def show_user_information_dialog(self):
        """Opens the User Information Window with validation for phone and email fields."""
        user_info_dialog = QDialog(self)
        user_info_dialog.setWindowTitle("New User Information")
        user_info_dialog.setGeometry(200, 200, 300, 200)

        # User information input fields
        form_layout = QFormLayout()
        name_input = QLineEdit()
        form_layout.addRow(QLabel("Name :"), name_input)
        company_input = QLineEdit()
        form_layout.addRow(QLabel("Company :"), company_input)
        position_input = QLineEdit()
        form_layout.addRow(QLabel("Position :"), position_input)
        phone_input = QLineEdit()
        form_layout.addRow(QLabel("User Phone :"), phone_input)
        email_input = QLineEdit()
        form_layout.addRow(QLabel("Email :"), email_input)

        # Submit button
        button_layout = QHBoxLayout()
        submit_button = QPushButton(" Submit ")

        # Lambda function to validate phone and email fields
        submit_button.clicked.connect(lambda: self.validate_and_submit_user_info(
            name_input, company_input, position_input, phone_input, email_input, user_info_dialog))

        button_layout.addStretch()
        button_layout.addWidget(submit_button)
        button_layout.addStretch()

        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

        user_info_dialog.setLayout(main_layout)
        user_info_dialog.exec()

    # Add this helper method for validation
    def validate_and_submit_user_info(self, name_input, company_input, position_input, phone_input, email_input,
                                      dialog):
        """Validates phone and email inputs, and displays an error message if validation fails."""
        # Check if all required fields are filled
        if not all([name_input.text(), company_input.text(), position_input.text(),
                    phone_input.text(), email_input.text()]):
            QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return

        # Validate phone number: Check that it contains only digits
        if not phone_input.text().isdigit():
            QMessageBox.warning(self, "Input Error", "Please enter a valid numeric phone number.")
            return

        # Validate email format
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email_input.text()):
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address.")
            return

        # If validations pass, save the user information
        self.save_user_info(name_input, company_input, position_input, phone_input, email_input)

        QMessageBox.information(self, "Information Saved", "User information has been saved successfully.")
        dialog.close()

    def save_user_info(self, name_input, company_input, position_input, phone_input, email_input):
        """Saves the user information into the Users.db database."""
        # Get existing user codes
        self.users_c.execute("SELECT user_code FROM users")
        existing_codes = {row[0] for row in self.users_c.fetchall()}

        # Generate a new user code (User-1, User-2, etc.)
        new_user_code = f"User-{len(existing_codes) + 1}"

        # Insert new user into the users table
        self.users_c.execute('''INSERT INTO users (user_code, name, company, position, phone, email)
                                 VALUES (?, ?, ?, ?, ?, ?)''',
                             (new_user_code, name_input.text(), company_input.text(), position_input.text(),
                              phone_input.text(), email_input.text()))
        self.users_conn.commit()

    def load_data(self):
        """Loads data from the database into the table."""
        self.c.execute('SELECT * FROM materials')
        rows = self.c.fetchall()
        self.table.setRowCount(len(rows))

        # Initialize max widths for Mat ID and Material columns
        max_width_mat_id = 0
        max_width_trade = 0
        max_width_material = 0
        max_width_unit = 0
        max_width_vendor = 0
        max_width_email = 0

        font_metrics = QFontMetrics(self.table.font())  # Use table's font to calculate width

        for row_num, row_data in enumerate(rows):
            for col_num, data in enumerate(row_data[1:]):  # Skip the id column
                item_text = str(data)
                if col_num == 0:  # Mat ID column
                    max_width_mat_id = max(max_width_mat_id, font_metrics.horizontalAdvance(item_text))
                elif col_num == 1:  # Trade column
                    max_width_trade = max(max_width_trade, font_metrics.horizontalAdvance(item_text))
                elif col_num == 2:  # Material column
                    max_width_material = max(max_width_material, font_metrics.horizontalAdvance(item_text))
                elif col_num == 5:  # Unit column
                    max_width_unit = max(max_width_unit, font_metrics.horizontalAdvance(item_text))
                elif col_num == 6:  # Vendor column
                    max_width_vendor = max(max_width_vendor, font_metrics.horizontalAdvance(item_text))
                elif col_num == 8:  # Email column
                    max_width_email = max(max_width_email, font_metrics.horizontalAdvance(item_text))

                if col_num == 4:  # Assuming 'price' is the 5th column
                    # Check if data is a string, and remove commas if necessary
                    if isinstance(data, str):
                        data = float(data.replace(',', ''))
                    formatted_price = f"{data:,.2f}"
                    self.table.setItem(row_num, col_num, QTableWidgetItem(formatted_price))
                else:
                    self.table.setItem(row_num, col_num, QTableWidgetItem(item_text))

        # Set the column widths based on the widest entry for each column
        self.table.setColumnWidth(0, max_width_mat_id + 20)  # Mat ID column with padding
        self.table.setColumnWidth(1, max_width_trade + 20)  # Trade column with padding
        self.table.setColumnWidth(2, max_width_material + 20)  # Material column with padding
        self.table.setColumnWidth(3, 60)  # Set fixed width for Currency column
        self.table.setColumnWidth(5, max_width_unit + 20)  # Unit column with padding
        self.table.setColumnWidth(6, max_width_vendor + 20)  # Vendor column with padding
        self.table.setColumnWidth(8, max_width_email + 20)  # Email column with padding

    def populate_currency_combo(self, combo_box):
        """Populates the currency dropdown with available currencies."""
        currencies = self.get_currency_list()
        combo_box.addItems([f"{code} - {name}" for code, name in currencies])

    def get_currency_list(self):
        """Fetches the list of currencies using pycountry."""
        return [(currency.alpha_3, currency.name) for currency in pycountry.currencies]

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
                         search_text in row[7].lower()]  # Vendor
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
        elif sort_index == 4:
            sort_column = 'vendor'

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

    def open_rfp_window(self):
        """Opens the RFP window with the vendor's email and lists all materials from that vendor."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a material to Request For its Price.")
            return

        # Get the vendor's email from the selected row
        vendor_email = self.table.item(selected_row, 8).text()  # Adjusted for the new column

        try:
            # Fetch the vendor's name from the materials.db database using the vendor_email
            self.c.execute("SELECT vendor FROM materials WHERE vendor_email = ?", (vendor_email,))
            vendor_info = self.c.fetchone()

            if not vendor_info:
                QMessageBox.warning(self, "Vendor Info Missing", "Vendor information could not be found.")
                return

            vendor_name = vendor_info[0]  # Assuming the vendor's name is in the first column of the materials table

            # Collect all materials by the same vendor
            materials = [self.table.item(row, 2).text() for row in range(self.table.rowCount())
                         if self.table.item(row, 8).text() == vendor_email]

            # Query the database for the user details
            self.users_c.execute("SELECT name, company, position, phone, email FROM users WHERE is_default = 1 LIMIT 1")
            user_info = self.users_c.fetchone()

            if not user_info:
                QMessageBox.warning(self, "User Info Missing",
                                    "No default user information found. Please set a default user.")
                return

            # Unpack user information
            user_name, company_name, user_position, user_phone, user_email = user_info

            # Create the email body with the list of materials
            material_list = "\n".join(f"{i + 1}.  {material}" for i, material in enumerate(materials))
            email_body_text = (
                f"Dear {vendor_name},\n\n"
                f"I would like to request your current prices for the following materials:\n\n"
                f"{material_list}\n\n"
                f"Acknowledgment of receipt would be highly appreciated.\n\n"
                f"Best regards,\n{user_name}.\n\n{company_name}\n{user_position}\n{user_phone}"
            )

            # Set up the RFP dialog
            rfq_dialog = QDialog(self)
            rfq_dialog.setWindowTitle("Request For Prices")
            rfq_dialog.setGeometry(200, 200, 400, 400)

            layout = QVBoxLayout()
            sender_label = QLabel(f"From: {user_email}")
            email_label = QLabel(f"To: {vendor_email}")
            layout.addWidget(sender_label)
            layout.addWidget(email_label)

            email_body = QTextEdit()
            email_body.setPlainText(email_body_text)
            layout.addWidget(email_body)

            # Add "Send Request" button with responsive layout
            button_layout = QHBoxLayout()
            send_button = QPushButton("Send Request")
            send_button.clicked.connect(lambda: self.send_email(user_email, vendor_email, email_body_text))
            button_layout.addStretch()  # Add space before the button
            button_layout.addWidget(send_button)
            button_layout.addStretch()  # Add space after the button
            layout.addLayout(button_layout)  # Add button layout to main layout

            rfq_dialog.setLayout(layout)
            rfq_dialog.exec()

        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred: {e}")

    def send_email(self, from_email, to_email, email_body_text):
        """Sends an email using the smtplib library with Mailtrap SMTP configuration."""

        # Mailtrap SMTP configuration
        smtp_server = "smtp.mailtrap.live"  # Mailtrap SMTP server
        port = 587
        login = "4cf01760c7fa731c57742f9671ba3732"  # Replace with your Mailtrap login
        password = "191986kil"  # Replace with your Mailtrap password

        # Query the database for the user details
        self.users_c.execute("SELECT name, company, position, phone, email FROM users WHERE is_default = 1 LIMIT 1")
        user_info = self.users_c.fetchone()

        if not user_info:
            QMessageBox.warning(self, "User Info Missing",
                                "No default user information found. Please set a default user.")
            return

        # Unpack user information
        user_name, company_name, user_position, user_phone, user_email = user_info

        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a material to Request For its Price.")
            return

        # Set up email message with MIMEText
        message = MIMEText(email_body_text, "plain")
        message["Subject"] = "Request For Prices"
        message["From"] = from_email
        message["To"] = to_email

        try:
            # Send the email via Mailtrap's SMTP server
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls()  # Secure the connection
                server.login(login, password)
                server.sendmail(from_email, to_email, message.as_string())

            QMessageBox.information(self, "Request Sent", "Your request has been sent successfully.")

        except Exception as e:
            QMessageBox.warning(self, "Email Error", f"Failed to send email: {e}")

    def open_new_material_window(self):
        """Opens a window to input a new material."""
        self.material_dialog = QDialog(self)
        self.material_dialog.setWindowTitle("New Material")
        self.material_dialog.setGeometry(200, 200, 300, 300)  # Updated height for new field

        layout = QFormLayout()
        self.trade_input = QLineEdit()
        self.material_name_input = QLineEdit()
        self.material_name_input.setAlignment(Qt.AlignmentFlag.AlignLeft)   # Text aligns left

        self.currency_input = QComboBox()
        self.populate_currency_combo(self.currency_input)  # Populate currency dropdown
        self.currency_input.setCurrentText("GHS - Ghana Cedi")  # default GHS currency
        self.currency_input.setMinimumWidth(150)  # Set minimum width for the combo box

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
        """Adds a new material to the database with validation checks."""

        # Ensure all required fields are filled
        if not all([self.trade_input.text(), self.material_name_input.text(),
                    self.currency_input.currentText(), self.price_input.text(),
                    self.unit_input.text(), self.vendor_input.text(),
                    self.vendor_phone_input.text(), self.vendor_email_input.text()]):
            QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return

        try:
            # Ensure price is a valid number
            price = float(self.price_input.text())
            formatted_price = f"{price:,.2f}"
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number for the price.")
            return

        # Validate that the phone number contains only numbers
        if not self.vendor_phone_input.text().isdigit():
            QMessageBox.warning(self, "Input Error", "Please enter a valid numeric phone number.")
            return

        # Validate email format
        vendor_email = self.vendor_email_input.text()
        if not self.is_valid_email(vendor_email):
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address.")
            return

        # Get other field values
        trade = self.trade_input.text()
        material_name = self.material_name_input.text()
        currency = self.currency_input.currentText().split(' - ')[0]  # Get the currency code
        unit = self.unit_input.text()
        vendor = self.vendor_input.text()
        vendor_phone = self.vendor_phone_input.text()
        price_date = self.price_date_input.text()  # Get date as string

        # Generate new mat_id by finding the next available number in the MAT- format
        self.c.execute("SELECT mat_id FROM materials WHERE mat_id LIKE 'MAT-%'")
        existing_ids = {int(id.split('-')[1]) for id, in self.c.fetchall() if id.split('-')[1].isdigit()}
        new_id = 1
        while new_id in existing_ids:
            new_id += 1
        mat_id = f'MAT-{new_id}'

        # Insert into the database
        self.c.execute('''INSERT INTO materials (mat_id, trade, material_name, currency, price, unit, vendor, vendor_phone, vendor_email, price_date) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (mat_id, trade, material_name, currency, formatted_price, unit, vendor, vendor_phone,
                        vendor_email, price_date))
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
        self.material_dialog.setGeometry(200, 200, 300, 300)  # Updated height for new field

        layout = QFormLayout()
        self.trade_input = QLineEdit(trade)
        self.material_name_input = QLineEdit(material_name)
        self.material_name_input.setAlignment(Qt.AlignmentFlag.AlignLeft)   # Text aligns left


        # Populate currency dropdown
        self.currency_input = QComboBox()
        self.populate_currency_combo(self.currency_input)

        self.currency_input.setMinimumWidth(150)  # Set minimum width for the combo box

        # Construct the expected currency format (e.g., "GHS - Ghana Cedi")
        currency_text = f"{currency} - {pycountry.currencies.get(alpha_3=currency).name}"

        # Find the exact text match in the ComboBox and set it
        currency_index = self.currency_input.findText(currency_text)
        if currency_index != -1:
            self.currency_input.setCurrentIndex(currency_index)
        else:
            print(f"Currency '{currency_text}' not found in ComboBox items. Please check formatting.")

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
        """Updates the selected material in the database with validation checks."""

        # Ensure all required fields are filled
        if not all([self.trade_input.text(), self.material_name_input.text(),
                    self.currency_input.currentText(), self.price_input.text(),
                    self.unit_input.text(), self.vendor_input.text(),
                    self.vendor_phone_input.text(), self.vendor_email_input.text()]):
            QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return

        try:
            # Remove commas to safely convert to float and ensure price is valid
            price = float(self.price_input.text().replace(',', ''))
            formatted_price = f"{price:,.2f}"
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number for the price.")
            return

        # Validate that the phone number contains only numbers
        if not self.vendor_phone_input.text().isdigit():
            QMessageBox.warning(self, "Input Error", "Please enter a valid numeric phone number.")
            return

        # Validate email format
        vendor_email = self.vendor_email_input.text()
        if not self.is_valid_email(vendor_email):
            QMessageBox.warning(self, "Input Error", "Please enter a valid email address.")
            return

        # Get other field values
        trade = self.trade_input.text()
        material_name = self.material_name_input.text()
        currency = self.currency_input.currentText().split(' - ')[0]  # Get the currency code
        unit = self.unit_input.text()
        vendor = self.vendor_input.text()
        vendor_phone = self.vendor_phone_input.text()
        price_date = self.price_date_input.text()  # Get updated date

        # Update in the database
        self.c.execute('''UPDATE materials SET trade=?, material_name=?, currency=?, price=?, unit=?, vendor=?, vendor_phone=?, vendor_email=?, price_date=? 
                          WHERE mat_id=?''',
                       (trade, material_name, currency, formatted_price, unit, vendor, vendor_phone, vendor_email,
                        price_date, mat_id))
        self.conn.commit()
        self.load_data()  # Reload data to display updated list
        self.material_dialog.close()

    def duplicate_material(self):
        """Duplicates the selected material in the database with a new unique Mat ID."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a material to duplicate.")
            return

        # Retrieve the Mat ID and Material Name for the confirmation message
        mat_id = self.table.item(selected_row, 0).text()  # Mat ID
        material_name = self.table.item(selected_row, 2).text()  # Material Name

        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Confirm Duplication",
            f"Are you sure you want to duplicate [{mat_id}] {material_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return  # Cancel duplication if user selects 'No'

        try:
            # Retrieve current material details
            trade = self.table.item(selected_row, 1).text()
            material_name = self.table.item(selected_row, 2).text()
            currency = self.table.item(selected_row, 3).text()
            price = self.table.item(selected_row, 4).text().replace(',', '')  # Remove commas for conversion
            unit = self.table.item(selected_row, 5).text()
            vendor = self.table.item(selected_row, 6).text()
            vendor_phone = self.table.item(selected_row, 7).text()
            vendor_email = self.table.item(selected_row, 8).text()
            price_date = self.table.item(selected_row, 9).text()

            # Generate a new unique Mat ID by finding the maximum existing suffix
            self.c.execute("SELECT mat_id FROM materials WHERE mat_id LIKE 'MAT-%'")
            existing_ids = [int(id.split('-')[1]) for id, in self.c.fetchall() if id.split('-')[1].isdigit()]
            new_id = max(existing_ids) + 1 if existing_ids else 1
            new_mat_id = f'MAT-{new_id}'

            # Insert duplicated material into the database
            self.c.execute('''INSERT INTO materials (mat_id, trade, material_name, currency, price, unit, vendor, 
                              vendor_phone, vendor_email, price_date) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (new_mat_id, trade, material_name, currency, price, unit, vendor, vendor_phone,
                            vendor_email, price_date))
            self.conn.commit()

            # Reload data to display updated list with duplicated entry
            self.load_data()
            QMessageBox.information(self, "Duplication Successful",
                                    f"Material duplicated successfully with Mat ID {new_mat_id}")

        except Exception as e:
            QMessageBox.critical(self, "Duplication Error", f"An error occurred while duplicating the material: {e}")

    def delete_material(self):
        """Deletes the selected material from the database."""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a material to delete.")
            return

        mat_id = self.table.item(selected_row, 0).text()    # Mat ID
        material_name = self.table.item(selected_row, 2).text()  # Material Name

        reply = QMessageBox.question(self, 'Delete Material',
                                     f'Are you sure you want to delete [{mat_id}] {material_name}?',
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
