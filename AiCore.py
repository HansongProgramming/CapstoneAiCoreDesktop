from imports import *


if getattr(sys, 'frozen', False):
    import pyi_splash

global canEnable
canEnable = False
global active_folder
active_folder = None

class MenuButton(QPushButton):
    def __init__(self,main_window, parent=None):
        super().__init__("File", parent)
        self.main_window = main_window
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
        
        
        self.menu.addAction("New Case")
        self.menu.addAction("Open")
        self.menu.addSeparator()
        self.menu.addAction("Exit")
        
        self.setMenu(self.menu)
        
        self.menu.triggered.connect(self.handleMenuAction)

    def handleMenuAction(self, action):
        global canEnable
        global active_folder
        if action.text() == "Exit":
            self.window().close()
        elif action.text() == "New Case":
            folder_path = QFileDialog.getExistingDirectory(self, "Select Directory for New Case")
            if folder_path:
                folder_name, ok = QInputDialog.getText(self, "Folder Name", "Enter a name for the new case folder:")
                case_folder = os.path.join(folder_path, folder_name)
                os.makedirs(case_folder, exist_ok=True)
                
                # Create Data.json
                data_file = os.path.join(case_folder, "Data.json")
                with open(data_file, 'w') as json_file:
                    json.dump([], json_file)
                
                # Create Assets.json
                assets_file = os.path.join(case_folder, "Assets.json")
                with open(assets_file, 'w') as json_file:
                    json.dump({}, json_file)
                
                # Create assets directory
                os.makedirs(os.path.join(case_folder, "assets"), exist_ok=True)
                
                canEnable = True
                active_folder = case_folder 
                self.main_window.enableUI(canEnable)
        elif action.text() == "Open":
            folder_path = QFileDialog.getExistingDirectory(self, "Select Directory for Case")
            if folder_path:
                canEnable = True
                active_folder = folder_path
                self.main_window.enableUI(canEnable)
                
                # Load assets first
                assets_file = os.path.join(active_folder, "Assets.json")
                if os.path.exists(assets_file):
                    try:
                        with open(assets_file, 'r') as f:
                            assets_data = json.load(f)
                        
                        # Load each plane with its image
                        for position, relative_path in assets_data.items():
                            full_path = os.path.join(active_folder, relative_path)
                            if os.path.exists(full_path):
                                texture = pv.read_texture(full_path)
                                img = QImage(full_path)
                                width = img.width()
                                height = img.height()
                                
                                self.main_window.default_size = (width, height)
                                self.main_window.textures[position] = texture
                                self.main_window.image_paths[position] = full_path
                                
                                # Add plane with loaded texture
                                self.main_window.add_plane_with_image(position)
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to load assets: {e}")
                
                # Then load and plot the data
                self.main_window.load_objects_from_json()

class EditButton(QPushButton):
    def __init__(self, main_window, parent=None):
        super().__init__("Edit", parent)
        self.main_window = main_window
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
        
        self.menu.addAction("Undo Action")
        self.setMenu(self.menu)
        
        self.menu.triggered.connect(self.handleMenuAction)
        
        self.previous_states = []

    def handleMenuAction(self, action):
        if action.text() == "Undo Action":
            self.undo_last_action()

    def undo_last_action(self):
        global active_folder
        if not active_folder:
            QMessageBox.warning(self, "Error", "No active folder selected.")
            return

        json_file = os.path.join(active_folder, "Data.json")
        try:
            with open(json_file, 'r') as file:
                current_data = json.load(file)
                
            if len(current_data) > 0:
                current_data.pop()
                
                with open(json_file, 'w') as file:
                    json.dump(current_data, file)
                
                self.main_window.load_objects_from_json()
                QMessageBox.information(self, "Success", "Last action undone successfully.")
            else:
                QMessageBox.warning(self, "Warning", "No actions to undo.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to undo action: {str(e)}")

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.title = QLabel("AiCore x SpatterSense")
        self.title.setStyleSheet("color: white; font-size: 12px;")

        self.AiCoreLabel = QLabel()
        self.AiCoreIcon = QPixmap(self.get_resource_path("images/AiCore.png"))
        self.scaled_pixmap = self.AiCoreIcon.scaled(20, 20, aspectRatioMode=Qt.KeepAspectRatio)
        self.AiCoreLabel.setPixmap(self.scaled_pixmap)
        self.file_btn = MenuButton(parent)
        self.file_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                width: 35px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
            }
        """)
        self.edit_btn = EditButton(parent)
        self.minimizeIcon = QPixmap(self.get_resource_path("images/minimize.png"))
        self.scaled_pixmap = self.minimizeIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.maximizeIcon = QPixmap(self.get_resource_path("images/maximize.png"))
        self.scaled_pixmap = self.maximizeIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.exitIcon = QPixmap(self.get_resource_path("images/exit.png"))
        self.scaled_pixmap = self.exitIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
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
        
        self.layout.addWidget(self.AiCoreLabel)
        self.layout.addWidget(self.file_btn)
        self.layout.addWidget(self.edit_btn)
        self.layout.addStretch(1)
        self.layout.addWidget(self.minimize_btn)
        self.layout.addWidget(self.maximize_btn)
        self.layout.addWidget(self.close_btn)
        
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
        if getattr(sys, 'frozen', False): 
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

        self.assets_frame = QFrame()
        self.assets_frame.setFrameShape(QFrame.StyledPanel)
        self.assets_frame.setFrameShadow(QFrame.Raised)
        self.assets_layout = QGridLayout(self.assets_frame)
        self.sidebar_layout.addWidget(self.assets_frame)
        
        self.Header3D = QLabel("3D Assets")
        self.assets_layout.addWidget(self.Header3D)
        
        self.add_floor_btn = QPushButton("Floor")
        self.add_floor_btn.clicked.connect(lambda: self.add_plane_with_image("floor"))
        self.add_floor_btn.setIcon(QIcon(self.scaled_pixmap1))
        self.add_floor_btn.setIconSize(QSize(20,20))

        self.add_right_wall_btn = QPushButton("Right Wall")
        self.add_right_wall_btn.clicked.connect(lambda: self.add_plane_with_image("right"))
        self.add_right_wall_btn.setIcon(QIcon(self.scaled_pixmap2))
        self.add_right_wall_btn.setIconSize(QSize(20,20))

        self.add_left_wall_btn = QPushButton("Left Wall")
        self.add_left_wall_btn.clicked.connect(lambda: self.add_plane_with_image("left"))
        self.add_left_wall_btn.setIcon(QIcon(self.scaled_pixmap3))
        self.add_left_wall_btn.setIconSize(QSize(20,20))

        self.add_back_wall_btn = QPushButton("Back Wall")
        self.add_back_wall_btn.clicked.connect(lambda: self.add_plane_with_image("back"))
        self.add_back_wall_btn.setIcon(QIcon(self.scaled_pixmap4))
        self.add_back_wall_btn.setIconSize(QSize(20,20))

        self.add_front_wall_btn = QPushButton("Front Wall")
        self.add_front_wall_btn.clicked.connect(lambda: self.add_plane_with_image("front"))
        self.add_front_wall_btn.setIcon(QIcon(self.scaled_pixmap5))
        self.add_front_wall_btn.setIconSize(QSize(20,20))
        
        self.del_floor_btn = QPushButton("x")
        self.del_floor_btn.clicked.connect(lambda: self.delete_plane(self.plotter.renderer.actors["floor_plane"]))
        self.del_right_wall_btn = QPushButton("x")
        self.del_right_wall_btn.clicked.connect(lambda: self.delete_plane(self.plotter.renderer.actors["right_plane"]))
        self.del_left_wall_btn = QPushButton("x")
        self.del_left_wall_btn.clicked.connect(lambda: self.delete_plane(self.plotter.renderer.actors["left_plane"]))
        self.del_back_wall_btn = QPushButton("x")
        self.del_back_wall_btn.clicked.connect(lambda: self.delete_plane(self.plotter.renderer.actors["back_plane"]))
        self.del_front_wall_btn = QPushButton("x")
        self.del_front_wall_btn.clicked.connect(lambda: self.delete_plane(self.plotter.renderer.actors["front_plane"]))
        
        self.buttons = [ self.add_floor_btn, self.del_floor_btn, self.add_right_wall_btn, self.del_right_wall_btn, self.add_left_wall_btn, self.del_left_wall_btn, self.add_back_wall_btn, self.del_back_wall_btn, self.add_front_wall_btn, self.del_front_wall_btn ]

        for i, button in enumerate(self.buttons):
            row = i // 2
            col = i % 2
            self.assets_layout.addWidget(button, row, col)
        
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

        self.ObjectListLabel = QLabel("Spatters:")
        self.sidebar_layout.addWidget(self.ObjectListLabel)
        self.object_list = QListWidget()
        self.object_list.itemClicked.connect(self.on_object_selected)
        self.sidebar_layout.addWidget(self.object_list)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_object)
        self.sidebar_layout.addWidget(self.delete_button)

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
        self.report.clicked.connect(self.generateReport)
        self.sidebar_layout.addWidget(self.report)

        self.simulate = QPushButton("Simulate")
        self.sidebar_layout.addWidget(self.simulate)
        self.simulate.clicked.connect(self.open_blender_file)

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

        self.enableUI(canEnable)

        self.setStyleSheet(self.load_stylesheet(self.get_resource_path("style/style.css")))
        self.init_plot()
        if getattr(sys, 'frozen', False):
            pyi_splash.close()

    def enableUI(self, enabled):
        print("UI Enabled", enabled)
        self.add_floor_btn.setEnabled(enabled)
        self.add_right_wall_btn.setEnabled(enabled)
        self.add_left_wall_btn.setEnabled(enabled)
        self.add_back_wall_btn.setEnabled(enabled)
        self.add_front_wall_btn.setEnabled(enabled)
        self.add_points_btn.setEnabled(enabled)
        self.simulate.setEnabled(enabled)
        self.report.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)
        self.object_list.setEnabled(enabled)

    def load_objects_from_json(self):
        global active_folder
        if not active_folder:
            QMessageBox.warning(self, "Error", "No active folder selected.")

        self.path = os.path.join(active_folder, "Data.json")
        print(self.path)
        self.json_file = str(self.path)
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
        if getattr(sys, 'frozen', False): 
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def on_object_selected(self, item):
        index = self.object_list.row(item)
        selected_segment = self.segments[index]
        
        self.AngleReport.setText(f"Impact Angle: {round(selected_segment['angle'], 2)}°")

        start = selected_segment["center"]
        end = selected_segment["line_endpoints"]["negative_direction"]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.sqrt(dx*dx + dy*dy)
        bz = distance * math.sin(math.radians(selected_segment["angle"]))
        
        angle = math.degrees(math.atan2(dy, dx))
        if angle < 0:
            angle += 360
        
        direction = "East"
        if 22.5 <= angle < 67.5:
            direction = "Northeast"
        elif 67.5 <= angle < 112.5:
            direction = "North"
        elif 112.5 <= angle < 157.5:
            direction = "Northwest"
        elif 157.5 <= angle < 202.5:
            direction = "West"
        elif 202.5 <= angle < 247.5:
            direction = "Southwest"
        elif 247.5 <= angle < 292.5:
            direction = "South"
        elif 292.5 <= angle < 337.5:
            direction = "Southeast"
        
        self.HeightReport.setText(f"Point of Origin: {round(bz, 2)} mm {direction}")
        
        orientation = self.texture_select.currentText().lower()
        actors_to_remove = []
        for actor in self.plotter.renderer.actors.values():
            if not actor.GetTexture():
                actors_to_remove.append(actor)
        
        for actor in actors_to_remove:
            self.plotter.renderer.RemoveActor(actor)
            
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
            
        actors_to_remove = []
        for actor in self.plotter.renderer.actors.values():
            if not actor.GetTexture():
                actors_to_remove.append(actor)
        
        for actor in actors_to_remove:
            self.plotter.renderer.RemoveActor(actor)
            
        for segment in self.segments:
            self.generate_3d_line(segment)

    def open_blender_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Simulate", "", "Blender Files (*.blend)")
        if file_path:
            blender_path = r"D:\Academics\CIT7\CapstoneAiCoreDesktop\blender\blender-3.6.0-windows-x64\blender.exe"
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
                print(f"Loaded texture from: {file_path}")  
                return width, height, texture, file_path
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load texture: {e}")
                return None, None, None, None
        return None, None, None, None
    
    def add_plane_with_image(self, position):
            global active_folder
            if not active_folder:
                QMessageBox.warning(self, "Error", "No active folder selected.")
                return

            # First check if image already exists in Assets.json
            assets_json_path = os.path.join(active_folder, "Assets.json")
            if os.path.exists(assets_json_path):
                try:
                    with open(assets_json_path, 'r') as f:
                        assets_data = json.load(f)
                        if position in assets_data:
                            # Image already exists, load it directly
                            image_path = os.path.join(active_folder, assets_data[position])
                            if os.path.exists(image_path):
                                try:
                                    with Image.open(image_path) as img:
                                        width, height = img.size
                                    texture = pv.read_texture(image_path)
                                    self.default_size = (width, height)
                                    self.textures[position] = texture
                                    self.image_paths[position] = image_path
                                    self.create_plane(position, width, height, texture)
                                    return
                                except Exception as e:
                                    QMessageBox.warning(self, "Error", f"Failed to load existing texture: {e}")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to read Assets.json: {e}")

            # If no existing image found, proceed with selecting new image
            width, height, texture, image_path = self.load_image()
            if not image_path:
                return

            # Create assets directory if it doesn't exist
            assets_dir = os.path.join(active_folder, "assets")
            os.makedirs(assets_dir, exist_ok=True)

            # Get the file extension from original image
            _, ext = os.path.splitext(image_path)
            
            # Create new filename based on position
            new_filename = f"{position}{ext}"
            new_image_path = os.path.join(assets_dir, new_filename)

            # Copy the image file
            try:
                import shutil
                shutil.copy2(image_path, new_image_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to copy image: {e}")
                return

            # Update Assets.json
            try:
                if os.path.exists(assets_json_path):
                    with open(assets_json_path, 'r') as f:
                        assets_data = json.load(f)
                else:
                    assets_data = {}

                assets_data[position] = os.path.join("assets", new_filename)

                with open(assets_json_path, 'w') as f:
                    json.dump(assets_data, f, indent=4)

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to update Assets.json: {e}")
                return

            if texture:
                self.default_size = (width, height)
                self.textures[position] = texture
                self.image_paths[position] = new_image_path
                self.create_plane(position, width, height, texture)
            else:
                width, height = self.default_size[0], self.default_size[1]
                self.create_plane(position, width, height, None)

    def create_plane(self, position, width, height, texture):
            plane_center = {
                "floor": (0, 0, 0),
                "right": (self.default_size[0] / 2, 0, self.default_size[0]/2),
                "left":  (-self.default_size[0] / 2, 0, self.default_size[0]/2),
                "back":  (0, -self.default_size[1] / 2, self.default_size[1] / 2),
                "front": (0, self.default_size[1] / 2, self.default_size[1] / 2),
            }
            plane_direction = {
                "floor": (0, 0, 1),
                "right": (1, 0, 0),
                "left": (1, 0, 0),
                "back": (0, -1, 0),
                "front": (0, 1, 0),
            }

            if position in plane_center and position in plane_direction:
                i_resolution = width
                j_resolution = height

                floor_plane = pv.Plane(center=plane_center[position],direction=plane_direction[position],i_size=width,j_size=height,i_resolution=i_resolution,j_resolution=j_resolution,)
                right_plane = pv.Plane(center=plane_center[position],direction=plane_direction[position],i_size=width,j_size=height,i_resolution=i_resolution,j_resolution=j_resolution,)
                left_plane = pv.Plane(center=plane_center[position],direction=plane_direction[position],i_size=width,j_size=height,i_resolution=i_resolution,j_resolution=j_resolution,)
                front_plane = pv.Plane(center=plane_center[position],direction=plane_direction[position],i_size=width,j_size=height,i_resolution=i_resolution,j_resolution=j_resolution,)
                back_plane = pv.Plane(center=plane_center[position],direction=plane_direction[position],i_size=width,j_size=height,i_resolution=i_resolution,j_resolution=j_resolution,)

                if position == "back":
                    rotationAngle = -90
                    back_plane = back_plane.rotate_y(rotationAngle, point=plane_center[position])
                    self.plotter.add_mesh(back_plane, texture=texture, name=f"{position}_plane")
                elif position == "front":
                    rotationAngle = 90
                    front_plane = front_plane.rotate_y(rotationAngle, point=plane_center[position])
                    front_plane = front_plane.rotate_z(180, point=plane_center[position])
                    self.plotter.add_mesh(front_plane, texture=texture, name=f"{position}_plane")
                elif position == "left":
                    left_plane.rotate_z(180)
                    self.plotter.add_mesh(left_plane, texture=texture, name=f"{position}_plane")
                elif position == "right":
                    self.plotter.add_mesh(right_plane, texture=texture, name=f"{position}_plane")
                elif position == "floor":
                    self.plotter.add_mesh(floor_plane, texture=texture, name=f"{position}_plane")
    
    def delete_plane(self, plane):
        global active_folder
        assets_json_path = os.path.join(active_folder, "Assets.json")
        if os.path.exists(assets_json_path):
            try:
                with open(assets_json_path, 'r') as f:
                    assets_data = json.load(f)
                    for position, relative_path in assets_data.items():
                        full_path = os.path.join(active_folder, relative_path)
                        if full_path == self.image_paths.get(position):
                            del assets_data[position]
                            os.remove(full_path)
                            break
                with open(assets_json_path, 'w') as f:
                    json.dump(assets_data, f, indent=4)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete plane: {e}")
                return
        self.plotter.remove_actor(plane)

    def open_image_with_interaction(self):
        global active_folder
        position = self.texture_select.currentText().lower()
        
        # Try to get image path from Assets.json first
        assets_json_path = os.path.join(active_folder, "Assets.json")
        if os.path.exists(assets_json_path):
            try:
                with open(assets_json_path, 'r') as f:
                    assets_data = json.load(f)
                    if position in assets_data:
                        image_path = os.path.join(active_folder, assets_data[position])
                        if os.path.exists(image_path):
                            self.path = os.path.join(active_folder, "Data.json")
                            self.json_file = str(self.path)
                            jsonpath = self.json_file
                            dialog = SegmentAndMap(image_path, jsonpath, self)
                            dialog.dataUpdated.connect(self.update_from_interaction)
                            dialog.exec_()
                            return
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read Assets.json: {e}")
        
        # Fallback to old behavior if Assets.json doesn't exist or doesn't have the image
        image_path = self.image_paths.get(position)
        if image_path:
            self.path = os.path.join(active_folder, "Data.json")
            self.json_file = str(self.path)
            jsonpath = self.json_file
            dialog = SegmentAndMap(image_path, jsonpath, self)
            dialog.dataUpdated.connect(self.update_from_interaction)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "Please load an image for the selected orientation.")

    
    def update_from_interaction(self, json_data):
        self.load_objects_from_json()
        
        # Clear existing lines
        actors_to_remove = []
        for actor in self.plotter.renderer.actors.values():
            if not actor.GetTexture():
                actors_to_remove.append(actor)
        
        for actor in actors_to_remove:
            self.plotter.renderer.RemoveActor(actor)
        
        try:
            with open(self.json_file, 'r') as file:
                current_data = json.load(file)
                if current_data != self.previous_data:
                    self.segments = current_data
                    self.previous_data = current_data
                    
                    # Update information labels
                    total_spatters = sum(segment["spatter_count"] for segment in self.segments)
                    avg_angle = sum(segment["angle"] for segment in self.segments) / len(self.segments) if self.segments else 0
                    
                    self.stainCount.setText(f"Spatter Count: {total_spatters}")
                    self.AngleReport.setText(f"Average Impact Angle: {round(avg_angle, 2)}°")
                    
                    # Calculate average point of origin
                    avg_bz = 0
                    directions = []
                    for segment in self.segments:
                        # Calculate Bz for each segment
                        start = segment["center"]
                        end = segment["line_endpoints"]["negative_direction"]
                        dx = end[0] - start[0]
                        dy = end[1] - start[1]
                        distance = math.sqrt(dx*dx + dy*dy)
                        bz = distance * math.sin(math.radians(segment["angle"]))
                        avg_bz += bz
                        
                        # Get direction
                        angle = math.degrees(math.atan2(dy, dx))
                        if angle < 0:
                            angle += 360
                        
                        # Map angle to direction
                        if 22.5 <= angle < 67.5:
                            directions.append("Northeast")
                        elif 67.5 <= angle < 112.5:
                            directions.append("North")
                        elif 112.5 <= angle < 157.5:
                            directions.append("Northwest")
                        elif 157.5 <= angle < 202.5:
                            directions.append("West")
                        elif 202.5 <= angle < 247.5:
                            directions.append("Southwest")
                        elif 247.5 <= angle < 292.5:
                            directions.append("South")
                        elif 292.5 <= angle < 337.5:
                            directions.append("Southeast")
                        else:
                            directions.append("East")
                    
                    avg_bz = avg_bz / len(self.segments) if self.segments else 0
                    
                    # Get most common direction
                    from collections import Counter
                    most_common_direction = Counter(directions).most_common(1)[0][0] if directions else "Unknown"
                    
                    self.HeightReport.setText(f"Average Point of Origin: {round(avg_bz, 2)} mm {most_common_direction}")
                    
                    print("Data updated from JSON file.")
                else:
                    print("No changes in the data.")
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", f"File {self.json_file} not found.")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error", "Error decoding JSON.")
            
        for segment in self.segments:
            self.generate_3d_line(segment)
            
    def generate_3d_line(self, segment, color="red"):
        self.update_object_list()
        self.angle = segment["angle"]
        self.start_point_2d = segment["center"]
        self.spatterCount = segment["spatter_count"]
        self.end_point2d = segment["line_endpoints"]["negative_direction"]
        self.impact_angles = []
        
        orientation = segment.get("origin", self.texture_select.currentText().lower())

        image_width = self.default_size[0]
        image_height = self.default_size[1]

        self.impact_angles.append(abs(self.angle))

        Ax = self.start_point_2d[0] - image_width / 2
        Ay = -(self.start_point_2d[1] - image_height / 2)
        Az = 0

        Bx = self.end_point2d[0] - image_width / 2
        By = -(self.end_point2d[1] - image_height / 2)

        Bxy = math.sqrt(((Bx - Ax) ** 2) + ((By - Ay) ** 2))
        angleInDeg = self.angle
        Bxyz = math.sin(math.radians(angleInDeg))
        self.Bz = (Bxyz * Bxy)

        start_point = np.array([Ax, Ay, Az])
        end_point = np.array([Bx, By, abs(self.Bz)])

        dx = Bx - Ax
        dy = By - Ay
        if dx == 0 and dy == 0:
            self.direction = "No movement"
        else:
            angle = math.degrees(math.atan2(dy, dx))
            if angle < 0:
                angle += 360

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
        
        print(end_point)

        if orientation == "right":
            start_point = np.array([(self.default_size[0] / 2), Ay, (self.default_size[0] / 2 - Ax)])
            end_point = np.array([(Bx - self.default_size[0] / 2), (self.default_size[1]/2 + By), (self.default_size[0] / 2 - Bx)])
        elif orientation == "left":
            start_point = np.array([-(self.default_size[0] / 2), Ay, (self.default_size[0] / 2 - Ax)])
            end_point = np.array([(self.default_size[0] / 2 - Bx), (self.default_size[1]/2 + By), (self.default_size[0] / 2 - Bx)])
        elif orientation == "back":
            start_point = np.array([Ax, -(self.default_size[1] / 2), (self.default_size[1] / 2 + Ay)])
            end_point = np.array([(Bx - self.default_size[0] / 2), (self.default_size[1] /2 + By), (self.default_size[1] / 2 + By)])
        elif orientation == "front":
            start_point = np.array([Ax, (self.default_size[1] / 2), (self.default_size[1] / 2 + Ay)])
            end_point = np.array([(Bx - self.default_size[0] / 2), -(self.default_size[1] / 2 + By), (self.default_size[1] / 2 + By)])

        line = pv.Arrow(
            start_point, 
            end_point, 
            tip_length=0.05,
            tip_radius=0.009, 
            tip_resolution=20,
            shaft_radius=0.001,
            scale=self.default_size[0]
        )
        print(end_point)
        self.plotter.add_mesh(line, color=color, line_width=3)
        self.plotter.update()

        self.Conclusive.setText(f"Classification: Medium Velocity")


    
    def generateReport(self):
        case_number = self.caseNumber.text()
        investigator_name = self.investigator.text()
        location = self.location.text()

        if not case_number or not investigator_name or not location:
            print("Please fill in all the fields before generating the report.")
            return

        file_name = QFileDialog.getSaveFileName(self, "Save Report", "", "Word Document (*.docx)")[0]
        if not file_name:
            return  

        doc = Document()

        doc.add_heading('Bloodstain Pattern Analysis Report', level=1).alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

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
