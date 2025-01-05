from imports import *

if getattr(sys, 'frozen', False):
    import pyi_splash

global canEnable
canEnable = False

class MenuButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("File", parent)
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
            }
        """)
        
        # Create menu
        self.menu = QMenu(self)
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
        """)
        
        # Add menu items
        self.menu.addAction("New")
        self.menu.addAction("Open")
        self.menu.addAction("Save")
        self.menu.addSeparator()
        self.menu.addAction("Exit")
        
        # Set the menu
        self.setMenu(self.menu)
        
        # Connect actions
        self.menu.triggered.connect(self.handleMenuAction)

    def handleMenuAction(self, action):
        global canEnable
        if action.text() == "Exit":
            self.window().close()
        elif action.text() == "New":
            # Prompt user to select a directory
            folder_path = QFileDialog.getExistingDirectory(self, "Select Directory for New Case")
            if folder_path:
                # Create a new folder and `Data.json`
                case_folder = os.path.join(folder_path, "NewCase")
                os.makedirs(case_folder, exist_ok=True)
                data_file = os.path.join(case_folder, "Data.json")
                with open(data_file, 'w') as json_file:
                    json.dump({}, json_file)  # Create an empty JSON

                # Notify the MainWindow to enable interactions
                canEnable = True

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        # Title label
        self.title = QLabel("AiCore x SpatterSense")
        self.title.setStyleSheet("color: white; font-size: 12px;")

        self.AiCoreLabel = QLabel()
        self.AiCoreIcon = QPixmap(self.get_resource_path("images/AiCore.png"))
        self.scaled_pixmap = self.AiCoreIcon.scaled(20, 20, aspectRatioMode=Qt.KeepAspectRatio)
        self.AiCoreLabel.setPixmap(self.scaled_pixmap)
        # File button
        self.file_btn = MenuButton(self)
        self.file_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
            }
        """)
        self.minimizeIcon = QPixmap(self.get_resource_path("images/minimize.png"))
        self.scaled_pixmap = self.minimizeIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.maximizeIcon = QPixmap(self.get_resource_path("images/maximize.png"))
        self.scaled_pixmap = self.maximizeIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.exitIcon = QPixmap(self.get_resource_path("images/exit.png"))
        self.scaled_pixmap = self.exitIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        # Window controls
        self.minimize_btn = QPushButton()
        self.maximize_btn = QPushButton()
        self.close_btn = QPushButton()
        self.minimize_btn.setIcon(QIcon(self.minimizeIcon))
        self.maximize_btn.setIcon(QIcon(self.maximizeIcon)) 
        self.close_btn.setIcon(QIcon(self.exitIcon))
        
        for btn in (self.minimize_btn, self.maximize_btn, self.close_btn):
            btn.setFixedSize(50, 30)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: white;
                    border: none;
                    text-align: center;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.1);
                }
            """)
        
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                text-align: center;
            }
            QPushButton:hover {
                background: #c83f61;
                color: white;
            }
        """)
        
        # Add widgets to layout
        self.layout.addWidget(self.AiCoreLabel)
        self.layout.addWidget(self.file_btn)
        self.layout.addStretch(1)
        self.layout.addWidget(self.minimize_btn)
        self.layout.addWidget(self.maximize_btn)
        self.layout.addWidget(self.close_btn)
        
        # Connect buttons
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        self.maximize_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.parent.close)
        
        self.start = QPoint(0, 0)
        self.pressing = False
        
    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
            
    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True
        
    def mouseMoveEvent(self, event):
        if self.pressing:
            if self.parent.isMaximized():
                self.parent.showNormal()
            
            end = self.mapToGlobal(event.pos())
            movement = end - self.start
            
            self.parent.setGeometry(
                self.parent.pos().x() + movement.x(),
                self.parent.pos().y() + movement.y(),
                self.parent.width(),
                self.parent.height()
            )
            self.start = end
            
    def mouseReleaseEvent(self, event):
        self.pressing = False

    def get_resource_path(self, relative_path):
        if getattr(sys, 'frozen', False):  # If the script is run from an executable
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    dataUpdated = pyqtSignal(str)
    def __init__(self):
        global canEnable
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("AiCore x SpatterSense")
        self.title_bar = TitleBar(self)

        self.setGeometry(100, 100, 1200, 800)

        self.label = QLabel("AI Core Viewer", self)
        self.label.setGeometry(10, 10, 780, 30)

        self.default_size = (10, 10)
        self.textures = {}
        self.image_paths = {}
        self.segments = []
        self.previous_data = None  

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.addWidget(self.title_bar)

        self.content_layout = QHBoxLayout()

        self.plotter = QtInteractor(self)
        self.content_layout.addWidget(self.plotter.interactor)

        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(330)
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        self.sidebarIcon = QPixmap(self.get_resource_path("images/sidebar.png"))
        self.scaled_pixmap = self.sidebarIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.floorIcon = QPixmap(self.get_resource_path("images/floor.png"))
        self.scaled_pixmap1 = self.floorIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.wallrIcon = QPixmap(self.get_resource_path("images/wallR.png"))
        self.scaled_pixmap2 = self.wallrIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.walllIcon = QPixmap(self.get_resource_path("images/wallL.png"))
        self.scaled_pixmap3 = self.walllIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.wallbIcon = QPixmap(self.get_resource_path("images/wallB.png"))
        self.scaled_pixmap4 = self.wallbIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.wallfIcon = QPixmap(self.get_resource_path("images/wallF.png"))
        self.scaled_pixmap5 = self.wallfIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.generateicon = QPixmap(self.get_resource_path("images/generateicon.png"))
        self.scaled_pixmap6 = self.generateicon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.selectspatter = QPixmap(self.get_resource_path("images/select spatter.png"))
        self.scaled_pixmap7 = self.selectspatter.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)

        self.Header3D = QLabel("3D Assets")
        self.add_floor_btn = QPushButton("Floor")
        self.add_floor_btn.clicked.connect(lambda: self.add_plane_with_image("floor"))
        self.add_floor_btn.setIcon(QIcon(self.scaled_pixmap1))
        self.add_floor_btn.setIconSize(QSize(20,20))
        self.sidebar_layout.addWidget(self.add_floor_btn)

        self.add_right_wall_btn = QPushButton("Right Wall")
        self.add_right_wall_btn.clicked.connect(lambda: self.add_plane_with_image("right"))
        self.add_right_wall_btn.setIcon(QIcon(self.scaled_pixmap2))
        self.add_right_wall_btn.setIconSize(QSize(20,20))
        self.sidebar_layout.addWidget(self.add_right_wall_btn)

        self.add_left_wall_btn = QPushButton("Left Wall")
        self.add_left_wall_btn.clicked.connect(lambda: self.add_plane_with_image("left"))
        self.add_left_wall_btn.setIcon(QIcon(self.scaled_pixmap3))
        self.add_left_wall_btn.setIconSize(QSize(20,20))
        self.sidebar_layout.addWidget(self.add_left_wall_btn)

        self.add_back_wall_btn = QPushButton("Back Wall")
        self.add_back_wall_btn.clicked.connect(lambda: self.add_plane_with_image("back"))
        self.add_back_wall_btn.setIcon(QIcon(self.scaled_pixmap4))
        self.add_back_wall_btn.setIconSize(QSize(20,20))
        self.sidebar_layout.addWidget(self.add_back_wall_btn)

        self.add_front_wall_btn = QPushButton("Front Wall")
        self.add_front_wall_btn.clicked.connect(lambda: self.add_plane_with_image("front"))
        self.add_front_wall_btn.setIcon(QIcon(self.scaled_pixmap5))
        self.add_front_wall_btn.setIconSize(QSize(20,20))
        self.sidebar_layout.addWidget(self.add_front_wall_btn)

        self.add_points_btn = QPushButton("Add Points")
        self.add_points_btn.setIcon(QIcon(self.scaled_pixmap7))
        self.add_points_btn.setIconSize(QSize(20,20))
        self.add_points_btn.clicked.connect(self.open_image_with_interaction)
        self.sidebar_layout.addWidget(self.add_points_btn)

        self.texture_select = QComboBox()
        self.texture_select.addItem("Floor")
        self.texture_select.addItem("Right")
        self.texture_select.addItem("Left")
        self.texture_select.addItem("Back")
        self.texture_select.addItem("Front")
        self.sidebar_layout.addWidget(self.texture_select)

        self.sidebar_layout.addStretch()

        self.caseNumberLabel = QLabel("Case Number:")
        self.sidebar_layout.addWidget(self.caseNumberLabel)
        self.caseNumber = QLineEdit()
        self.sidebar_layout.addWidget(self.caseNumber)

        self.locationLabel = QLabel("Location:")
        self.sidebar_layout.addWidget(self.locationLabel)
        self.location = QLineEdit()
        self.sidebar_layout.addWidget(self.location)

        self.investigatorLabel = QLabel("Investigator:")
        self.sidebar_layout.addWidget(self.investigatorLabel)
        self.investigator = QLineEdit()
        self.sidebar_layout.addWidget(self.investigator)


        self.report = QPushButton("Generate Report")
        self.report.setIcon(QIcon(self.scaled_pixmap6))
        self.report.setIconSize(QSize(20,20))
        self.report.clicked.connect(self.generateReport)  # Fixed connection
        self.sidebar_layout.addWidget(self.report)

        self.simulate = QPushButton("Simulate")
        self.sidebar_layout.addWidget(self.simulate)
        self.simulate.clicked.connect(self.open_blender_file)

        self.sidebar_layout.addStretch()

        self.object_list = QListWidget()
        self.object_list.itemClicked.connect(self.on_object_selected)
        self.sidebar_layout.addWidget(self.object_list)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_object)
        self.sidebar_layout.addWidget(self.delete_button)

        self.load_objects_from_json()

        self.toggle_sidebar_btn = QPushButton("")
        self.toggle_sidebar_btn.setObjectName("sidebarButton")
        self.toggle_sidebar_btn.setFixedSize(20,20)
        self.toggle_sidebar_btn.setIcon(QIcon(self.scaled_pixmap))
        self.toggle_sidebar_btn.setIconSize(QSize(20,20))
        self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)
        self.content_layout.addWidget(self.toggle_sidebar_btn)

        self.content_layout.addWidget(self.sidebar)

        self.main_layout.addLayout(self.content_layout)

        self.bottom_bar = QWidget()
        self.bottom_bar_layout = QHBoxLayout(self.bottom_bar)
        self.bottom_bar.setFixedHeight(35)
        self.InformationHeader = QLabel("Information")
        self.stainCount = QLabel("Spatter Count: 0")
        self.AngleReport = QLabel("Impact Angle: 0")
        self.HeightReport = QLabel("Point of Origin: 0")
        self.Conclusive = QLabel("")
        self.bottom_bar_layout.addWidget(self.InformationHeader)
        self.bottom_bar_layout.addWidget(self.stainCount)
        self.bottom_bar_layout.addWidget(self.AngleReport)
        self.bottom_bar_layout.addWidget(self.HeightReport)
        self.bottom_bar_layout.addWidget(self.Conclusive)

        self.main_layout.addWidget(self.bottom_bar)

        self.add_floor_btn.setEnabled(canEnable)
        self.add_right_wall_btn.setEnabled(canEnable)
        self.add_left_wall_btn.setEnabled(canEnable)
        self.add_back_wall_btn.setEnabled(canEnable)
        self.add_front_wall_btn.setEnabled(canEnable)
        self.add_points_btn.setEnabled(canEnable)
        self.simulate.setEnabled(canEnable)
        self.report.setEnabled(canEnable)
        self.delete_button.setEnabled(canEnable)
        self.object_list.setEnabled(canEnable)

        self.setStyleSheet(self.load_stylesheet(self.get_resource_path("style/style.css")))
        self.init_plot()
        if getattr(sys, 'frozen', False):
            pyi_splash.close()
    

    def load_objects_from_json(self):
        self.json_file = "Data.json"
        try:
            with open(self.json_file,'r') as file:
                self.segments = json.load(file)
                self.update_object_list()
        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Error", "Failure in loading of data")
            self.segments = []
    def update_object_list(self):
        self.object_list.clear()
        for i, segment in enumerate(self.segments):
            item = QListWidgetItem(f"Spatter {i+1}: {segment['angle']}")
            self.object_list.addItem(item)
    def get_resource_path(self, relative_path):
        if getattr(sys, 'frozen', False):  # If the script is run from an executable
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    def on_object_selected(self, item):
        index = self.object_list.row(item)
        selected_segment = self.segments[index]
        
        # Store current orientation
        orientation = self.texture_select.currentText().lower()
        
        # Clear only the lines (meshes) but keep the plane
        actors_to_remove = []
        for actor in self.plotter.renderer.actors.values():
            # Skip the plane actors which have texture
            if not actor.GetTexture():
                actors_to_remove.append(actor)
        
        for actor in actors_to_remove:
            self.plotter.renderer.RemoveActor(actor)
            
        # Redraw all lines with selected one highlighted
        for i, segment in enumerate(self.segments):
            color = "green" if i == index else "red"
            self.generate_3d_line(segment, color)

    def delete_selected_object(self):
        selected_items = self.object_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "No object selected for deletion.")
            return

        for item in selected_items:
            index = self.object_list.row(item)
            del self.segments[index]
            self.update_object_list()

        with open(self.json_file, 'w') as file:
            json.dump(self.segments, file)
            
        # Clear only the lines (meshes) but keep the plane
        actors_to_remove = []
        for actor in self.plotter.renderer.actors.values():
            # Skip the plane actors which have texture
            if not actor.GetTexture():
                actors_to_remove.append(actor)
        
        for actor in actors_to_remove:
            self.plotter.renderer.RemoveActor(actor)
            
        # Redraw all remaining lines
        for segment in self.segments:
            self.generate_3d_line(segment)

    def open_blender_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Simulate", "", "Blender Files (*.blend)")
        if file_path:
            blender_path = r"C:\Users\flore\Downloads\blender-3.0.0-windows-x64\blender-3.0.0-windows-x64\blender.exe"  # Update with your Blender executable path
            try:
                subprocess.run([blender_path, file_path])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error opening Blender file: {e}")

    def load_stylesheet(self, file_path):
        with open(file_path, 'r') as f:
            return f.read()
    
    def init_plot(self):
        self.plotter.clear()
        self.plotter.add_axes()
        self.plotter.background_color = "#3f3f3f"
    
    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()
    
    def load_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_path:
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                texture = pv.read_texture(file_path)
                print(f"Loaded texture from: {file_path}")  # Debug message
                return width, height, texture, file_path
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load texture: {e}")
                return None, None, None, None
        return None, None, None, None
    
    def add_plane_with_image(self, position):
        width, height, texture, image_path = self.load_image() 
        if texture:
            self.default_size = (width, height) 
            self.textures[position] = texture  
            self.image_paths[position] = image_path  
            print(f"Loaded texture for {position}: {image_path}")  # Debug message
        else:
            # Fallback to default size and empty image path
            width, height = self.default_size[0], self.default_size[1]
            texture = None
            if position not in self.image_paths:
                self.image_paths[position] = None

        plane_center = {
            "floor": (0, 0, 0),
            "right": (self.default_size[0] / 2, 0, height / 2),
            "left": (-self.default_size[0] / 2, 0, height / 2),
            "back": (0, -self.default_size[1] / 2, height / 2),
            "front": (0, self.default_size[1] / 2, height / 2),
        }
        plane_direction = {
            "floor": (0, 0, 1),
            "right": (1, 0, 0),
            "left": (-1, 0, 0),
            "back": (0, -1, 0),
            "front": (0, 1, 0),
        }

        if position in plane_center and position in plane_direction:
            i_resolution = width  
            j_resolution = height 

            plane = pv.Plane(
                center=plane_center[position],
                direction=plane_direction[position],
                i_size=width,
                j_size=height,  
                i_resolution=i_resolution, 
                j_resolution=j_resolution, 
            )
            self.plotter.add_mesh(plane, texture=texture, name=f"{position}_plane")
    
    def open_image_with_interaction(self):
        position = self.texture_select.currentText().lower()
        print(f"test: {position}")
        print(f"Loaded texture for {position}: {self.image_paths.get(position)}")
        image_path = self.image_paths.get(position)
        if image_path:
            dialog = SegmentAndMap(image_path, self)
            dialog.dataUpdated.connect(self.update_from_interaction)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "Please load an image for the selected orientation.")
    
    def update_from_interaction(self, json_data):
        # Store current orientation
        orientation = self.texture_select.currentText().lower()
        
        # Clear only the lines (meshes) but keep the plane
        actors_to_remove = []
        for actor in self.plotter.renderer.actors.values():
            # Skip the plane actors which have texture
            if not actor.GetTexture():
                actors_to_remove.append(actor)
        
        for actor in actors_to_remove:
            self.plotter.renderer.RemoveActor(actor)
        
        # Update the JSON data
        self.json_file = "Data.json"
        try:
            with open(self.json_file, 'r') as file:
                current_data = json.load(file)
                if current_data != self.previous_data:
                    self.segments = current_data
                    self.previous_data = current_data
                    print("Data updated from JSON file.")
                else:
                    print("No changes in the data.")
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", f"File {self.json_file} not found.")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error", "Error decoding JSON.")
            
        # Redraw all lines
        for segment in self.segments:
            self.generate_3d_line(segment)
    
    def generate_3d_line(self, segment, color="red"):
        self.update_object_list()
        self.angle = segment["angle"]
        self.start_point_2d = segment["center"]
        self.spatterCount = segment["spatter_count"]
        self.end_point2d = segment["line_endpoints"]["negative_direction"]
        self.impact_angles = []
        orientation = self.texture_select.currentText().lower()

        print(f"test: {self.end_point2d}")

        image_width = self.default_size[0]  
        image_height = self.default_size[1]  
        
        self.impact_angles.append(abs(self.angle))
        # Convert 2D points to origin-relative coordinates
        Ax = self.start_point_2d[0] - image_width / 2  
        Ay = -(self.start_point_2d[1] - image_height / 2)  
        Az = 0

        Bx = self.end_point2d[0] - image_width / 2
        By = -(self.end_point2d[1] - image_height / 2)

        initAx = Ax
        initAy = Ay
        initBx = Bx
        initBy = By

        print(f"Start : {initAx} , {initAy}")
        print(f"End: {Bx} , {By}")

        # Calculate 3D distance
        Bxy = math.sqrt(((initBx - (initAx))**2) + ((initBy - (initAy))**2))
        print(f"height: {Bxy}")

        angleInDeg = self.angle
        Bxyz = math.sin(math.radians(angleInDeg))
        self.Bz = (Bxyz * Bxy)

        match orientation:
            case "floor":
                start_point = np.array([Ax, Ay, Az])
                end_point = np.array([Bx, By, abs(self.Bz)])
            
            case "right":
                start_point = np.array([Az, Ay -image_height/2, (image_height / 2) - Bx])  # Y and Z swapped
                end_point = np.array([self.Bz, By -image_height/2, (image_height / 2) - Ax])  # Y and Z swapped


        # Determine direction of travel
        dx = initBx - initAx
        dy = initBy - initAy

        if dx == 0 and dy == 0:
            self.direction = "No movement"
        else:
            # Calculate angle in 2D space
            angle = math.degrees(math.atan2(dy, dx))
            if angle < 0:
                angle += 360  # Normalize to 0-360 degrees

            # Map angle to direction
            if 22.5 <= angle < 67.5:
                self.direction = "Northeast"
            elif 67.5 <= angle < 112.5:
                self.direction = "North"
            elif 112.5 <= angle < 157.5:
                self.direction = "Northwest"
            elif 157.5 <= angle < 202.5:
                self.direction = "West"
            elif 202.5 <= angle < 247.5:
                self.direction = "Southwest"
            elif 247.5 <= angle < 292.5:
                self.direction = "South"
            elif 292.5 <= angle < 337.5:
                self.direction = "Southeast"
            else:
                self.direction = "East"

        print(f"Direction of Travel: {self.direction}")

        # Add visual representation of line
        line = pv.Line(start_point, end_point)
        self.plotter.add_mesh(line, color=color, line_width=3)
        self.plotter.update()

        self.stainCount.setText(f"Spatter Count: {self.spatterCount}")
        self.AngleReport.setText(f"Impact Angle: {round(self.angle, 2)}")
        self.HeightReport.setText(f"Point Of Origin: {round(self.Bz, 2)} {self.direction}")
        self.Conclusive.setText(f"Classification: Medium Velocity")
    
    def generateReport(self):
        # Fetch inputs from textboxes
        case_number = self.caseNumber.text()
        investigator_name = self.investigator.text()
        location = self.location.text()

        if not case_number or not investigator_name or not location:
            print("Please fill in all the fields before generating the report.")
            return

        file_name = QFileDialog.getSaveFileName(self, "Save Report", "", "Word Document (*.docx)")[0]
        if not file_name:
            return  # Cancel if no file selected

        doc = Document()

        # Title
        doc.add_heading('Bloodstain Pattern Analysis Report', level=1).alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        # Case Details
        doc.add_heading('Case Details', level=2)
        doc.add_paragraph(f"Case Number: {case_number}")
        doc.add_paragraph(f"Investigator Name: {investigator_name}")
        doc.add_paragraph(f"Location of Incident: {location}")
        doc.add_paragraph(f"Date of Incident: {datetime.now().strftime('%Y-%m-%d')}")

        # Other sections remain unchanged...
        doc.add_heading('1. Introduction', level=2)
        doc.add_paragraph("The purpose of this analysis is to evaluate the bloodstain patterns documented at the crime scene and provide insights regarding the events that occurred.")

        doc.add_heading('2. Evidence Documentation', level=2)
        doc.add_paragraph(f"Spatter Count: {self.spatterCount}")

        doc.add_heading('3. Data Analysis', level=2)

        doc.add_heading('a. Estimated Point of Origin', level=3)
        doc.add_paragraph(f"Location: {round(abs(self.end_point2d[0]),2)} millimeters and {self.direction} {round(self.Bz,2)} millimeters off the {self.texture_select.currentText().lower()}")

        doc.add_heading('b. Impact Angles', level=3)
        # Assuming self.impact_angles is a dictionary:
        if hasattr(self, 'impact_angles') and self.impact_angles:
            # Categorize angles by certain ranges (e.g., Low, Medium, High)
            low_angles = [angle for angle in self.impact_angles if angle < 30]
            medium_angles = [angle for angle in self.impact_angles if 30 <= angle < 60]
            high_angles = [angle for angle in self.impact_angles if angle >= 60]

            if low_angles:
                rounded_low_angles = [round(angle, 2) for angle in low_angles]  # Round each angle
                doc.add_paragraph(f"Low Impact Angles: {', '.join(map(str, rounded_low_angles))} degrees")

            if medium_angles:
                rounded_medium_angles = [round(angle, 2) for angle in medium_angles]  # Round each angle
                doc.add_paragraph(f"Medium Impact Angles: {', '.join(map(str, rounded_medium_angles))} degrees")

            if high_angles:
                rounded_high_angles = [round(angle, 2) for angle in high_angles]  # Round each angle
                doc.add_paragraph(f"High Impact Angles: {', '.join(map(str, rounded_high_angles))} degrees")


        # Interpretation and Conclusions
        doc.add_heading('4. Interpretation', level=2)
        doc.add_paragraph("The data suggests a progression from low to medium bloodshed events. The patterns indicate possible blunt force trauma.")

        doc.add_heading('5. Conclusions', level=2)
        doc.add_paragraph("The BPA system data supports the following conclusions:")
        doc.add_paragraph(f"1. The blood source was positioned approximately at {round(abs(self.end_point2d[0]),2)} millimeters {self.direction} of the room's {self.texture_select.currentText().lower()} and {round(self.Bz,2)} millimeters above ground level during the incident.")
        doc.add_paragraph("2. The patterns indicate multiple mechanisms of bloodshed, progressing from low to medium velocity.")
        doc.add_paragraph("3. The findings are consistent with a violent altercation.")

        # Expert's Statement
        doc.add_heading('6. Expert\'s Statement', level=2)
        doc.add_paragraph(f"I, {investigator_name}, certified Bloodstain Pattern Analyst, declare that this report is based on data "
                        "generated by the BPA system and my professional analysis. The conclusions presented are "
                        "consistent with current forensic practices.")
        doc.add_paragraph("Signature:")
        doc.add_paragraph(f"{investigator_name}")
        doc.add_paragraph("Certified Bloodstain Pattern Analyst")

        # Save Document
        try:
            doc.save(file_name)
            print(f"Report saved as {file_name}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save report: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
