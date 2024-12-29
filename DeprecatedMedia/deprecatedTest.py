import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFileDialog, QLabel, QComboBox
from PyQt5.QtGui import QPixmap
import pyvista as pv
from pyvistaqt import QtInteractor
from PIL import Image
from PyQt5.QtCore import Qt
from image_interaction_dialog import ImageInteractionDialog  # Import the dialog class


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyVista Image Plane Adder")
        self.setGeometry(100, 100, 1200, 800)

        # Track the size of the first loaded image and its path
        self.default_size = (10, 10)
        self.textures = {}
        self.image_paths = {}  # Store image paths for each plane

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

        # Buttons to add planes
        self.add_floor_btn = QPushButton("Add Floor with Image")
        self.add_floor_btn.clicked.connect(lambda: self.add_plane_with_image("floor"))
        self.sidebar_layout.addWidget(self.add_floor_btn)

        self.add_right_wall_btn = QPushButton("Add Right Wall with Image")
        self.add_right_wall_btn.clicked.connect(lambda: self.add_plane_with_image("right"))
        self.sidebar_layout.addWidget(self.add_right_wall_btn)

        self.add_left_wall_btn = QPushButton("Add Left Wall with Image")
        self.add_left_wall_btn.clicked.connect(lambda: self.add_plane_with_image("left"))
        self.sidebar_layout.addWidget(self.add_left_wall_btn)

        self.add_back_wall_btn = QPushButton("Add Back Wall with Image")
        self.add_back_wall_btn.clicked.connect(lambda: self.add_plane_with_image("back"))
        self.sidebar_layout.addWidget(self.add_back_wall_btn)

        self.add_front_wall_btn = QPushButton("Add Front Wall with Image")
        self.add_front_wall_btn.clicked.connect(lambda: self.add_plane_with_image("front"))
        self.sidebar_layout.addWidget(self.add_front_wall_btn)

        # Spacer to push buttons up
        self.sidebar_layout.addStretch()

        # Add "Add Points" button
        self.add_points_btn = QPushButton("Add Points")
        self.add_points_btn.clicked.connect(lambda: self.open_image_with_interaction(self.texture_select.currentText().lower()))
        self.main_layout.addWidget(self.add_points_btn)

        # Toggle sidebar button
        self.toggle_sidebar_btn = QPushButton("<>")
        self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)
        self.main_layout.addWidget(self.toggle_sidebar_btn)

        # Add sidebar to the layout
        self.main_layout.addWidget(self.sidebar)

        # QLabel to display the image preview
        self.image_label = QLabel("No image selected")
        self.sidebar_layout.addWidget(self.image_label)

        # Dropdown to select wall or floor for texture
        self.texture_select = QComboBox()
        self.texture_select.addItem("Floor")
        self.texture_select.addItem("Right Wall")
        self.texture_select.addItem("Left Wall")
        self.texture_select.addItem("Back Wall")
        self.texture_select.addItem("Front Wall")
        self.texture_select.currentIndexChanged.connect(self.update_texture_for_plane)
        self.sidebar_layout.addWidget(self.texture_select)

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

    def load_image(self):
        """Open a file dialog to load an image, return its dimensions, and prepare the texture."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_path:
            with Image.open(file_path) as img:
                width, height = img.size
            texture = pv.read_texture(file_path)

            # Store the image path in a dictionary for later reference
            return width, height, texture, file_path
        return None, None, None, None

    def add_plane_with_image(self, position):
        """Add a plane with the size of the imported image."""
        width, height, texture, image_path = self.load_image()  # Assuming this function loads the texture and path
        if texture:
            self.default_size = (width / 100, height / 100)  # Normalize size
            self.textures[position] = texture  # Store texture for the plane (floor or wall)
            self.image_paths[position] = image_path  # Store the image path
        else:
            width, height = self.default_size[0] * 100, self.default_size[1] * 100
            texture = None

        # Create the plane (for floor or wall)
        plane_center = {
            "floor": (0, 0, 0),
            "right": (self.default_size[0] / 2, 0, height / 134 / 2),
            "left": (-self.default_size[0] / 2, 0, height / 134 / 2),
            "back": (0, -self.default_size[1] / 2, height / 134 / 2),
            "front": (0, self.default_size[1] / 2, height / 134 / 2),
        }

        plane_direction = {
            "floor": (0, 0, 1),
            "right": (1, 0, 0),
            "left": (-1, 0, 0),
            "back": (0, -1, 0),
            "front": (0, 1, 0),
        }

        if position in plane_center and position in plane_direction:
            plane = pv.Plane(
                center=plane_center[position],
                direction=plane_direction[position],
                i_size=(width / 100 if position == "floor" else self.default_size[0]),
                j_size=(height / 100 if position == "floor" else self.default_size[1]),
            )
            self.plotter.add_mesh(plane, texture=texture, name=f"{position}_plane")

    def update_texture_for_plane(self):
        """Handle texture update when a wall/floor is selected from the dropdown."""
        selected_plane = self.texture_select.currentText()
        position_map = {
            "Floor": "floor",
            "Right Wall": "right",
            "Left Wall": "left",
            "Back Wall": "back",
            "Front Wall": "front"
        }

        # Get the corresponding plane position
        position = position_map.get(selected_plane)

        if position and position in self.textures:
            texture = self.textures.get(position)  # Retrieve the texture for the selected plane

            # Update the image preview for the selected texture
            self.update_image_preview(position)
        else:
            # Handle case where no texture is found (optional)
            self.update_image_preview(None)  # Clear the preview

    def update_image_preview(self, position):
        """Update the image preview based on the selected texture."""
        if position and position in self.image_paths:
            # Get the path of the image associated with the selected plane
            image_path = self.image_paths[position]

            # Load the image using QPixmap
            pixmap = QPixmap(image_path)

            # Get the original width and height of the image
            original_width = pixmap.width()
            original_height = pixmap.height()

            # Define the maximum size for the preview (you can adjust this value)
            max_size = 200  # Maximum width or height

            # Maintain the aspect ratio by scaling the image dynamically
            if original_width > original_height:
                scaled_width = max_size
                scaled_height = int(max_size * original_height / original_width)
            else:
                scaled_height = max_size
                scaled_width = int(max_size * original_width / original_height)

            # Resize the pixmap while maintaining the aspect ratio
            scaled_pixmap = pixmap.scaled(scaled_width, scaled_height, aspectRatioMode=1)  # 1 is Qt.KeepAspectRatio

            # Set the scaled pixmap to the label for preview
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setText("")  # Clear the default text
        else:
            self.image_label.clear()  # Clear the image preview if no texture is found
            self.image_label.setText("No texture available.")

    def open_image_with_interaction(self, position):
        """Open a new window with the image and allow the user to select points."""
        image_path = self.image_paths.get(position)  # Safely get the image path
        if image_path:
            dialog = ImageInteractionDialog(image_path, self)
            dialog.exec_()
        else:
            print(f"No image found for {position}.")


# Main loop
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
