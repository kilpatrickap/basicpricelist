from PyQt6 import QtCore, QtGui, QtWidgets
import random

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton_generate = QtWidgets.QPushButton(parent=Dialog)
        self.pushButton_generate.setObjectName("pushButton_generate")

        # Connect signal
        self.pushButton_generate.clicked.connect(self.generate)

        self.verticalLayout.addWidget(self.pushButton_generate)
        self.lineEdit_key = QtWidgets.QLineEdit(parent=Dialog)
        self.lineEdit_key.setObjectName("lineEdit_key")
        self.verticalLayout.addWidget(self.lineEdit_key)
        self.label_verify = QtWidgets.QLabel(parent=Dialog)
        self.label_verify.setObjectName("label_verify")
        self.verticalLayout.addWidget(self.label_verify)
        self.label_score = QtWidgets.QLabel(parent=Dialog)
        self.label_score.setObjectName("label_score")
        self.verticalLayout.addWidget(self.label_score)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Register"))
        self.pushButton_generate.setText(_translate("Dialog", "Generate Key"))
        self.label_verify.setText(_translate("Dialog", "Waiting..."))
        self.label_score.setText(_translate("Dialog", "Score:"))

    def generate(self):
        # Clear the lineEdit_key
        self.lineEdit_key.clear()
        self.label_verify.setText("")

        # Set some defaults
        key = ''
        section = ''
        check_digit_count = 0
        alphabet = 'abcdefghijklmnopqrstuvwxyz1234567890'
        
        # key = aaaa-bbbb-cccc-dddd-1111 (5 sets of 4 or 24 chars)

        while len(key) < 25:
            # Randomly pick digit from alphabet
            char = random.choice(alphabet)
            # Add random choice to key
            key += char
            # Add random choice to the section blob
            section += char

            # Add in the hyphens
            if len(section) == 4:
                # Add in a hyphen
                key += '-'
                # Reset section to nothing
                section = ''

        # Set key to all but the last digit
        key = key[:-1]   # Everything up to the last digit

        # Output the key
        #self.lineEdit_key.insert(key)

        # Verify
        if self.verify(key):
            # Key is verified
            self.lineEdit_key.setText(key)
            self.label_verify.setText("Valid!")
            self.label_score.setText(f'Score: {score}')
        else:
            # Key is not verified
            # Run the generate() function again
            self.generate()

    def verify(self, key):
        global score
        score = 0

        # Define our check digit
        check_digit = key[3]    # Say 3rd digit TODO: Change key
        check_digit_count = 0   # Track how many times we see that digit in the key

        # aafa-bbfb-cccc-ddfd-1111
        # separate by hypen
        chunks = key.split('-')

        # Loop through chunks and check
        for chunk in chunks:
            if len(chunk) != 4:     # If chunk is < 4, return false
                return False

            for char in chunk:
                if char == check_digit:
                    check_digit_count += 1  # add 1 to the counter

                # Grab the score of the ANSCII char
                score += ord(char)      # ord() converts the numerical value of a char.

        # Check for rules
        if 1700 < score < 1800 and check_digit_count == 3:
            return True
        else:
            return False

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec())
