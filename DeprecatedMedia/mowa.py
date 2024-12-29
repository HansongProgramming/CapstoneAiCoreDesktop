import sys
import pyvista as pv
from pyvistaqt import QtInteractor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QDockWidget, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import Qt
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AiCore Test")
        self.setGeometry(100, 100, 1200, 800)

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)

        # PyVista plotter
        self.plotter = QtInteractor(self)
        self.main_layout.addWidget(self.plotter.interactor)

        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(300)
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        # Input fields for room dimensions
        self.sidebar_layout.addWidget(QLabel("Enter Room Dimensions (X, Y, Z):"))
        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("X size")
        self.sidebar_layout.addWidget(self.x_input)

        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Y size")
        self.sidebar_layout.addWidget(self.y_input)

        self.z_input = QLineEdit()
        self.z_input.setPlaceholderText("Z size")
        self.sidebar_layout.addWidget(self.z_input)

        # Button to create room
        self.create_room_btn = QPushButton("Create Room")
        self.create_room_btn.clicked.connect(self.create_room)
        self.sidebar_layout.addWidget(self.create_room_btn)

        # Button to load image as texture
        self.load_image_btn = QPushButton("Load Image as Texture")
        self.load_image_btn.clicked.connect(self.load_image)
        self.sidebar_layout.addWidget(self.load_image_btn)

        # Button to automatically find convergence point
        self.auto_convergence_btn = QPushButton("Auto Convergence Point")
        self.auto_convergence_btn.clicked.connect(self.auto_convergence_point)
        self.sidebar_layout.addWidget(self.auto_convergence_btn)

        # Spacer to push buttons up
        self.sidebar_layout.addStretch()

        # Toggle sidebar button
        self.toggle_sidebar_btn = QPushButton("<>")
        self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)
        self.main_layout.addWidget(self.toggle_sidebar_btn)

        # Add sidebar to the layout
        self.main_layout.addWidget(self.sidebar)

        # PyVista initial plot
        self.init_plot()

    def init_plot(self):
        """Initialize the PyVista scene."""
        self.plotter.clear()
        self.plotter.add_axes()
        self.plotter.background_color = "white"

    def toggle_sidebar(self):
        """Show or hide the sidebar."""
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()

    def create_room(self):
        """Create a 3D room based on input dimensions."""
        try:
            x = float(self.x_input.text())
            y = float(self.y_input.text())
            z = float(self.z_input.text())

            # Clear the plot and add a room (cube)
            self.plotter.clear()
            room = pv.Box(bounds=(0, x, 0, y, 0, z))
            self.plotter.add_mesh(room, style="wireframe", color="blue")
            self.plotter.reset_camera()
        except ValueError:
            print("Please enter valid numbers for X, Y, Z.")

    def load_image(self):
        """Load an image and display it as a texture."""
        # Open file dialog to select an image
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp *.jpeg);;All Files (*)")
        
        if file_name:
            try:
                # Create a plane to apply the texture
                plane = pv.Plane(center=(0, 0, 0), i_size=5 , j_size=5)
                
                # Load the selected texture
                texture = pv.read_texture(file_name)
                
                # Clear previous plot and add the plane with the new texture
                self.plotter.clear()
                self.plotter.add_mesh(plane, texture=texture)
                self.plotter.reset_camera()
            except Exception as e:
                print(f"Failed to load texture: {e}")

    def auto_convergence_point(self):
        """Calculate and display the point of convergence of the stains."""
        # For now, generate some dummy stain points
        # Replace this with actual stain detection logic
        stain_points = np.random.rand(10, 3) * 5  # Random points within the room

        # Calculate the convergence point (simplified method: average of points)
        # This is just an example. More complex algorithms can be used.
        convergence_point = stain_points.mean(axis=0)

        # Add the stain points to the plot
        self.plotter.add_points(stain_points, color="red", point_size=10)

        # Add the convergence point to the plot
                # Convert the list of points into a PolyData object
        points = pv.PolyData(convergence_point)

        # Add the points to the plotter
        self.plotter.add_mesh(points, color="green", point_size=15)
        self.plotter.reset_camera()

# Run the application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
