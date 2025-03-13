from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt

class TutorialOverlay(QLabel):
    def __init__(self, text, target_widget, parent=None):
        super().__init__(parent)
        self.target = target_widget

        # Arrow image
        self.arrow = QLabel(parent)
        arrow_pixmap = QPixmap("arrow.png")  # Replace with your arrow image
        self.arrow.setPixmap(arrow_pixmap)
        self.arrow.setScaledContents(True)
        self.arrow.resize(50, 50)

        # Tutorial text
        self.setText(text)
        self.setStyleSheet("background: yellow; padding: 5px; border: 1px solid black;")
        self.adjustSize()

        self.update_position()

    def update_position(self):
        """Update position near the target widget."""
        if self.target:
            pos = self.target.mapToParent(self.target.rect().bottomLeft())
            self.move(pos.x(), pos.y() + 10)

            arrow_pos = self.target.mapToParent(self.target.rect().topRight())
            self.arrow.move(arrow_pos.x() + 10, arrow_pos.y() - 30)

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt Tutorial Demo")
        self.setGeometry(100, 100, 400, 300)

        # Example button
        self.button = QPushButton("Click Me", self)
        self.button.setGeometry(150, 150, 100, 40)

        # Show tutorial overlay
        self.tutorial = TutorialOverlay("Click this button!", self.button, self)

        # Remove tutorial after clicking
        self.button.clicked.connect(self.hide_tutorial)

    def hide_tutorial(self):
        self.tutorial.hide()
        self.tutorial.arrow.hide()

app = QApplication([])
window = MainApp()
window.show()
app.exec_()
