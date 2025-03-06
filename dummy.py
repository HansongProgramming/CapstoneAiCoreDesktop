import sys
import numpy as np
import pyvista as pv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QLineEdit
from PyQt5.QtCore import Qt
from pyvistaqt import QtInteractor  # Import PyVista's Qt-compatible interactor
from scipy.spatial.transform import Rotation as R  # Import rotation library


class PyVistaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyVista Example")
        self.resize(800, 600)

        # Main layout
        main_layout = QHBoxLayout(self)

        # PyVista Plotter
        self.plotter = QtInteractor(self)  # ✅ Use QtInteractor instead of regular Plotter
        main_layout.addWidget(self.plotter, 2)

        # Sidebar
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)
        main_layout.addWidget(self.sidebar, 1)

        # Coordinate display
        self.coord_labels = QLabel("X: 0 | Y: 0 | Z: 0")
        sidebar_layout.addWidget(self.coord_labels)

        # Position Inputs
        self.x_input = QLineEdit("0")
        self.y_input = QLineEdit("0")
        self.z_input = QLineEdit("0")
        sidebar_layout.addWidget(QLabel("X Position:"))
        sidebar_layout.addWidget(self.x_input)
        sidebar_layout.addWidget(QLabel("Y Position:"))
        sidebar_layout.addWidget(self.y_input)
        sidebar_layout.addWidget(QLabel("Z Position:"))
        sidebar_layout.addWidget(self.z_input)

        self.x_input.editingFinished.connect(self.update_position)
        self.y_input.editingFinished.connect(self.update_position)
        self.z_input.editingFinished.connect(self.update_position)

        # Rotation Sliders
        self.add_slider("Rotate X", sidebar_layout, self.rotate_x)
        self.add_slider("Rotate Y", sidebar_layout, self.rotate_y)
        self.add_slider("Rotate Z", sidebar_layout, self.rotate_z)

        # Create 3D scene
        self.create_wall()
        self.create_cylinder()

        self.plotter.show()

    def create_wall(self):
        """Creates a plane with an image texture."""
        texture = pv.read_texture("D:\\Academics\\CIT7\\imgValid\\IMG_0914.png")
        self.wall = pv.Plane(center=(0, 0, 0), direction=(0, 0, 1), i_size=5, j_size=5)
        self.plotter.add_mesh(self.wall, texture=texture)

    def create_cylinder(self):
        """Creates a white cylinder representing the trajectory line."""
        self.cylinder_position = np.array([0, 0, 0])
        self.cylinder_rotation = np.array([0, 0, 0])
        
        start = self.cylinder_position
        end = start + np.array([0, 1.5, 0])  # Adjust for end anchoring
        self.cylinder = pv.Line(start, end)
        self.cylinder_actor = self.plotter.add_mesh(self.cylinder, color='white', line_width=5)

    def add_slider(self, label, layout, callback):
        layout.addWidget(QLabel(label))
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(360)
        slider.valueChanged.connect(callback)
        layout.addWidget(slider)

    def update_position(self):
        x = float(self.x_input.text())
        y = float(self.y_input.text())
        z = float(self.z_input.text())
        
        self.cylinder_position = np.array([x, y, z])
        self.refresh_cylinder()
        self.coord_labels.setText(f"X: {x} | Y: {y} | Z: {z}")

    def rotate_x(self, value):
        self.cylinder_rotation[0] = value
        self.refresh_cylinder()

    def rotate_y(self, value):
        self.cylinder_rotation[1] = value
        self.refresh_cylinder()

    def rotate_z(self, value):
        self.cylinder_rotation[2] = value
        self.refresh_cylinder()

    def refresh_cylinder(self):
        """Recalculates the cylinder position and applies rotation."""
        start = self.cylinder_position
        end = np.array([0, 1.5, 0])  # Default end position

        # Create a rotation matrix from the stored rotation values
        rotation = R.from_euler('xyz', self.cylinder_rotation, degrees=True)
        
        # Apply the rotation to the end position (keeping start fixed)
        rotated_end = rotation.apply(end) + start  

        # Remove the old line
        self.plotter.remove_actor(self.cylinder_actor)

        # Create a new updated line with rotation
        self.cylinder = pv.Line(start, rotated_end)
        self.cylinder_actor = self.plotter.add_mesh(self.cylinder, color='white', line_width=5)

        # Refresh the scene
        self.plotter.render()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyVistaApp()
    window.show()
    sys.exit(app.exec_())
