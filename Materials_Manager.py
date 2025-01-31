import requests
import json
import os
import sys
import sqlite3
import pandas as pd
import openpyxl
import re
import pycountry
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFontMetrics, QPixmap
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem,
                             QDialog, QTextEdit, QFormLayout, QLineEdit, QSizePolicy,
                             QMessageBox, QFileDialog, QComboBox, QDateEdit, QRadioButton, QButtonGroup, QSpacerItem
                             )

class BasicPricelist(QMainWindow):
    def __init__(self):
        """Initializes the GUI and database."""
        super().__init__()
        self.initUI()
        self.initDB()

    def initUI(self):
        """Sets up the user interface."""

        # Define the path to the icons folder
        icon_folder_path = os.path.join(os.path.dirname(__file__), "images")

        self.setWindowTitle('Materials Manager v.1.0')
        self.setGeometry(50, 50, 1400, 750)

        # Create an icon for the window.
        window_icon_path = os.path.join(icon_folder_path, "materials-manager.png")
        self.setWindowIcon(QtGui.QIcon(window_icon_path))

        # Tool Bar
        self.toolBar = QtWidgets.QToolBar(self)  # Assign self as parent
        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        # Set the icon size for the toolbar (e.g., 32x32 pixels)
        self.toolBar.setIconSize(QtCore.QSize(32, 32))  # Increase size to your preference

        # Helper function to create a QToolButton with an icon
        def create_tool_button_with_icon(icon_name, text, callback):
            """
            Creates a GUI button with an icon from a specified file name and sets a callback function when clicked.

            Args:
                icon_name (str): The name of the icon file (e.g., 'my_icon.ico').
                text (str): The text label or title for the button.
                callback (callable): A function to be called when the button is clicked.

            Returns:
                QToolButton: An object containing an icon and a text label with the specified text and icon.

            Example:
                To create a button with the ' Materials Manager' text and a click handler, you can use:
                >>> btn = create_tool_button_with_icon('my_icon.ico', 'Materials Manager', lambda btn: print("Button clicked"))
            """

            icon = QtGui.QIcon()
            icon_path = os.path.join(icon_folder_path, icon_name)
            icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)

            button = QtWidgets.QToolButton(self)
            button.setIcon(icon)
            button.setText(text)
            button.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)  # Tooltip beneath icon
            button.clicked.connect(callback)

            return button

        # Adding tool buttons with icons to the toolbar
        jobs_button = create_tool_button_with_icon("job.png", "Job", self.open_jobs_info_window)
        self.toolBar.addWidget(jobs_button)
        self.toolBar.addSeparator()  # Separator between icons

        jobs_list_button = create_tool_button_with_icon("job-list.png", "Jobs List", self.open_jobs_list)
        self.toolBar.addWidget(jobs_list_button)
        self.toolBar.addSeparator()

        user_button = create_tool_button_with_icon("user.png", "User", self.open_user_info_window)
        self.toolBar.addWidget(user_button)
        self.toolBar.addSeparator()

        new_material_button = create_tool_button_with_icon("new-material.png", "New Material",
                                                           self.open_new_material_window)
        self.toolBar.addWidget(new_material_button)
        self.toolBar.addSeparator()

        edit_material_button = create_tool_button_with_icon("edit-material.png", "Edit Material",
                                                            self.open_edit_material_window)
        self.toolBar.addWidget(edit_material_button)
        self.toolBar.addSeparator()

        duplicate_material_button = create_tool_button_with_icon("duplicate-material.png", "Duplicate Material",
                                                                 self.duplicate_material)
        self.toolBar.addWidget(duplicate_material_button)
        self.toolBar.addSeparator()

        delete_material_button = create_tool_button_with_icon("delete.png", "Delete Material", self.delete_material)
        self.toolBar.addWidget(delete_material_button)
        self.toolBar.addSeparator()

        vendors_button = create_tool_button_with_icon("vendors.png", "Vendor Management", self.show_vendor_list_window)
        self.toolBar.addWidget(vendors_button)
        self.toolBar.addSeparator()

        rfp_button = create_tool_button_with_icon("rfp.png", "Request For Vendors Prices", self.open_rfp_window)
        self.toolBar.addWidget(rfp_button)
        self.toolBar.addSeparator()

        compare_button = create_tool_button_with_icon("price-comparison.png", "Compare Vendors Price",
                                                      self.open_compare_window)
        self.toolBar.addWidget(compare_button)
        self.toolBar.addSeparator()

        export_excel_button = create_tool_button_with_icon("export-to-excel.png", "Export to Excel",
                                                           self.export_to_excel)
        self.toolBar.addWidget(export_excel_button)
        self.toolBar.addSeparator()

        import_excel_button = create_tool_button_with_icon("import-from-excel.png", "Import from Excel",
                                                           self.import_from_excel)
        self.toolBar.addWidget(import_excel_button)
        self.toolBar.addSeparator()

        about_button = create_tool_button_with_icon("about.png", "About",
                                                           self.about)
        self.toolBar.addWidget(about_button)
        self.toolBar.addSeparator()

        main_layout = QVBoxLayout()

        # Create a single horizontal layout to hold both the default job and default user labels
        default_info_layout = QHBoxLayout()

        # ------------------- Default Job Section -------------------
        # Create the icon for the default job
        default_job_icon_label = QLabel()
        icon_path = os.path.join(icon_folder_path, "current-job.png")
        default_job_icon_label.setPixmap(
            QtGui.QPixmap(icon_path).scaled(30, 30, QtCore.Qt.AspectRatioMode.KeepAspectRatio))

        # Create the label for the job name
        self.default_job_label = QLabel()
        self.update_default_job_label("No existing Job selected")  # Placeholder text for now
        self.default_job_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        # Add the icon and label to the layout
        default_info_layout.addWidget(default_job_icon_label)
        default_info_layout.addWidget(self.default_job_label)

        # Add a horizontal spacer to push the labels to the left
        spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        default_info_layout.addItem(spacer)

        # ------------------- Default User Section -------------------
        # Create the icon for the default user
        default_user_icon_label = QLabel()
        icon_path = os.path.join(icon_folder_path, "user.png")
        default_user_icon_label.setPixmap(
            QtGui.QPixmap(icon_path).scaled(30, 30, QtCore.Qt.AspectRatioMode.KeepAspectRatio))

        # Create the label for the user
        self.default_user_label = QLabel()
        self.update_default_user_label("No existing User selected")  # Placeholder text for now
        self.default_user_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        # Add the icon and label to the layout
        default_info_layout.addWidget(default_user_icon_label)
        default_info_layout.addWidget(self.default_user_label)

        # Add a horizontal spacer to push the labels to the left
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        default_info_layout.addItem(spacer)

        # Add the combined layout to the main layout
        main_layout.addLayout(default_info_layout)

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
        self.table.setColumnCount(12)  # Updated to 12 columns to match the header count
        self.table.setHorizontalHeaderLabels(
            ['Mat ID', 'Trade', 'Material', 'Currency', 'Price', 'Unit', 'Vendor', 'Phone', 'Email', 'Location',
             'Price Date', 'Comment'])  # Correct number of columns
        main_layout.addWidget(self.table)

        # ----------------- bottom label --------------------------------
        # Create the label for the job file location
        self.job_file_location_label = QLabel()

        # Set the text to the current working directory
        current_directory = os.getcwd()  # Get the current working directory
        self.job_file_location_label.setText(f"Job File Location: {current_directory}")

        # Optionally, align it to the left
        self.job_file_location_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        # Add a spacer before the label if you want the label centered or aligned to a specific area
        bottom_spacer = QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Add the spacer and the label to the layout
        main_layout.addItem(bottom_spacer)
        main_layout.addWidget(self.job_file_location_label)


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
            vendor_location TEXT,
            price_date TEXT,
            comment TEXT
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

        # Initialize Jobs database
        self.jobs_conn = sqlite3.connect('jobs.db')
        self.jobs_c = self.jobs_conn.cursor()
        self.jobs_c.execute('''CREATE TABLE IF NOT EXISTS jobs (
                    job_id INTEGER PRIMARY KEY,
                    job_code TEXT UNIQUE,
                    job_name TEXT,
                    client TEXT,
                    location TEXT
                )''')

        # Check if 'is_default' column exists; if not, add it
        try:
            self.jobs_c.execute("ALTER TABLE jobs ADD COLUMN is_default INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            # Column already exists, no need to add it
            pass

        self.jobs_conn.commit()

    def check_user(self):
        # Query the users.db for the current user
        try:
            self.users_c.execute("SELECT name FROM users WHERE is_default = 1 LIMIT 1")
            user = self.users_c.fetchone()

            if user:
                # Return only the user's name
                return user[0]
            else:
                print("No default user found.")
                return None
        except Exception as e:
            print(f"Error checking user: {str(e)}")
            return None

    def authorized_users_to_post_API(self):
        authorized_users = ["kil", "pat"]   #todo change user.
        return authorized_users

    def update_json(self):
        # Check current user if is in the list of authorized_users, if yes, update_json, else don't
        current_user = self.check_user()

        if current_user in self.authorized_users_to_post_API():

            # Proceed with JSON update if the user is authorized
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [table[0] for table in cursor.fetchall()]

                all_data = {}
                for table in tables:
                    df = pd.read_sql_query(f"SELECT * FROM {table}", self.conn)
                    all_data[table] = df.to_dict(orient="records")

                if all_data:
                    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
                    json_path = os.path.join(parent_dir, "materials-data.json")
                    with open(json_path, "w", encoding="utf-8") as json_file:
                        json.dump(all_data, json_file, indent=4, ensure_ascii=False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update JSON file: {str(e)}")

            print(f"{current_user} is authorized to post to API.")

            # post json file to API
            self.post_json_to_API()

        else:
            print(f"{current_user} is not authorized to post to API.")

    def post_json_to_API(self):

        # Read the materials-data.json file
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
        json_path = os.path.join(parent_dir, "materials-data.json")

        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Post the data to the API root `/`
        response = requests.post("https://mm-api-rz05.onrender.com", json=data)

        # Check the response
        if response.status_code == 200:
            print("Data uploaded successfully.")
        else:
            print(f"Failed to upload data: {response.status_code} - {response.text}")


    def update_default_job_label(self, job_name):
        """Updates the current job label with the job name (db_file)."""
        self.default_job_label.setText(f"Current Job: \t{job_name}")

        if job_name == "No existing Job selected":
            # Set text color to red for the placeholder text
            self.default_job_label.setStyleSheet("color: red;")
        else:
            # Set text color to blue once a job is selected
            self.default_job_label.setStyleSheet("color: blue;")

    def update_default_user_label(self, user_name):
        """Updates the current job label with the job name (db_file)."""
        self.default_user_label.setText(f"Current User: \t{user_name}")

        if user_name == "No existing User selected":
            # Set text color to red for the placeholder text
            self.default_user_label.setStyleSheet("color: red;")
        else:
            # Set text color to blue once a user is selected
            self.default_user_label.setStyleSheet("color: blue;")


    def open_jobs_info_window(self):
        """Displays options for New User and Existing User, with a responsive Submit button."""
        job_type_dialog = QDialog(self)
        job_type_dialog.setWindowTitle("Select Job Type")
        job_type_dialog.setGeometry(200, 200, 200, 100)

        layout = QVBoxLayout()

        # Radio buttons for selecting job type
        new_job_radio = QRadioButton("New Job")
        existing_job_radio = QRadioButton("Existing Jobs")

        # Add the radio buttons to a button group for exclusive selection
        button_group = QButtonGroup(job_type_dialog)
        button_group.addButton(new_job_radio)
        button_group.addButton(existing_job_radio)

        layout.addWidget(new_job_radio)
        layout.addWidget(existing_job_radio)

        # Responsive layout for the Submit button
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Spacer on the left
        submit_button = QPushButton("Next")
        submit_button.clicked.connect(
            lambda: self.check_job_type_selection(new_job_radio, existing_job_radio, job_type_dialog))

        button_layout.addWidget(submit_button)  # Center button
        button_layout.addStretch()  # Spacer on the right

        layout.addLayout(button_layout)  # Add button layout to the main layout
        job_type_dialog.setLayout(layout)
        job_type_dialog.exec()

    def check_job_type_selection(self, new_job_radio, existing_job_radio, job_type_dialog):
        """Checks which radio button is selected and opens the appropriate window."""
        if new_job_radio.isChecked():
            job_type_dialog.close()  # Close the selection dialog
            self.show_job_information_dialog()  # Open the job information window
        elif existing_job_radio.isChecked():  # Check if the existing job radio is selected
            job_type_dialog.close()  # Close the selection dialog
            self.show_existing_jobs_window()  # Open the existing job window

    def show_job_information_dialog(self):
        """Opens the Job Information Window with location to save jobs database."""
        job_info_dialog = QDialog(self)
        job_info_dialog.setWindowTitle("New Job Information")
        job_info_dialog.setGeometry(200, 200, 400, 150)

        # User information input fields
        form_layout = QFormLayout()
        job_name_input = QLineEdit()
        job_name_input.setMinimumWidth(400)
        form_layout.addRow(QLabel("Job Name :"), job_name_input)
        client_input = QLineEdit()
        client_input.setMinimumWidth(400)
        form_layout.addRow(QLabel("Client :"), client_input)
        location_input = QLineEdit()
        location_input.setMinimumWidth(400)
        form_layout.addRow(QLabel("Location :"), location_input)


        # Submit button
        button_layout = QHBoxLayout()
        submit_button = QPushButton(" Submit ")

        # Lambda function to validate phone and email fields
        submit_button.clicked.connect(lambda: self.validate_and_submit_job_info(
            job_name_input, client_input, location_input, job_info_dialog))

        button_layout.addStretch()
        button_layout.addWidget(submit_button)
        button_layout.addStretch()

        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

        job_info_dialog.setLayout(main_layout)
        job_info_dialog.exec()

    # Add this helper method for validation
    def validate_and_submit_job_info(self, job_name_input, client_input, location_input, dialog):
        """Validates phone and email inputs, and displays an error message if validation fails."""
        # Check if all required fields are filled
        if not all([job_name_input.text(), client_input.text(), location_input.text()]):
            QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return

        # If validations pass, save the user information
        self.save_job_info(job_name_input, client_input, location_input)

        QMessageBox.information(self, "Information Saved", "Job information has been saved successfully.")
        dialog.close()

    def save_job_info(self, job_name_input, client_input, location_input):
        """Saves the job information into the Jobs.db database."""
        # Get existing user codes
        self.jobs_c.execute("SELECT job_code FROM jobs")
        existing_codes = {row[0] for row in self.jobs_c.fetchall()}

        # Generate a new job code (Job-1, Job-2, etc.)
        new_job_code = f"Job-{len(existing_codes) + 1}"

        # Insert new job into the jobs table
        self.jobs_c.execute('''INSERT INTO jobs (job_code, job_name, client, location)
                                 VALUES (?, ?, ?, ?)''',
                             (new_job_code, job_name_input.text(), client_input.text(), location_input.text()))
        self.jobs_conn.commit()

    def show_existing_jobs_window(self):
        """Shows the list of all existing jobs with 'Make Default', 'Edit', and 'Delete' buttons."""
        job_list_dialog = QDialog(self)
        job_list_dialog.setWindowTitle("Existing Jobs")
        job_list_dialog.setGeometry(200, 200, 800, 400)

        table_widget = QTableWidget()
        table_widget.setRowCount(0)
        table_widget.setColumnCount(3)
        table_widget.setHorizontalHeaderLabels(["Job ID", "Job Name", "Make Current"])

        # Fetch and populate data
        self.jobs_c.execute("SELECT job_id, job_name FROM jobs")
        jobs = self.jobs_c.fetchall()
        for row_idx, job in enumerate(jobs):


            table_widget.insertRow(row_idx)
            table_widget.setItem(row_idx, 0, QTableWidgetItem(f"Job-ID-{job[0]}"))
            table_widget.setItem(row_idx, 1, QTableWidgetItem(job[1]))
            table_widget.setColumnWidth(1, 400)

            make_default_job_button = QPushButton("Current Job")
            make_default_job_button.clicked.connect(lambda checked, job_id=job[0]: self.make_default_job(job_id))
            table_widget.setCellWidget(row_idx, 2, make_default_job_button)

        # Horizontal layout for table and buttons
        main_horizontal_layout = QHBoxLayout()
        main_horizontal_layout.addWidget(table_widget)

        # Vertical layout for edit and delete buttons
        button_layout = QVBoxLayout()
        edit_job_button = QPushButton("Edit Job")
        edit_job_button.clicked.connect(lambda: self.open_edit_job_window(table_widget))
        button_layout.addWidget(edit_job_button)

        delete_job_button = QPushButton("Delete Job")
        delete_job_button.clicked.connect(lambda: self.delete_selected_job(table_widget))  # Assuming delete function
        button_layout.addWidget(delete_job_button)

        button_layout.addStretch()  # Spacer at the bottom

        # Add the vertical button layout to the horizontal layout
        main_horizontal_layout.addLayout(button_layout)

        # Main vertical layout for the dialog
        main_layout = QVBoxLayout()
        main_layout.addLayout(main_horizontal_layout)

        # Layout for the close button
        close_button_layout = QHBoxLayout()
        close_button_layout.addStretch()  # Add stretch to center-align the button
        close_button = QPushButton("Close")
        close_button.clicked.connect(job_list_dialog.close)
        close_button_layout.addWidget(close_button)
        close_button_layout.addStretch()  # Add stretch to center-align the button

        # Add the close button layout to the main vertical layout
        main_layout.addLayout(close_button_layout)

        job_list_dialog.setLayout(main_layout)
        job_list_dialog.exec()

    def make_default_job(self, job_id):
        """Sets the selected job as the default job after confirming the job."""
        try:
            # Retrieve the job's name based on job_id
            self.jobs_c.execute("SELECT job_name FROM jobs WHERE job_id = ?", (job_id,))
            job_name = self.jobs_c.fetchone()

            if job_name:  # Ensure the job was found
                job_name = job_name[0]  # Extract the name from the tuple

                # Show confirmation dialog
                reply = QMessageBox.question(
                    self,
                    "Confirm Default Job",
                    f"Are you sure you want to make {job_name} the current default job?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                # Proceed only if the job is confirmed
                if reply == QMessageBox.StandardButton.Yes:
                    # Clear any existing default job
                    self.jobs_c.execute("UPDATE jobs SET is_default = 0 WHERE is_default = 1")

                    # Set the new default job
                    self.jobs_c.execute("UPDATE jobs SET is_default = 1 WHERE job_id = ?", (job_id,))

                    # set the default job_name as a label
                    self.update_default_job_label(job_name)

                    self.jobs_conn.commit()

                    QMessageBox.information(self, "Default Job", f"{job_name} has been set as the default Job.")
            else:
                QMessageBox.warning(self, "User Not Found", "The selected job does not exist.")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred: {e}")

    def open_edit_job_window(self, table_widget):
        """Opens a dialog to edit the selected job's information or prompts if no selection."""
        selected_row = table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a Job to edit.")
            return

        # Retrieve selected job ID
        job_id_item = table_widget.item(selected_row, 0)
        if not job_id_item:
            QMessageBox.warning(self, "Selection Error", "No valid Job ID found.")
            return

        job_id_text = job_id_item.text()
        if not job_id_text.startswith("Job-ID-") or '-' not in job_id_text:
            QMessageBox.critical(self, "Error", "Invalid Job ID format.")
            return

        job_id = job_id_text.split('-')[-1]  # Safely extract the numeric ID

        # Fetch current job information from the database
        self.jobs_c.execute("SELECT job_name, client, location FROM jobs WHERE job_id = ?", (job_id,))
        job_data = self.jobs_c.fetchone()

        if not job_data:
            QMessageBox.critical(self, "Error", "Job not found in the database.")
            return

        current_job_name, current_client, current_location = job_data

        # Open edit dialog with current job information
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle("Edit Job")
        edit_dialog.setGeometry(200, 200, 400, 150)

        layout = QFormLayout()

        job_name_input = QLineEdit()
        job_name_input.setMinimumWidth(400)
        job_name_input.setText(current_job_name)
        client_input = QLineEdit()
        client_input.setMinimumWidth(400)
        client_input.setText(current_client)
        location_input = QLineEdit()
        location_input.setMinimumWidth(400)
        location_input.setText(current_location)

        layout.addRow("Job Name:", job_name_input)
        layout.addRow("Client:", client_input)
        layout.addRow("Location:", location_input)

        # Create a horizontal layout for the save button
        save_button_layout = QHBoxLayout()
        save_job_button = QPushButton("Save Job")
        save_job_button.setFixedWidth(150)  # Optional: Set a fixed width if you prefer
        save_job_button.clicked.connect(lambda: self.save_job_edits(
            job_id, job_name_input.text(), client_input.text(),
            location_input.text(), edit_dialog, table_widget, selected_row
        ))

        # Center the button within the horizontal layout
        save_button_layout.addWidget(save_job_button)
        save_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the horizontal layout to the main form layout
        layout.addRow(save_button_layout)

        edit_dialog.setLayout(layout)
        edit_dialog.exec()

    def save_job_edits(self, job_id, job_name, client, location, dialog, table_widget, row):
        """Saves the edited job information to the database and updates the table."""
        try:
            # Update the jobs table with the new values
            self.jobs_c.execute(
                "UPDATE jobs SET job_name = ?, client = ?, location = ? WHERE job_id = ?",
                (job_name, client, location, job_id)
            )
            self.jobs_conn.commit()

            QMessageBox.information(self, "Update", f"Job {job_id} updated successfully!")

            # Update the table widget with the new values
            table_widget.setItem(row, 1, QTableWidgetItem(job_name))  # Update job name
            # Add additional columns as needed:
            # table_widget.setItem(row, 2, QTableWidgetItem(client))  # Example for client column
            # table_widget.setItem(row, 3, QTableWidgetItem(location))  # Example for location column

            dialog.close()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Failed to update job: {str(e)}")

    def delete_selected_job(self, table_widget):
        """Deletes the selected job from the database and removes the row from the table."""
        # Get the selected row
        selected_row = table_widget.currentRow()

        # Check if a row is selected
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a job to delete.")
            return

        # Retrieve the job ID and name from the selected row
        job_id_item = table_widget.item(selected_row, 0)
        job_name_item = table_widget.item(selected_row, 1)

        if not job_id_item or not job_name_item:
            QMessageBox.warning(self, "Selection Error", "Unable to retrieve job information.")
            return

        job_id = job_id_item.text().replace("Job-ID-", "")  # Remove prefix to get the numeric ID
        job_name = job_name_item.text()

        # Confirm deletion with the job's name
        reply = QMessageBox.question(self, "Delete Job", f"Delete {job_name} from the existing jobs?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete the job from the database
                self.jobs_c.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
                self.jobs_conn.commit()

                # Verify deletion
                self.jobs_c.execute("SELECT COUNT(*) FROM jobs WHERE job_id = ?", (job_id,))
                if self.jobs_c.fetchone()[0] == 0:
                    # Remove the row from the table
                    table_widget.removeRow(selected_row)
                    QMessageBox.information(self, "Job Deleted", f"{job_name} has been deleted successfully.")
                else:
                    QMessageBox.warning(self, "Deletion Failed", f"Failed to delete {job_name}. Please try again.")
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Database Error", f"An error occurred: {e}")

    def open_jobs_list(self):
        """Lists all job-related databases in the current working directory with options to open or delete."""
        try:
            # Step 1: Get all .db files in the current working directory
            db_files = [f for f in os.listdir(os.getcwd()) if f.endswith('.db') and f.startswith('Job-ID')]

            if not db_files:
                QMessageBox.information(self, "No Job Databases Found",
                                        "No job-related databases were found in the current directory.")
                return

            # Step 2: Create a dialog window to display the job databases
            dialog = QDialog(self)
            dialog.setWindowTitle("Jobs List")
            dialog.setGeometry(200, 200, 600, 400)

            layout = QVBoxLayout(dialog)  # Main layout to hold everything

            # Create a table to display the database files only
            table = QTableWidget()
            table.setColumnCount(1)  # Only one column to show the database filename
            table.setHorizontalHeaderLabels(["Database File"])
            table.setRowCount(len(db_files))

            for row, db_file in enumerate(db_files):
                table.setItem(row, 0, QTableWidgetItem(db_file))  # Display the full database filename

            # Adjust column width to fit contents dynamically
            table.resizeColumnsToContents()

            # Step 3: Create a horizontal layout for the table and the buttons
            table_button_layout = QHBoxLayout()  # Horizontal layout for table and buttons

            # Add the table to the left part of the horizontal layout
            table_button_layout.addWidget(table)

            # Create a vertical layout for the buttons (Open/Delete)
            button_layout = QVBoxLayout()  # Vertical layout for the buttons

            open_button = QPushButton("Open Job")
            open_button.clicked.connect(lambda: self.open_job_window(table, dialog))

            delete_button = QPushButton("Delete Job")
            delete_button.clicked.connect(lambda: self.handle_job_action(table, "delete", dialog))

            # Add buttons to the vertical layout
            button_layout.addWidget(open_button)
            button_layout.addWidget(delete_button)

            # Add a vertical spacer below the delete button
            spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Fixed,
                                 QSizePolicy.Policy.Expanding)  # Corrected QSizePolicy
            button_layout.addItem(spacer)

            # Add the button layout to the right part of the horizontal layout
            table_button_layout.addLayout(button_layout)

            # Add the table and button layout to the main layout
            layout.addLayout(table_button_layout)

            # Create a horizontal layout for the close button at the bottom
            close_button_layout = QHBoxLayout()  # Horizontal layout for close button
            close_button_layout.addStretch(1)  # Add a stretchable space before the close button

            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.close)  # Close the dialog when clicked

            close_button_layout.addWidget(close_button)  # Add close button to layout
            close_button_layout.addStretch(1)  # Add a stretchable space after the close button

            # Add the close button layout to the main layout
            layout.addLayout(close_button_layout)

            dialog.setLayout(layout)  # Set the layout for the dialog

            # Show dialog
            dialog.exec()

        except Exception as e:
            # Handle unexpected errors
            QMessageBox.critical(self, "Error", f"An error occurred while listing job databases: {e}")

    def handle_job_action(self, table, action, dialog):
        """Handles the action based on the selected button: open or delete a job."""
        selected_row = table.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a job to perform the action.")
            return

        db_file = table.item(selected_row, 0).text()  # Get the selected job database filename

        if action == "open":
            # Open the job database (you can modify this action as needed)
            QMessageBox.information(self, "Open Job", f"Opening job database: {db_file}")
            # Perform the opening of the job database (e.g., loading the database or showing job details)
            dialog.accept()

        elif action == "delete":
            # Confirm deletion of the job database
            reply = QMessageBox.question(self, "Delete Job", f"Are you sure you want to delete {db_file}?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # Attempt to delete the selected job database file
                    os.remove(db_file)
                    QMessageBox.information(self, "Job Deleted", f"{db_file} has been deleted successfully.")
                    dialog.accept()  # Close the dialog after deletion
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete {db_file}: {e}")

    def open_job_window(self, table, parent_dialog):
        """Opens a Job window with the job name as the title and displays all data from the selected job database."""
        selected_row = table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a job to open.")
            return

        # Get the database file name
        db_file = table.item(selected_row, 0).text()

        try:
            # Open a connection to the selected job's database
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()

            # Fetch all table names in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            if not tables:
                QMessageBox.information(self, "No Tables Found", f"The database '{db_file}' contains no tables.")
                return

            # We are displaying data from only the first table (or you can choose another table)
            table_name = tables[0][0]  # Use the first table in the database

            # Create a new dialog window for the job
            job_dialog = QDialog(self)
            job_dialog.setWindowTitle(db_file)
            job_dialog.setGeometry(400, 200, 1000, 600)

            # Create the main layout for the dialog
            layout = QVBoxLayout(job_dialog)

            # Create a horizontal layout for the buttons (Export and Delete Material)
            button_layout = QHBoxLayout()
            button_layout.addStretch(1)  # Push buttons to the right

            # Delete Material button
            delete_button = QPushButton("Delete Material")
            delete_button.clicked.connect(lambda: self.job_delete_material(db_file))  # Pass db_file to delete_material
            button_layout.addWidget(delete_button)

            # Export Job to Excel button
            export_button = QPushButton("Export Job to Excel")
            export_button.clicked.connect(self.export_job_to_excel)  # Make sure this is defined elsewhere in your code
            button_layout.addWidget(export_button)

            # Add the button layout above the table layout
            layout.addLayout(button_layout)

            # Create a horizontal layout for the table
            table_layout = QHBoxLayout()

            # Create a table widget to display the contents of the selected table
            self.table_widget = QTableWidget()  # Store the table widget as an instance variable
            table_layout.addWidget(self.table_widget)

            # Fetch data from the selected table
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]

            # Exclude the first column (id) from the columns list
            columns = [col for col in columns if col.lower() != 'id']  # Modify 'id' if it's not exactly "id"

            # Populate the table widget with the data, excluding the id column
            self.table_widget.setRowCount(len(rows))
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)

            for row_idx, row_data in enumerate(rows):
                col_idx = 0  # Initialize column index
                for data_idx, data in enumerate(row_data):
                    # Skip the first column (id) in the data
                    if data_idx == 0:  # Assuming the id column is the first column
                        continue

                    # Format the price column if it's numeric
                    if isinstance(data, (int, float)):  # Check if the data is numeric
                        # Format price to 2 decimal places with commas
                        formatted_data = "{:,.2f}".format(data)
                        self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(formatted_data))
                    else:
                        self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

                    col_idx += 1

            # Adjust column widths
            self.table_widget.resizeColumnsToContents()

            # Add the table layout to the main layout
            layout.addLayout(table_layout)

            # Create a horizontal layout for the close button
            close_button_layout = QHBoxLayout()

            # Add stretchable space to center the button
            close_button_layout.addStretch(1)  # Adds flexible space before the button
            close_button = QPushButton("Close")
            close_button.clicked.connect(job_dialog.close)
            close_button_layout.addWidget(close_button)
            close_button_layout.addStretch(1)  # Adds flexible space after the button

            # Add close button layout to the main layout
            layout.addLayout(close_button_layout)

            job_dialog.setLayout(layout)
            job_dialog.exec()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Failed to load data from the database '{db_file}': {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def job_delete_material(self, db_file):
        """Deletes the selected material from the job's database."""
        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a material to delete.")
            return

        try:
            # Attempt to open a connection to the selected job's database
            conn = sqlite3.connect(db_file)

            cursor = conn.cursor()

            # Fetch and print the list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            if not tables:
                QMessageBox.information(self, "No Tables Found", f"The database '{db_file}' contains no tables.")
                return

            # We are displaying data from only the first table (or you can choose another table)
            table_name = tables[0][0]  # Use the first table in the database

            # Fetch the ID and name of the selected material (assuming ID is in the first column and name in the third)
            material_id = self.table_widget.item(selected_row, 0).text()  # Assuming the ID is in the first column
            material_name = self.table_widget.item(selected_row, 2).text()  # Assuming the name is in the third column

            if not material_id:  # Check for None or empty value
                QMessageBox.warning(self, "Error", "The selected material does not have an ID.")
                return

            # Confirm deletion with the user
            reply = QMessageBox.question(self, 'Delete Material',
                                         f'Are you sure you want to delete [{material_id}] {material_name}?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return

            # Delete the selected material from the db_file
            cursor.execute(f"DELETE FROM {table_name} WHERE mat_id=?", (material_id,))
            conn.commit()

            # Remove deleted row from table
            self.table_widget.removeRow(selected_row)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Failed to delete material: {e}")
            # Debug: Print the specific error message
            print(f"Database error: {e}")
        finally:
            # Ensure connection closure in all cases
            if 'conn' in locals() and conn:
                conn.close()

    def export_job_to_excel(self):
        """Exports the contents of the table widget to an Excel file."""
        # Access the table widget that displays the data
        table_widget = self.table_widget  # This assumes the table widget is named self.table_widget

        # Prepare the data from the table widget
        data = []
        for row in range(table_widget.rowCount()):
            row_data = []
            for col in range(table_widget.columnCount()):
                item = table_widget.item(row, col)
                row_data.append(item.text() if item is not None else "")  # Handle None values safely
            data.append(row_data)

        # Get the column names (headers)
        columns = [table_widget.horizontalHeaderItem(i).text() for i in range(table_widget.columnCount())]

        # Create a DataFrame with the data
        df = pd.DataFrame(data, columns=columns)

        # Prompt the user to choose where to save the Excel file
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx);;All Files (*)")
        if not file_path:
            return  # Exit if no file was chosen

        try:
            # Save the DataFrame to an Excel file
            df.to_excel(file_path, index=False)

            # Show success message
            QMessageBox.information(self, "Export Successful", f"Data exported successfully to {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred during export: {e}")

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
        submit_button.clicked.connect(
            lambda: self.check_user_type_selection(new_user_radio, existing_user_radio, user_type_dialog))
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
        user_list_dialog.setGeometry(200, 200, 600, 400)

        table_widget = QTableWidget()
        table_widget.setRowCount(0)
        table_widget.setColumnCount(3)
        table_widget.setHorizontalHeaderLabels(["User ID", "Name", "Make Current"])

        # Fetch and populate data
        self.users_c.execute("SELECT user_id, name FROM users")
        users = self.users_c.fetchall()
        for row_idx, user in enumerate(users):
            table_widget.insertRow(row_idx)
            table_widget.setItem(row_idx, 0, QTableWidgetItem(f"UserID-{user[0]}"))
            table_widget.setItem(row_idx, 1, QTableWidgetItem(user[1]))

            make_default_button = QPushButton("Current")
            make_default_button.clicked.connect(lambda checked, user_id=user[0]: self.make_default_user(user_id))
            table_widget.setCellWidget(row_idx, 2, make_default_button)

        # Horizontal layout for table and buttons
        main_horizontal_layout = QHBoxLayout()
        main_horizontal_layout.addWidget(table_widget)

        # Vertical layout for edit and delete buttons
        button_layout = QVBoxLayout()
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda: self.open_edit_user_window(table_widget))
        button_layout.addWidget(edit_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.delete_selected_user(table_widget))  # Assuming delete function
        button_layout.addWidget(delete_button)

        button_layout.addStretch()  # Spacer at the bottom

        # Add the vertical button layout to the horizontal layout
        main_horizontal_layout.addLayout(button_layout)

        # Main vertical layout for the dialog
        main_layout = QVBoxLayout()
        main_layout.addLayout(main_horizontal_layout)

        # Layout for the close button
        close_button_layout = QHBoxLayout()
        close_button_layout.addStretch()  # Add stretch to center-align the button
        close_button = QPushButton("Close")
        close_button.clicked.connect(user_list_dialog.close)
        close_button_layout.addWidget(close_button)
        close_button_layout.addStretch()  # Add stretch to center-align the button

        # Add the close button layout to the main vertical layout
        main_layout.addLayout(close_button_layout)

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
        edit_dialog.setGeometry(200, 200, 400, 200)

        layout = QFormLayout()

        name_input = QLineEdit()
        name_input.setMinimumWidth(400)
        name_input.setText(current_name)
        company_input = QLineEdit()
        company_input.setMinimumWidth(400)
        company_input.setText(current_company)
        position_input = QLineEdit()
        position_input.setMinimumWidth(400)
        position_input.setText(current_position)
        phone_input = QLineEdit()
        phone_input.setMinimumWidth(400)
        phone_input.setText(current_phone)
        email_input = QLineEdit()
        email_input.setMinimumWidth(400)
        email_input.setText(current_email)

        layout.addRow("Name :", name_input)
        layout.addRow("Company :", company_input)
        layout.addRow("Position :", position_input)
        layout.addRow("Phone :", phone_input)
        layout.addRow("Email :", email_input)

        # Create a horizontal layout for the save button
        save_button_layout = QHBoxLayout()
        save_button = QPushButton("Save User")
        save_button.setFixedWidth(150)  # Optional: Set a fixed width if needed
        save_button.clicked.connect(lambda: self.save_user_edits(
            user_id, name_input.text(), company_input.text(),
            position_input.text(), phone_input.text(),
            email_input.text(), edit_dialog, table_widget, selected_row
        ))

        # Center the button within the horizontal layout
        save_button_layout.addWidget(save_button)
        save_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the horizontal layout to the main form layout
        layout.addRow(save_button_layout)

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

                    # dynamically update default user label
                    self.update_default_user_label(user_name)

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
        user_info_dialog.setGeometry(200, 200, 400, 200)

        # User information input fields
        form_layout = QFormLayout()
        name_input = QLineEdit()
        name_input.setMinimumWidth(400)

        form_layout.addRow(QLabel("Name :"), name_input)
        company_input = QLineEdit()
        company_input.setMinimumWidth(400)

        form_layout.addRow(QLabel("Company :"), company_input)
        position_input = QLineEdit()
        position_input.setMinimumWidth(400)

        form_layout.addRow(QLabel("Position :"), position_input)
        phone_input = QLineEdit()
        phone_input.setMinimumWidth(400)

        form_layout.addRow(QLabel("User Phone :"), phone_input)
        email_input = QLineEdit()
        email_input.setMinimumWidth(400)

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
        max_width_location = 0
        max_width_comment = 0       # Comment column

        font_metrics = QFontMetrics(self.table.font())  # Use table's font to calculate width

        for row_num, row_data in enumerate(rows):
            for col_num, data in enumerate(row_data[1:]):  # Skip the id column
                # Convert data to string if it is not None
                item_text = '' if data is None else str(data)
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
                elif col_num == 9:  # Location column
                    max_width_location = max(max_width_location, font_metrics.horizontalAdvance(item_text))
                elif col_num == 11:  # comment column
                    max_width_comment = max(max_width_comment, font_metrics.horizontalAdvance(item_text))

                if col_num == 4:  # Assuming 'price' is the 5th column
                    # Check if data is a string, and remove commas if necessary
                    if isinstance(data, str):
                        data = float(data.replace(',', ''))
                    formatted_price = f"{data:,.2f}"
                    item = QTableWidgetItem(formatted_price)
                else:
                    item = QTableWidgetItem(item_text)

                self.table.setItem(row_num, col_num, item)

        # Set the column widths based on the widest entry for each column
        self.table.setColumnWidth(0, max_width_mat_id + 20)  # Mat ID column with padding
        self.table.setColumnWidth(1, max_width_trade + 20)  # Trade column with padding
        self.table.setColumnWidth(2, max_width_material + 20)  # Material column with padding
        self.table.setColumnWidth(3, 60)  # Set fixed width for Currency column
        self.table.setColumnWidth(5, max_width_unit + 20)  # Unit column with padding
        self.table.setColumnWidth(6, max_width_vendor + 20)  # Vendor column with padding
        self.table.setColumnWidth(8, max_width_email + 20)  # Email column with padding
        self.table.setColumnWidth(9, max_width_location + 20)  # Location column with padding
        self.table.setColumnWidth(11, max_width_comment + 20)  # Comment column with padding

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
        search_text = f"%{self.search_input.text().lower()}%"  # Add wildcards for SQL LIKE search

        try:
            # Perform the search query with placeholders
            query = """
                SELECT * FROM materials
                WHERE LOWER(trade) LIKE ?
                OR LOWER(material_name) LIKE ?
                OR LOWER(vendor) LIKE ?
            """
            self.c.execute(query, (search_text, search_text, search_text))
            rows = self.c.fetchall()

            # Populate the table with the filtered rows
            self.populate_table(rows)
        except sqlite3.Error as e:
            # Display an error message if the database query fails
            QMessageBox.critical(self, "Database Error", f"Failed to search materials: {e}")

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

    def open_compare_window(self):
        """Opens a window to compare vendor prices for the selected material."""
        try:
            # Get the selected row in the table
            selected_row = self.table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Selection Error", "Please select a material to compare.")
                return

            # Get the material name and other information from the selected row
            material_id = self.table.item(selected_row, 0).text()  # Assuming column 0 is mat_id
            material_name = self.table.item(selected_row, 2).text()  # Assuming column 2 is material_name

            # Query database to fetch all vendors and prices for the selected material
            try:
                self.c.execute('''SELECT mat_id, vendor, currency, price, unit, vendor_location, price_date, comment 
                                  FROM materials 
                                  WHERE material_name = ?''', (material_name,))
                results = self.c.fetchall()

            except sqlite3.Error as e:
                # Show an error message if there’s a database issue
                QMessageBox.critical(self, "Database Error", f"Error fetching data: {e}")
                return

            # Check if there is only one item in the database for this material
            if len(results) <= 1:
                QMessageBox.information(self, "Comparison not possible",
                                        "The selected material is the only item and has nothing to compare with.")
                return

            # Create a dialog window for comparison
            compare_dialog = QDialog(self)
            compare_dialog.setWindowTitle(f"Vendors Price Comparison")
            compare_dialog.setGeometry(200, 200, 1000, 600)

            # Layout for the comparison table
            layout = QVBoxLayout(compare_dialog)

            # Add filter drop-down
            filter_layout = QHBoxLayout()
            filter_label = QLabel(f"[{material_id}] : {material_name}\t\t\t\t\t\t\t\t\t\t\t\t\t\t Sort by Price :")
            filter_combo = QComboBox()
            filter_combo.addItems(["Low - High", "High - Low"])
            filter_layout.addWidget(filter_label)
            filter_layout.addWidget(filter_combo)
            layout.addLayout(filter_layout)

            # Table to display comparison data
            compare_table = QTableWidget()
            compare_table.setColumnCount(9)  # Increase the column count to 9 to include Comment
            compare_table.setHorizontalHeaderLabels(
                ["Mat ID", "Vendor", "Currency", "Price", "Unit", "Location", "Date", "Comment", "Allocation"])

            # Extract job_id and job_name for view in label
            self.jobs_c.execute("SELECT job_id, job_name FROM jobs WHERE is_default = 1")
            default_job = self.jobs_c.fetchone()

            job_id, job_name = default_job

            # Update the default job label
            self.update_default_job_label(job_name)

            # Function to populate the table with formatted prices
            def populate_table(data):
                compare_table.setRowCount(len(data))
                for row, (mat_id, vendor, currency, price, unit, vendor_location, price_date, comment) in enumerate(
                        data):
                    compare_table.setItem(row, 0, QTableWidgetItem(mat_id))
                    compare_table.setItem(row, 1, QTableWidgetItem(vendor))
                    compare_table.setItem(row, 2, QTableWidgetItem(currency))

                    # Format price to two decimal places with commas
                    formatted_price = "{:,.2f}".format(price)
                    compare_table.setItem(row, 3, QTableWidgetItem(formatted_price))

                    compare_table.setItem(row, 4, QTableWidgetItem(unit))
                    compare_table.setItem(row, 5, QTableWidgetItem(vendor_location))  # Add Location data
                    compare_table.setItem(row, 6, QTableWidgetItem(price_date))
                    compare_table.setItem(row, 7, QTableWidgetItem(comment))  # Add comment

                    # Add an "Assign Job" button
                    assign_job_button = QPushButton("Allocate to Job")
                    assign_job_button.clicked.connect(
                        lambda checked, material_id=mat_id: self.assign_material_to_job(material_id))
                    compare_table.setCellWidget(row, 8, assign_job_button)

            # Convert prices to float for accurate sorting
            try:
                results = [
                    (mat_id, vendor, currency, float(price.replace(',', '')) if isinstance(price, str) else price,
                     unit, vendor_location, price_date, comment)
                    for (mat_id, vendor, currency, price, unit, vendor_location, price_date, comment) in results]
            except Exception as e:
                # Show an error message if there’s an issue with data conversion
                QMessageBox.critical(self, "Data Error", f"Error processing data: {e}")
                return

            sorted_results = sorted(results, key=lambda x: x[3])
            populate_table(sorted_results)

            # Set default filter selection to "Low - High"
            filter_combo.setCurrentIndex(0)

            # Handle filter changes
            def on_filter_change():
                sorted_results = sorted(results, key=lambda x: x[3],
                                        reverse=(filter_combo.currentText() == "High - Low"))
                populate_table(sorted_results)

            filter_combo.currentIndexChanged.connect(on_filter_change)

            # Add the table to the layout
            layout.addWidget(compare_table)

            # Calculate average price if all currencies are the same
            unique_currencies = {currency for _, _, currency, _, _, _, _, _ in results}
            if len(unique_currencies) == 1:
                # Calculate average price
                average_price = sum(price for _, _, _, price, _, _, _, _ in results) / len(results)
                currency = unique_currencies.pop()
                average_price_label_text = f"Average Price : {currency} {average_price:,.2f}"
            else:
                # Display message if currencies vary
                average_price_label_text = "Average prices cannot be calculated due to currency variance."

            # Create and add the average price label
            average_price_label = QLabel(average_price_label_text)
            average_price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(average_price_label)

            # Add a close button at the bottom, center-aligned
            close_button_layout = QHBoxLayout()
            close_button_layout.addStretch(1)  # Add stretch to center-align
            close_button = QPushButton("Close")
            close_button.clicked.connect(compare_dialog.close)
            close_button_layout.addWidget(close_button)
            close_button_layout.addStretch(1)  # Add stretch to center-align

            # Add the close button layout to the main layout
            layout.addLayout(close_button_layout)
            compare_dialog.setLayout(layout)

            # Show the comparison dialog
            compare_dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def assign_material_to_job(self, material_id):
        """Assigns a selected material to the default job."""
        try:
            # Step 1: Retrieve the default job from jobs.db
            self.jobs_c.execute("SELECT job_id, job_name FROM jobs WHERE is_default = 1")
            default_job = self.jobs_c.fetchone()

            job_id, job_name = default_job

            if not default_job:
                QMessageBox.warning(self, "No Default Job", "No default job is set. Please set a default job first.")
                return

            # Step 2: Create a database file name using job_id and job_name
            job_db_name = f"Job-ID-{job_id}_{job_name.replace(' ', '_')}.db"

            # Step 3: Establish a connection to the job database (creates it if it doesn’t exist)
            job_conn = sqlite3.connect(job_db_name)
            job_c = job_conn.cursor()

            # Step 4: Create a table for assigned materials if it doesn’t already exist
            job_c.execute('''CREATE TABLE IF NOT EXISTS assigned_materials (
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
                                vendor_location TEXT,
                                price_date TEXT,
                                comment TEXT
                            )''')

            # Step 5: Fetch all material details from materials.db using the material_id
            self.c.execute(
                '''SELECT id, mat_id, trade, material_name, currency, price, unit, vendor, 
                          vendor_phone, vendor_email, vendor_location, price_date, comment 
                   FROM materials WHERE mat_id = ?''',
                (material_id,)
            )
            material_details = self.c.fetchone()

            if not material_details:
                QMessageBox.warning(self, "Material Not Found", "The selected material could not be found.")
                return

            # Step 6: Insert the material into the job-specific database
            job_c.execute('''INSERT OR IGNORE INTO assigned_materials 
                              (id, mat_id, trade, material_name, currency, price, unit, vendor, 
                               vendor_phone, vendor_email, vendor_location, price_date, comment)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          material_details)
            job_conn.commit()

            # Inform the user of successful assignment
            QMessageBox.information(
                self,
                "Material Assigned",
                f"Material ID: {material_id} has been successfully assigned to Job: {job_name}."
            )

        except sqlite3.Error as e:
            # Handle SQLite database errors
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")

        except Exception as e:
            # Handle unexpected errors
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred: {e}")

        finally:
            # Ensure connections are closed
            try:
                if 'job_conn' in locals():
                    job_conn.close()
            except Exception:
                pass

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
                                       'Email', 'Location', 'Price Date', 'Comment'])  # Updated column names
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Export Successful", f"Data exported successfully to {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"An error occurred during export: {e}")

    def import_from_excel(self):
        """Imports data from an Excel file, validates it, and populates the materials database without repeating items."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Excel Files (*.xlsx);;All Files (*)")
        if not file_path:  # Check if a file path was provided
            return

        # Ask the user how to handle duplicates: Skip or Update
        duplicate_action = QMessageBox.question(
            self, "Duplicate Handling", "How would you like to handle existing material IDs?\n\n"
                                        "Yes - Update existing records\nNo - Skip duplicates\nCancel - Abort import",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if duplicate_action == QMessageBox.StandardButton.Cancel:
            return  # Abort the import process

        try:
            # Read the Excel file into a DataFrame
            df = pd.read_excel(file_path)

            # Ensure that the Excel file has the correct columns
            expected_columns = ['Mat ID', 'Trade', 'Material', 'Currency', 'Price', 'Unit', 'Vendor', 'Phone',
                                'Email', 'Location', 'Price Date', 'Comment']
            missing_columns = [col for col in expected_columns if col not in df.columns]
            if missing_columns:
                QMessageBox.critical(self, "Import Error",
                                     f"The Excel file is missing the following columns: {', '.join(missing_columns)}.")
                return

            invalid_rows = []  # Track rows that fail validation
            skipped_mat_ids = []  # Track duplicates that are skipped
            updated_mat_ids = []  # Track duplicates that are updated
            inserted_mat_ids = []  # Track successfully inserted material IDs
            skipped_rows = []  # Store rows for skipped duplicates to add later

            # Iterate through the DataFrame and validate data before inserting it into the database
            for index, row in df.iterrows():
                mat_id = str(row['Mat ID'])  # Ensure mat_id is a string
                trade = row['Trade']
                material_name = row['Material']
                currency = row['Currency']
                price = row['Price']
                unit = row['Unit']
                vendor = row['Vendor']
                phone = row['Phone']
                email = row['Email']
                location = row['Location']
                price_date = row['Price Date']
                comment = row['Comment']

                # Perform data validation
                if not mat_id or not material_name or not trade:
                    invalid_rows.append(str(index + 2))  # +2 to adjust for Excel row numbers (1-based)
                    continue

                if not isinstance(price, (int, float)):
                    try:
                        price = float(str(price).replace(',', ''))  # Attempt to convert to a number
                    except ValueError:
                        invalid_rows.append(str(index + 2))
                        continue

                if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):  # Basic email validation
                    invalid_rows.append(str(index + 2))
                    continue

                # Check if the mat_id already exists in the database
                self.c.execute("SELECT COUNT(*) FROM materials WHERE mat_id = ?", (mat_id,))
                exists = self.c.fetchone()[0] > 0

                if exists:
                    if duplicate_action == QMessageBox.StandardButton.Yes:  # User chose to update duplicates
                        # Update the existing record
                        self.c.execute('''UPDATE materials
                                          SET trade = ?, material_name = ?, currency = ?, price = ?, unit = ?, 
                                              vendor = ?, vendor_phone = ?, vendor_email = ?, vendor_location = ?, price_date = ?, comment = ?
                                          WHERE mat_id = ?''',
                                       (trade, material_name, currency, price, unit, vendor, phone, email, location,
                                        price_date, comment, mat_id))
                        updated_mat_ids.append(mat_id)
                    else:
                        # Skip the duplicate but store the row for later insertion with a new mat_id
                        skipped_mat_ids.append(mat_id)
                        skipped_rows.append(row)
                else:
                    # If mat_id doesn't exist, insert the row
                    self.c.execute('''INSERT INTO materials (mat_id, trade, material_name, currency, price, unit,
                                                            vendor, vendor_phone, vendor_email, vendor_location, price_date, comment)
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (mat_id, trade, material_name, currency, price, unit, vendor, phone, email, location,
                                    price_date, comment))
                    inserted_mat_ids.append(mat_id)

            # Commit the changes to the database
            self.conn.commit()

            # If there are skipped rows, generate new mat_ids and insert them
            for row in skipped_rows:
                mat_id = self.generate_new_mat_id()  # Generate a new unique mat_id
                trade = row['Trade']
                material_name = row['Material']
                currency = row['Currency']
                price = row['Price']
                unit = row['Unit']
                vendor = row['Vendor']
                phone = row['Phone']
                email = row['Email']
                location = row['Location']
                price_date = row['Price Date']
                comment = row['Comment']

                # Insert the skipped row with the new mat_id
                self.c.execute('''INSERT INTO materials (mat_id, trade, material_name, currency, price, unit,
                                                        vendor, vendor_phone, vendor_email, vendor_location, price_date, comment)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               (mat_id, trade, material_name, currency, price, unit, vendor, phone, email, location,
                                price_date, comment))
                inserted_mat_ids.append(mat_id)

            # Commit the changes for the new inserts
            self.conn.commit()

            # Reload the data in the table to reflect new changes
            self.load_data()

            # Provide feedback to the user
            message = f"Data imported successfully from {file_path}.\n\n"
            if inserted_mat_ids:
                message += f"Inserted material IDs: {', '.join(map(str, inserted_mat_ids))}\n"
            if updated_mat_ids:
                message += f"Updated material IDs: {', '.join(map(str, updated_mat_ids))}\n"
            if skipped_mat_ids:
                message += f"Skipped material IDs (duplicates, now added with new IDs): {', '.join(map(str, skipped_mat_ids))}\n"
            if invalid_rows:
                message += f"Rows with validation errors: {', '.join(map(str, invalid_rows))}\n"

            QMessageBox.information(self, "Import Completed", message)

        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"An error occurred during import: {e}")

    def generate_new_mat_id(self):
        """Generate a new unique material ID in the format MAT-XXX."""
        # Fetch the maximum mat_id from the database and extract the numeric part
        self.c.execute("SELECT mat_id FROM materials WHERE mat_id LIKE 'MAT-%'")
        all_ids = [row[0] for row in self.c.fetchall()]

        if not all_ids:
            new_id = 1
        else:
            max_id = max([int(id.split('-')[1]) for id in all_ids])
            new_id = max_id + 1

        return f"MAT-{new_id}"

    def open_rfp_window(self):
        """Opens the RFP window, but first checks if a default user is selected."""

        try:
            # Query the database for the default user details
            self.users_c.execute("SELECT name, company, position, phone, email FROM users WHERE is_default = 1 LIMIT 1")
            user_info = self.users_c.fetchone()

            # Check if a default user exists
            if not user_info:
                QMessageBox.warning(self, "User Info Missing",
                                    "No default user information found. Please set a default user before proceeding.")
                return

            # Unpack user information if a default user is found
            user_name, company_name, user_position, user_phone, user_email = user_info

            # update the default user label
            self.update_default_user_label(user_name)

            # Proceed with the rest of the logic if a default user is selected
            selected_row = self.table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Selection Error", "Please select a material to Request For its Price.")
                return

            # Get the vendor's email from the selected row
            vendor_email = self.table.item(selected_row, 8).text()  # Adjusted for the new column

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

            # Create the email body with the list of materials
            material_list = "\n".join(f"{i + 1}.  {material}" for i, material in enumerate(materials))
            email_body_text = (
                f"From : {user_email}\n"
                f"To : {vendor_email}\n\n"
                f"Dear {vendor_name},\n\n"
                f"I would like to request for your current prices for the following materials:\n\n"
                f"{material_list}\n\n"
                f"Acknowledgment of receipt would be highly appreciated.\n\n"
                f"Best regards,\n{user_name}.\n\n{company_name}\n{user_position}\n{user_phone}"
            )

            # Set up the RFP dialog
            rfq_dialog = QDialog(self)
            rfq_dialog.setWindowTitle("Request For Vendors Prices")
            rfq_dialog.setGeometry(200, 200, 600, 600)

            layout = QVBoxLayout()
            email_body = QTextEdit()
            email_body.setPlainText(email_body_text)
            layout.addWidget(email_body)

            # Add a close button at the bottom, center-aligned
            close_button_layout = QHBoxLayout()
            close_button_layout.addStretch(1)  # Add stretch to center-align
            close_button = QPushButton("Close")
            close_button.clicked.connect(rfq_dialog.close)
            close_button_layout.addWidget(close_button)
            close_button_layout.addStretch(1)  # Add stretch to center-align

            # Add the close button layout to the main layout
            layout.addLayout(close_button_layout)
            rfq_dialog.setLayout(layout)

            rfq_dialog.exec()

        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred: {e}")

    def open_new_material_window(self):
        """Opens a window to input a new material."""
        self.material_dialog = QDialog(self)
        self.material_dialog.setWindowTitle("New Material")
        self.material_dialog.setGeometry(200, 200, 400, 300)  # Updated height for new field

        layout = QFormLayout()

        # Create input fields
        self.trade_input = QLineEdit()
        self.trade_input.setMinimumWidth(400)

        self.material_name_input = QLineEdit()
        self.material_name_input.setMinimumWidth(400)
        self.material_name_input.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Text aligns left

        self.currency_input = QComboBox()
        self.currency_input.setMinimumWidth(400)
        self.populate_currency_combo(self.currency_input)  # Populate currency dropdown
        self.currency_input.setCurrentText("GHS - Ghana Cedi")  # Default currency to GHS
        self.currency_input.setMinimumWidth(400)

        self.price_input = QLineEdit()
        self.price_input.setMinimumWidth(400)

        self.unit_input = QLineEdit()
        self.unit_input.setMinimumWidth(400)

        self.vendor_input = QLineEdit()
        self.vendor_input.setMinimumWidth(400)

        self.vendor_phone_input = QLineEdit()
        self.vendor_phone_input.setMinimumWidth(400)

        self.vendor_email_input = QLineEdit()
        self.vendor_email_input.setMinimumWidth(400)

        self.vendor_location_input = QLineEdit()
        self.vendor_location_input.setMinimumWidth(400)

        self.price_date_input = QDateEdit()  # New date input field
        self.price_date_input.setMinimumWidth(400)
        self.price_date_input.setDate(QDate.currentDate())  # Set default date to today
        self.price_date_input.setCalendarPopup(True)  # Show calendar popup for date selection

        self.vendor_comment_input = QLineEdit()
        self.vendor_comment_input.setMinimumWidth(400)

        # Add fields to the layout
        layout.addRow('Trade:', self.trade_input)
        layout.addRow('Material:', self.material_name_input)
        layout.addRow('Currency:', self.currency_input)
        layout.addRow('Price:', self.price_input)
        layout.addRow('Unit:', self.unit_input)
        layout.addRow('Vendor:', self.vendor_input)
        layout.addRow('Vendor Phone:', self.vendor_phone_input)
        layout.addRow('Vendor Email:', self.vendor_email_input)
        layout.addRow('Vendor Location:', self.vendor_location_input)
        layout.addRow('Price Date:', self.price_date_input)
        layout.addRow('Comment:', self.vendor_comment_input)

        # Create a horizontal layout for the Add Material button
        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Material")
        add_button.setFixedWidth(150)  # Optional: Set a fixed width for consistency
        add_button.clicked.connect(self.add_material)

        # Center the button within the horizontal layout
        button_layout.addWidget(add_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the horizontal layout to the main form layout
        layout.addRow(button_layout)

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
                    self.vendor_phone_input.text(), self.vendor_email_input.text(), self.vendor_location_input.text()]):
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
        vendor_location = self.vendor_location_input.text()
        price_date = self.price_date_input.text()  # Get date as string
        comment = self.vendor_comment_input.text()  # Get comment as string

        # Generate new mat_id by finding the next available number in the MAT-format
        self.c.execute("SELECT mat_id FROM materials WHERE mat_id LIKE 'MAT-%'")
        existing_ids = {int(id.split('-')[1]) for id, in self.c.fetchall() if id.split('-')[1].isdigit()}
        new_id = 1
        while new_id in existing_ids:
            new_id += 1
        mat_id = f'MAT-{new_id}'

        # Insert into the database
        self.c.execute('''INSERT INTO materials (mat_id, trade, material_name, currency, price, unit, vendor, vendor_phone, vendor_email, vendor_location, price_date, comment) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (mat_id, trade, material_name, currency, formatted_price, unit, vendor, vendor_phone,
                        vendor_email, vendor_location, price_date, comment))
        self.conn.commit()

        # Update the json file
        self.update_json()

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
        vendor_location = self.table.item(selected_row, 9).text()
        price_date = self.table.item(selected_row, 10).text()  # Get price date
        comment = self.table.item(selected_row, 11).text()  # Get comment

        self.material_dialog = QDialog(self)
        self.material_dialog.setWindowTitle(f"Edit Material [{mat_id}]")
        self.material_dialog.setGeometry(200, 200, 400, 300)  # Updated height for new field

        layout = QFormLayout()
        self.trade_input = QLineEdit(trade)
        self.trade_input.setMinimumWidth(400)

        self.material_name_input = QLineEdit(material_name)
        self.material_name_input.setMinimumWidth(400)

        self.material_name_input.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Text aligns left

        # Populate currency dropdown
        self.currency_input = QComboBox()
        self.currency_input.setMinimumWidth(400)

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
        self.price_input.setMinimumWidth(400)

        self.unit_input = QLineEdit(unit)
        self.unit_input.setMinimumWidth(400)

        self.vendor_input = QLineEdit(vendor)
        self.vendor_input.setMinimumWidth(400)

        self.vendor_phone_input = QLineEdit(vendor_phone)
        self.vendor_phone_input.setMinimumWidth(400)

        self.vendor_email_input = QLineEdit(vendor_email)
        self.vendor_email_input.setMinimumWidth(400)

        self.vendor_location_input = QLineEdit(vendor_location)
        self.vendor_location_input.setMinimumWidth(400)

        self.price_date_input = QDateEdit()  # New date input field
        self.price_date_input.setMinimumWidth(400)

        self.price_date_input.setDate(
            pd.to_datetime(price_date, dayfirst=True))  # Set the date input from current value
        self.price_date_input.setCalendarPopup(True)  # Show calendar popup for date selection

        self.vendor_comment_input = QLineEdit(comment)  # New date input field
        self.vendor_comment_input.setMinimumWidth(400)

        layout.addRow('Trade:', self.trade_input)
        layout.addRow('Material:', self.material_name_input)
        layout.addRow('Currency:', self.currency_input)
        layout.addRow('Price:', self.price_input)
        layout.addRow('Unit:', self.unit_input)
        layout.addRow('Vendor:', self.vendor_input)
        layout.addRow('Vendor Phone:', self.vendor_phone_input)
        layout.addRow('Vendor Email:', self.vendor_email_input)
        layout.addRow('Vendor Location:', self.vendor_location_input)
        layout.addRow('Price Date:', self.price_date_input)  # Add the date input field
        layout.addRow('Comment:', self.vendor_comment_input)  # Add the Comment input field

        save_button = QPushButton("Save Changes")
        save_button.setFixedWidth(100)
        save_button.clicked.connect(lambda: self.update_material(mat_id))

        # Create a horizontal layout for the button
        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)

        # Center the button within the horizontal layout
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the horizontal layout to the main form layout
        layout.addRow(button_layout)

        self.material_dialog.setLayout(layout)
        self.material_dialog.exec()

    def update_material(self, mat_id):
        """Updates the selected material in the database with validation checks."""

        # Ensure all required fields are filled
        if not all([self.trade_input.text(), self.material_name_input.text(),
                    self.currency_input.currentText(), self.price_input.text(),
                    self.unit_input.text(), self.vendor_input.text(),
                    self.vendor_phone_input.text(), self.vendor_email_input.text(), self.vendor_location_input.text()]):
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
        vendor_location = self.vendor_location_input.text()
        price_date = self.price_date_input.text()  # Get updated date
        comment = self.vendor_comment_input.text()  # Get updated comment

        # Update in the database
        self.c.execute('''UPDATE materials SET trade=?, material_name=?, currency=?, price=?, unit=?, vendor=?, vendor_phone=?, vendor_email=?, vendor_location=?, price_date=?, comment=? 
                          WHERE mat_id=?''',
                       (trade, material_name, currency, formatted_price, unit, vendor, vendor_phone, vendor_email, vendor_location,
                        price_date, comment, mat_id))
        self.conn.commit()

        # Update the json file
        self.update_json()

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
            vendor_location = self.table.item(selected_row, 9).text()
            price_date = self.table.item(selected_row, 10).text()
            comment = self.table.item(selected_row, 11).text()

            # Generate a new unique Mat ID by finding the maximum existing suffix
            self.c.execute("SELECT mat_id FROM materials WHERE mat_id LIKE 'MAT-%'")
            existing_ids = [int(id.split('-')[1]) for id, in self.c.fetchall() if id.split('-')[1].isdigit()]
            new_id = max(existing_ids) + 1 if existing_ids else 1
            new_mat_id = f'MAT-{new_id}'

            # Insert duplicated material into the database
            self.c.execute('''INSERT INTO materials (mat_id, trade, material_name, currency, price, unit, vendor, 
                              vendor_phone, vendor_email, vendor_location, price_date, comment) 
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (new_mat_id, trade, material_name, currency, price, unit, vendor, vendor_phone,
                            vendor_email, vendor_location, price_date, comment))
            self.conn.commit()

            # Update the json file
            self.update_json()

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

        mat_id = self.table.item(selected_row, 0).text()  # Mat ID
        material_name = self.table.item(selected_row, 2).text()  # Material Name

        reply = QMessageBox.question(self, 'Delete Material',
                                     f'Are you sure you want to delete [{mat_id}] {material_name}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.c.execute('DELETE FROM materials WHERE mat_id=?', (mat_id,))
            self.conn.commit()

            # Update the json file
            self.update_json()

            self.load_data()  # Reload data to reflect deletion

    def show_vendor_list_window(self):
        """Shows the list of all existing vendors with their details including location."""
        vendor_list_dialog = QDialog(self)
        vendor_list_dialog.setWindowTitle("Vendor Management")
        vendor_list_dialog.setGeometry(200, 200, 800, 400)

        # Create a table widget for vendors
        vendor_table_widget = QTableWidget()
        vendor_table_widget.setRowCount(0)
        vendor_table_widget.setColumnCount(5)
        vendor_table_widget.setHorizontalHeaderLabels(["Vendor ID", "Name", "Phone", "Email", "Location"])

        # Fetch and populate vendor data from the database
        self.c.execute("SELECT id, vendor, vendor_phone, vendor_email, vendor_location FROM materials")
        vendors = self.c.fetchall()
        unique_vendors = {}

        # To avoid duplicate entries in case of multiple materials from the same vendor
        for vendor in vendors:
            if vendor[1] not in unique_vendors:
                unique_vendors[vendor[1]] = vendor

        for row_idx, vendor in enumerate(unique_vendors.values()):
            vendor_table_widget.insertRow(row_idx)
            vendor_table_widget.setItem(row_idx, 0, QTableWidgetItem(f"VendorID-{vendor[0]}"))
            vendor_table_widget.setItem(row_idx, 1, QTableWidgetItem(vendor[1]))
            vendor_table_widget.setItem(row_idx, 2, QTableWidgetItem(vendor[2]))
            vendor_table_widget.setItem(row_idx, 3, QTableWidgetItem(vendor[3]))
            vendor_table_widget.setItem(row_idx, 4, QTableWidgetItem(vendor[4]))  # Location column

        # Horizontal layout for table and buttons
        main_horizontal_layout = QHBoxLayout()
        main_horizontal_layout.addWidget(vendor_table_widget)

        # Vertical layout for edit and delete buttons
        button_layout = QVBoxLayout()

        # Create an edit button
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda: self.open_edit_vendor_window(vendor_table_widget, vendor_list_dialog))
        button_layout.addWidget(edit_button)

        # Create a delete button
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(
            lambda: self.delete_selected_vendor(vendor_table_widget, vendor_list_dialog))  # Assuming delete function exists
        button_layout.addWidget(delete_button)

        button_layout.addStretch()  # Spacer at the bottom

        # Add the vertical button layout to the horizontal layout
        main_horizontal_layout.addLayout(button_layout)

        # Main vertical layout for the dialog
        main_layout = QVBoxLayout()
        main_layout.addLayout(main_horizontal_layout)

        # Layout for the close button
        close_button_layout = QHBoxLayout()
        close_button_layout.addStretch()  # Add stretch to center-align the button
        close_button = QPushButton("Close")
        close_button.clicked.connect(
            lambda: self.close_vendor_list(vendor_list_dialog))  # Call a new method to close and refresh
        close_button_layout.addWidget(close_button)
        close_button_layout.addStretch()  # Add stretch to center-align the button

        # Add the close button layout to the main vertical layout
        main_layout.addLayout(close_button_layout)

        vendor_list_dialog.setLayout(main_layout)
        vendor_list_dialog.exec()

    def close_vendor_list(self, dialog):
        """Closes the vendor list dialog and refreshes the table."""
        dialog.close()
        self.load_data()

    def open_edit_vendor_window(self, vendor_table_widget, vendor_list_dialog):
        """Opens a window to edit and update vendor details."""

        # Get the selected row in the vendor table
        selected_row = vendor_table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a vendor to edit.")
            return

        # Close the Vendor List Dialog
        vendor_list_dialog.close()

        # Fetch vendor data from the selected row
        vendor_id = vendor_table_widget.item(selected_row, 0).text().replace("VendorID-", "")
        vendor_name = vendor_table_widget.item(selected_row, 1).text()
        vendor_phone = vendor_table_widget.item(selected_row, 2).text()
        vendor_email = vendor_table_widget.item(selected_row, 3).text()
        vendor_location = vendor_table_widget.item(selected_row, 4).text()

        # Create the dialog window for editing vendor details
        edit_vendor_dialog = QDialog(self)
        edit_vendor_dialog.setWindowTitle(f"Edit Vendor - {vendor_name}")
        edit_vendor_dialog.setGeometry(200, 200, 300, 150)

        # Create form layout for vendor details
        form_layout = QFormLayout()

        # Vendor fields with current data
        vendor_name_edit = QLineEdit(vendor_name)
        vendor_name_edit.setMinimumWidth(400)

        vendor_phone_edit = QLineEdit(vendor_phone)
        vendor_phone_edit.setMinimumWidth(400)

        vendor_email_edit = QLineEdit(vendor_email)
        vendor_email_edit.setMinimumWidth(400)

        vendor_location_edit = QLineEdit(vendor_location)
        vendor_location_edit.setMinimumWidth(400)

        # Add fields to form layout
        form_layout.addRow("Vendor Name:", vendor_name_edit)
        form_layout.addRow("Phone:", vendor_phone_edit)
        form_layout.addRow("Email:", vendor_email_edit)
        form_layout.addRow("Location:", vendor_location_edit)

        # Create a horizontal layout for the save button
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save Changes")
        save_button.setFixedWidth(100)  # Optional: Set a fixed width for the button
        save_button.clicked.connect(lambda: self.save_vendor_changes(
            vendor_id,
            vendor_name_edit.text(),
            vendor_phone_edit.text(),
            vendor_email_edit.text(),
            vendor_location_edit.text(),
            edit_vendor_dialog  # Pass the dialog to close it after saving
        ))

        # Center the button within the horizontal layout
        button_layout.addWidget(save_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the horizontal layout to the main form layout
        form_layout.addRow(button_layout)

        edit_vendor_dialog.setLayout(form_layout)
        edit_vendor_dialog.exec()

    def delete_selected_vendor(self, vendor_table_widget, vendor_list_dialog):
        """Deletes all entries of the selected vendor after user confirmation."""

        # Close the vendor list dialog first
        vendor_list_dialog.close()

        # Get the selected row in the vendor table
        selected_row = vendor_table_widget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a vendor to delete.")
            return

        # Retrieve the vendor name (or ID) from the selected row
        vendor_name = vendor_table_widget.item(selected_row, 1).text()  # Assume the name is in column 1

        # Show a confirmation dialog to the user
        confirmation = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete all entries associated with vendor '{vendor_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        # Check if the user clicked 'Yes'
        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                # Delete all entries with the same vendor name
                self.c.execute("DELETE FROM materials WHERE vendor = ?", (vendor_name,))
                self.conn.commit()

                # Notify the user of successful deletion
                QMessageBox.information(self, "Deletion Successful",
                                        f"All entries for vendor '{vendor_name}' have been deleted.")

                # Refresh the vendor list to reflect the changes
                self.show_vendor_list_window()

            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"An error occurred while deleting the vendor: {e}")

    def save_vendor_changes(self, vendor_id, name, phone, email, location, dialog):
        """Saves the updated vendor information to the database."""

        try:
            # Update all rows that have the same vendor name
            # The key here is NOT to change the 'vendor' name itself during the update
            original_vendor_name = self.get_original_vendor_name(vendor_id)  # Fetch the original name to match correctly

            # Update the vendor's details in the database
            self.c.execute('''UPDATE materials 
                              SET vendor = ?, vendor_phone = ?, vendor_email = ?, vendor_location = ? 
                              WHERE vendor = ?''', (name, phone, email, location, original_vendor_name))
            self.conn.commit()

            # Show success message
            QMessageBox.information(self, "Update Successful", "Vendor details have been updated successfully.")

            # Close the dialog after saving
            dialog.close()

            # Optionally, you can refresh the vendor table if necessary
            self.show_vendor_list_window()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while updating the vendor: {e}")

    def get_original_vendor_name(self, vendor_id):
        """Fetches the original vendor name based on vendor_id."""
        try:
            self.c.execute("SELECT vendor FROM materials WHERE id = ?", (vendor_id,))
            result = self.c.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred while fetching vendor: {e}")
            return None

    def about(self):
        icon_folder_path = os.path.join(os.path.dirname(__file__), "images")
        icon_path = os.path.join(icon_folder_path, "materials-manager.png")

        about_text = f"""
        \t\t\t\t\t Materials Manager v1.1

        Software Developed by: \tKilpatrick Atta-Poku
                             \t\tKilTech Enterprise

        Overview:
        Materials Manager helps streamline material management for projects, 
        boosting efficiency with its intuitive interface and powerful features.

        Features:
        🔧 Quick access toolbar for Job and User management, material handling, and Vendor management.
        🔍 Easy search and sort for materials, trades, prices and vendors.
        📊 Detailed material info with prices, vendors, and more.
        📤 Export to and from Excel for seamless data management.
        ⚖️ Compare vendor prices and locations for smart procurement decisions.

        Purpose:
        🛠️  Developed for Quantity Surveyors, Estimators, Project and Construction managers,
            Procurement officers, and other professionals to manage materials and vendors efficiently,
            enhancing overall productivity.

        Contact:
        📧 For support, contact us on 0541193598.
                        and email us at kiltech21@gmail.com

        © 2024 (Kilpatrick/ KilTech Ent). All rights reserved.
        """

        # Create a QDialog to display the "About" information
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About")
        about_dialog.setGeometry(200, 200, 600, 400)

        # Set up the layout and label to display the text
        main_layout = QVBoxLayout()

        # Adding icon next to title and centering it
        icon_label_layout = QHBoxLayout()
        icon_label_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)  # Center the layout
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap(icon_path).scaled(50, 50))
        icon_label_layout.addWidget(icon_label)
        main_layout.addLayout(icon_label_layout)

        label = QLabel(about_text)
        label.setWordWrap(True)
        main_layout.addWidget(label)

        # Add a close button centered in a QHBoxLayout
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(about_dialog.close)
        button_layout.addStretch()  # Add stretch to center the button
        button_layout.addWidget(close_button)
        button_layout.addStretch()  # Add stretch to center the button

        main_layout.addLayout(button_layout)

        about_dialog.setLayout(main_layout)
        about_dialog.exec()

    def closeEvent(self, event):
        """Handles the window close event."""
        self.conn.close()  # Close the database connection
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BasicPricelist()
    window.show()
    sys.exit(app.exec())
