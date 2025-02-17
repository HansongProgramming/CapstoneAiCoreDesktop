import sys
import pyvista as pv
from pyvistaqt import QtInteractor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main Widget and Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # QLabel for displaying selected plane
        self.label = QLabel("Selected Plane: None")
        self.layout.addWidget(self.label)

        # QtInteractor (PyVista rendering window)
        self.plotter = QtInteractor(self)
        self.layout.addWidget(self.plotter.interactor)

        # Add planes
        self.planes = {
            "Plane A": self.plotter.add_mesh(pv.Plane(i_size=5, j_size=5).translate([0, 0, 0]), name="Plane A", pickable=True, color="red"),
            "Plane B": self.plotter.add_mesh(pv.Plane(i_size=5, j_size=5).translate([10, 0, 0]), name="Plane B", pickable=True, color="blue"),
            "Plane C": self.plotter.add_mesh(pv.Plane(i_size=5, j_size=5).translate([-10, 0, 0]), name="Plane C", pickable=True, color="green"),
        }

        # Enable picking
        self.plotter.enable_point_picking(callback=self.pick_callback, left_clicking=True, show_message=False)

    def pick_callback(self, point):
        """Callback function to update label when a plane is picked."""
        picked_actor = self.plotter.picked_actor
        if picked_actor:
            for name, actor in self.planes.items():
                if picked_actor == actor:
                    self.label.setText(f"Selected Plane: {name}")
                    break
        else:
            self.label.setText("Selected Plane: None")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
