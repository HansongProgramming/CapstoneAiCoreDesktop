from imports import *

class GenerateReportDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.setWindowTitle("Generate Report")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(350, 250)

        self.layout = QVBoxLayout(self)

        self.title_label = QLabel("Generate Report")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.case_number_label = QLabel("Case Number:")
        self.case_number_input = QLineEdit()

        self.investigator_label = QLabel("Investigator:")
        self.investigator_input = QLineEdit()

        self.location_label = QLabel("Location:")
        self.location_input = QLineEdit()

        self.button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.export_button = QPushButton("Export")

        self.cancel_button.clicked.connect(self.close)
        self.export_button.clicked.connect(self.generate_report)

        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.export_button)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.case_number_label)
        self.layout.addWidget(self.case_number_input)
        self.layout.addWidget(self.investigator_label)
        self.layout.addWidget(self.investigator_input)
        self.layout.addWidget(self.location_label)
        self.layout.addWidget(self.location_input)
        self.layout.addLayout(self.button_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: white;
                border-radius: 10px;
            }
            QLabel {
                font-size: 12px;
            }
            QLineEdit {
                background-color: #3d3d3d;
                border: 1px solid #555;
                padding: 5px;
                color: white;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #444;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)

    def generate_report(self):
        case_number = self.case_number_input.text().strip()
        investigator = self.investigator_input.text().strip()
        location = self.location_input.text().strip()

        if not case_number or not investigator or not location:
            QMessageBox.warning(self, "Error", "Please fill in all fields before generating the report.")
            return

        self.main_window.generate_report(case_number, investigator, location)
        self.close()