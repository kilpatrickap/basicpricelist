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
        json_filename = os.path.join(parent_dir, "materials-data.json")
        db_filename = os.path.join(parent_dir, "materialsAPI.db")

        if self.download_json(api_url, json_filename):
            self.create_and_populate_db(json_filename, db_filename)
            QMessageBox.information(self, "Success", "Database updated successfully!")
            self.refresh_databases(db_filename)  # Refresh the databases
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
        """Creates an SQLite database and populates it with data from the JSON file, with error handling."""
        try:
            # Load JSON data
            with open(json_filename, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Connect to database
            conn = sqlite3.connect(db_filename)
            cursor = conn.cursor()

            # Create table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS materialsAPI (
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

            # Insert or update data
            for item in data["materials"]:
                cursor.execute('''
                    UPDATE materialsAPI 
                    SET trade=?, material_name=?, currency=?, price=?, unit=?, vendor=?, 
                        vendor_phone=?, vendor_email=?, vendor_location=?, price_date=?, comment=?
                    WHERE mat_id=?
                ''', (
                    item["trade"], item["material_name"], item["currency"], item["price"], item["unit"],
                    item["vendor"], item["vendor_phone"], item["vendor_email"], item["vendor_location"],
                    item["price_date"], item["comment"], item["mat_id"]
                ))

                # If no rows were updated, insert new data
                if cursor.rowcount == 0:
                    cursor.execute('''
                        INSERT INTO materialsAPI (
                            id, mat_id, trade, material_name, currency, price, unit, 
                            vendor, vendor_phone, vendor_email, vendor_location, price_date, comment
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item["id"], item["mat_id"], item["trade"], item["material_name"], item["currency"],
                        item["price"], item["unit"], item["vendor"], item["vendor_phone"],
                        item["vendor_email"], item["vendor_location"], item["price_date"], item["comment"]
                    ))

            conn.commit()

        except FileNotFoundError:
            QMessageBox.warning(self, "Error", f"File '{json_filename}' not found.")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error", "Invalid JSON format in the file.")
        except sqlite3.DatabaseError as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred: {e}")
            print(e)
        except Exception as e:
            QMessageBox.warning(self, "Unexpected Error", f"An error occurred: {str(e)}")
        finally:
            conn.close()  # Ensure connection is closed

    #############   REFRESH DATABASES     ##############
    # Replace the contents of materials.db with materialsAPI.db
    # This function copies the data from materialsAPI.db to materials.db.
    # If the "materials.db" file already exists, it will be overwritten.
    # After refreshing the database, the new data will be available in "materials.db".
    # This can be useful for scenarios where the database needs to be reset with the latest data
    # from the API download process or when switching between different data sources.
    def refresh_databases(self, source_db_filename):
        """Replaces the contents of materials.db with materialsAPI.db."""
        try:
            parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
            target_db_filename = os.path.join(parent_dir, "materials.db")

            # Connect to the source (materialsAPI.db) and target (materials.db) databases
            source_conn = sqlite3.connect(source_db_filename)
            target_conn = sqlite3.connect(target_db_filename)
            source_cursor = source_conn.cursor()
            target_cursor = target_conn.cursor()

            # Drop existing tables and create them again in the target database
            target_cursor.execute("DROP TABLE IF EXISTS materialsAPI")
            target_cursor.execute('''CREATE TABLE materialsAPI (
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

            # Copy data from the source database to the target database
            source_cursor.execute("SELECT * FROM materialsAPI")
            rows = source_cursor.fetchall()
            target_cursor.executemany('''
                INSERT INTO materialsAPI (
                    id, mat_id, trade, material_name, currency, price, unit, 
                    vendor, vendor_phone, vendor_email, vendor_location, price_date, comment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', rows)

            target_conn.commit()

            QMessageBox.information(self, "Success", "Database refreshed successfully!")

        except sqlite3.DatabaseError as e:
            QMessageBox.warning(self, "Database Error", f"An error occurred while refreshing the database: {e}")
            print(e)
        except Exception as e:
            QMessageBox.warning(self, "Unexpected Error", f"An error occurred: {str(e)}")
        finally:
            # Close connections
            source_conn.close()
            target_conn.close()


def main():
    app = QApplication([])
    window = ApiDownloaderApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
