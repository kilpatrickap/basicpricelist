import os
import json
import sqlite3
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox


class ApiDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("API Downloader")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()
        self.download_button = QPushButton("Download from API", self)
        self.download_button.clicked.connect(self.download_and_save)
        layout.addWidget(self.download_button)

        self.setLayout(layout)

    def download_and_save(self):
        api_url = "https://mm-api-rz05.onrender.com"
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
        json_filename = os.path.join(parent_dir, "materials-data-TEST.json")
        db_filename = os.path.join(parent_dir, "materials-TEST.db")

        if self.download_json(api_url, json_filename):
            self.create_and_populate_db(json_filename, db_filename)
            QMessageBox.information(self, "Success", "Database updated successfully!")
        else:
            QMessageBox.warning(self, "Error", "Failed to download data from API.")

    def download_json(self, api_url, json_filename):
        """Downloads JSON data from the API and saves it to a file."""
        response = requests.get(api_url)
        if response.status_code == 200:
            with open(json_filename, "w", encoding="utf-8") as file:
                json.dump(response.json(), file, indent=4)
            return True
        return False

    def create_and_populate_db(self, json_filename, db_filename):
        """Creates an SQLite database and populates it with data from the JSON file."""
        with open(json_filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        conn = sqlite3.connect(db_filename)
        cursor = conn.cursor()

        # Create materials table
        cursor.execute('''CREATE TABLE IF NOT EXISTS materials-TEST (
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

        # Insert data into the materials table
        for item in data:
            cursor.execute('''UPDATE materials-TEST 
                SET trade=?, material_name=?, currency=?, price=?, unit=?, vendor=?, vendor_phone=?, 
                    vendor_email=?, vendor_location=?, price_date=?, comment=?
                WHERE mat_id=?''', (
                item.get("trade"), item.get("material_name"), item.get("currency"),
                item.get("price"), item.get("unit"), item.get("vendor"), item.get("vendor_phone"),
                item.get("vendor_email"), item.get("vendor_location"), item.get("price_date"), item.get("comment"),
                item.get("mat_id")
            ))

            # If no rows were updated, insert new data
            if cursor.rowcount == 0:
                cursor.execute('''INSERT INTO materials-TEST (
                    mat_id, trade, material_name, currency, price, unit, vendor, vendor_phone, 
                    vendor_email, vendor_location, price_date, comment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                    item.get("mat_id"), item.get("trade"), item.get("material_name"), item.get("currency"),
                    item.get("price"), item.get("unit"), item.get("vendor"), item.get("vendor_phone"),
                    item.get("vendor_email"), item.get("vendor_location"), item.get("price_date"), item.get("comment")
                ))

        conn.commit()
        conn.close()


def main():
    app = QApplication([])
    window = ApiDownloaderApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
