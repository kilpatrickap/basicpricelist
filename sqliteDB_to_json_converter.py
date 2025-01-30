import sys
import sqlite3
import pandas as pd
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
import os


class SQLiteToJSONApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SQLite to JSON Converter")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Select an SQLite database to convert:")
        layout.addWidget(self.label)

        self.selectButton = QPushButton("Select Database")
        self.selectButton.clicked.connect(self.selectDatabase)
        layout.addWidget(self.selectButton)

        self.convertButton = QPushButton("Convert to JSON")
        self.convertButton.clicked.connect(self.convertToJSON)
        self.convertButton.setEnabled(False)
        layout.addWidget(self.convertButton)

        self.setLayout(layout)

    def selectDatabase(self):
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
        file_path, _ = QFileDialog.getOpenFileName(self, "Select SQLite Database", parent_dir,
                                                   "SQLite Files (*.db *.sqlite)")

        if file_path:
            self.db_path = file_path
            self.label.setText(f"Selected: {os.path.basename(file_path)}")
            self.convertButton.setEnabled(True)

    def convertToJSON(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]

            all_data = {}
            for table in tables:
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                all_data[table] = df.to_dict(orient="records")

            conn.close()

            if all_data:
                parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
                json_path = os.path.join(parent_dir, "materials-data.json")
                with open(json_path, "w", encoding="utf-8") as json_file:
                    json.dump(all_data, json_file, indent=4, ensure_ascii=False)

                QMessageBox.information(self, "Success", f"JSON file saved at: {json_path}")
            else:
                QMessageBox.warning(self, "Warning", "No tables found in the database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SQLiteToJSONApp()
    window.show()
    sys.exit(app.exec())
