from imports import *

if getattr(sys, 'frozen', False):
    import pyi_splash

class MainWindow(QMainWindow):
    dataUpdated = pyqtSignal(str)
   
# * UI and Main functions
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("AiCore x SpatterSense")
        self.setWindowIcon(QIcon("images/aicore.ico"))
        self.title_bar = TitleBar(self,self)
        self.setGeometry(100, 100, 1200, 800)

        self.label = QLabel("AI Core Viewer", self)
        self.label.setGeometry(10, 10, 780, 30)

        self.default_size = (10, 10)
        self.textures = {}
        self.image_paths = {}
        self.active_folder = None
        self.canEnable = False
        self.segments = []
        self.end_points =[]
        self.label_Actors = []
        self.average_end_point = np.array([0.0, 0.0, 0.0])  
        self.previous_data = None  

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.addWidget(self.title_bar)

        self.content_layout = QHBoxLayout()        
        
        self.tab_layout = QHBoxLayout()
        self.tabs = QTabWidget()
        self.tab_layout.addWidget(self.tabs)
        
        self.viewer3D = QWidget()
        self.viewer_layout3D = QVBoxLayout(self.viewer3D)

        self.plotter3D = QtInteractor(self.viewer3D)
        self.plotter3D.installEventFilter(self)
        self.picker = vtk.vtkCellPicker()
        self.picker.SetTolerance(0.01)
        self.plotter3D.iren.add_observer("LeftButtonPressEvent",self.on_pick)
        self.planes = []
        self.mesh_map = {}
        
        self.object_list = QListWidget(self.viewer3D)
        self.object_list.setFixedSize(120, 200) 

        self.object_list.raise_()
        self.object_list.setParent(self.plotter3D.interactor) 
        self.object_list.itemClicked.connect(self.on_object_selected)
        
        self.docker3d = QHBoxLayout()
        self.selected_plane = QLabel("Selected Plane:")
        self.export = QPushButton("Export")
        self.add_head_btn = QPushButton("Add Head")
        self.close_btn = QPushButton("Hide Spatters")
        self.close_btn.clicked.connect(lambda: (self.object_list.setVisible(not self.object_list.isVisible()),  
                                                self.close_btn.setText("Show Spatters" if self.object_list.isHidden() else "Hide Spatters")))
        self.add_head_btn.clicked.connect(self.add_head)
        self.export.clicked.connect(self.export_plotter)
        self.docker3d.addWidget(self.selected_plane)
        self.docker3d.addWidget(self.add_head_btn)
        self.docker3d.addWidget(self.export)
        self.docker3d.addWidget(self.close_btn)
        
        self.viewer_layout3D.addLayout(self.docker3d)
        self.viewer_layout3D.addWidget(self.plotter3D.interactor)

        self.viewer2D = QWidget()
        self.viewer_layout2D = QHBoxLayout(self.viewer2D)
          
        self.headIcon = QPixmap(self.get_resource_path("images/head.png"))
        self.headscaled = self.headIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.exportIcon = QPixmap(self.get_resource_path("images/Export.png"))
        self.exportscaled = self.exportIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        
        self.add_head_btn.setIcon(QIcon(self.headscaled))
        self.export.setIcon(QIcon(self.exportscaled))
        
        self.tabs.addTab(self.viewer3D, "3D Simulation")
        self.tabs.addTab(self.viewer2D, "2D Analysis")        
        self.content_layout.addLayout(self.tab_layout)
        
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(250)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(12)
        self.shadow.setXOffset(5)
        self.shadow.setYOffset(3)
        self.shadow.setColor(QColor(0,0,0,100))
        self.sidebar.setGraphicsEffect(self.shadow)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        
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
        self.deletePlaneIcon = QPixmap(self.get_resource_path("images/delete.png"))
        self.scaled_pixmap8 = self.deletePlaneIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)

        self.assets_frame = QFrame()
        self.assets_frame.setFrameStyle(QFrame.Raised)
        self.assets_layout = QGridLayout(self.assets_frame)
        
        self.Header3D = QLabel("3D Assets")
        self.sidebar_layout.addWidget(self.Header3D)
        self.sidebar_layout.addWidget(self.assets_frame)

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
        
        self.del_floor_btn = QPushButton()
        self.del_floor_btn.clicked.connect(lambda: self.delete_plane(self.plotter3D.renderer.actors["floor_plane"]))
        self.del_right_wall_btn = QPushButton()
        self.del_right_wall_btn.clicked.connect(lambda: self.delete_plane(self.plotter3D.renderer.actors["right_plane"]))
        self.del_left_wall_btn = QPushButton()
        self.del_left_wall_btn.clicked.connect(lambda: self.delete_plane(self.plotter3D.renderer.actors["left_plane"]))
        self.del_back_wall_btn = QPushButton()
        self.del_back_wall_btn.clicked.connect(lambda: self.delete_plane(self.plotter3D.renderer.actors["back_plane"]))
        self.del_front_wall_btn = QPushButton()
        self.del_front_wall_btn.clicked.connect(lambda: self.delete_plane(self.plotter3D.renderer.actors["front_plane"]))
        
        self.asset_buttons = [ self.add_floor_btn, self.del_floor_btn, self.add_right_wall_btn, self.del_right_wall_btn, self.add_left_wall_btn, self.del_left_wall_btn, self.add_back_wall_btn, self.del_back_wall_btn, self.add_front_wall_btn, self.del_front_wall_btn ]

        for i, button in enumerate(self.asset_buttons):
            row = i // 2
            col = i % 2
            if i % 2 != 0:
                button.setFixedSize(QSize(20,20))
                button.setIcon(QIcon(self.deletePlaneIcon))
            self.assets_layout.addWidget(button, row, col)
            
        self.analysis_label = QLabel("Analysis")
        self.sidebar_layout.addWidget(self.analysis_label)
        
        self.analysis_frame = QFrame()
        self.analysis_frame.setFrameShape(QFrame.StyledPanel)
        self.analysis_frame.setFrameShadow(QFrame.Raised)
        self.analysis_layout = QGridLayout(self.analysis_frame)
                
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
        
        self.analysis_buttons = [self.add_points_btn, self.texture_select]

        for i, button in enumerate(self.analysis_buttons):
            self.analysis_layout.addWidget(button, 0, i)
            
        self.sidebar_layout.addWidget(self.analysis_frame)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_object)
        self.sidebar_layout.addWidget(self.delete_button)
        
        rotate_90_btn = QPushButton("Rotate 90°")
        rotate_neg_90_btn = QPushButton("Rotate -90°")
        flip_h_btn = QPushButton("Flip Horizontal")
        flip_v_btn = QPushButton("Flip Vertical")

        self.sidebar_layout.addWidget(rotate_90_btn)
        self.sidebar_layout.addWidget(rotate_neg_90_btn)
        self.sidebar_layout.addWidget(flip_h_btn)
        self.sidebar_layout.addWidget(flip_v_btn)

        self.sidebar_layout.addStretch()

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

        self.enableUI(self.canEnable)
        self.resizeEvent(None)

        self.setStyleSheet(self.load_stylesheet(self.get_resource_path("style/dark.css")))
        if getattr(sys, 'frozen', False):
            pyi_splash.close()
        self.plotter3D.set_background("#3f3f3f")
        self.configure_plotter()
        
    def update_object_list_position(self):
        viewer_width = self.plotter3D.width()
        viewer_height = self.plotter3D.height()

        list_width = 120
        list_height = 200
        margin = 5 

        new_x = viewer_width - list_width - margin
        new_y = margin
        self.object_list.setGeometry(new_x, new_y, list_width, list_height)
        
    def eventFilter(self, obj, event):
        if obj == self.plotter3D and event.type() == QEvent.Resize:
            self.update_object_list_position()
        return super().eventFilter(obj, event)
    
    def enableUI(self, enabled):
        self.add_floor_btn.setEnabled(enabled)
        self.add_right_wall_btn.setEnabled(enabled)
        self.add_left_wall_btn.setEnabled(enabled)
        self.add_back_wall_btn.setEnabled(enabled)
        self.add_front_wall_btn.setEnabled(enabled)
        self.add_points_btn.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)
        self.object_list.setEnabled(enabled)
        self.del_floor_btn.setEnabled(enabled)
        self.del_right_wall_btn.setEnabled(enabled)
        self.del_left_wall_btn.setEnabled(enabled)
        self.del_back_wall_btn.setEnabled(enabled)
        self.del_front_wall_btn.setEnabled(enabled)
        self.texture_select.setEnabled(enabled)
        self.add_head_btn.setEnabled(enabled)

    def configure_plotter(self):

        renderer = self.plotter3D.renderer
        renderer.LightFollowCameraOff() 
        renderer.remove_all_lights()

        light1 = pv.Light(position=((0-self.default_size[0]/2), 0, self.default_size[1]/2), focal_point=(0, 0, 0), intensity=1.0)
        light2 = pv.Light(position=((self.default_size[0]), 0, self.default_size[1]/2), focal_point=(0, 0, 0), intensity=1.0)
        light3 = pv.Light(position=(0, self.default_size[1], self.default_size[1]/2), focal_point=(0, 0, 0), intensity=1.0)
        light4 = pv.Light(position=(0, (0-self.default_size[1]/2), self.default_size[1]/2), focal_point=(0, 0, 0), intensity=1.0)

        renderer.add_light(light1)
        renderer.add_light(light2)
        renderer.add_light(light3)
        renderer.add_light(light4)
        
        self.ground_plane = pv.Plane(i_size=self.default_size[0] * 2, j_size=self.default_size[0]*2)
        ground_texture = pv.read_texture(self.get_resource_path("images/ground.png"))
        
        
        self.plotter3D.add_mesh(self.ground_plane, texture=ground_texture, name="ground_plane", lighting=False)
        self.plotter3D.add_axes()
        self.plotter3D.show()
        
    def load_stylesheet(self, file_path):
        with open(file_path, 'r') as f:
            return f.read()
        
    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()
    
    def get_resource_path(self, relative_path):
        if getattr(sys, 'frozen', False): 
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def load_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)", options=options)
        if file_path:
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                texture = pv.read_texture(file_path)
                return width, height, texture, file_path
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load texture: {e}")
                return None, None, None, None
        return None, None, None, None
    
    def export_plotter(self):
        opt = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            "",
            "PNG Files (*.png);;All Files (*)",
            options=opt
        )
        
        if file_path: 
            self.plotter3D.screenshot(file_path)
            
    def add_head(self):
        model = self.get_resource_path("figure/head.stl")
        head = pv.read(model)
        translation_vector = self.average_end_point
        head.translate(translation_vector,inplace=True)
        head.scale(5.0)
        self.plotter3D.add_mesh(head, name="head",smooth_shading=False,ambient=0.2,color="white",specular=0.5,specular_power=20)
        
    def update_object_list(self):
        self.object_list.clear()
        for i, segment in enumerate(self.segments):
            item = QListWidgetItem(f"Spatter {i+1}: {round(int(segment['angle']),2)}")
            self.object_list.addItem(item)
        
# * PLANES FUNCTIONS

    def open_image_with_interaction(self):
        position = self.texture_select.currentText().lower()
        
        assets_json_path = os.path.join(self.active_folder, "Assets.json")
        if os.path.exists(assets_json_path):
            try:
                with open(assets_json_path, 'r') as f:
                    assets_data = json.load(f)
                    if position in assets_data:
                        # FIX: Use the original image instead of the scaled one
                        image_path = os.path.join(self.active_folder, assets_data[position]["original"])
                        if os.path.exists(image_path):
                            self.path = os.path.join(self.active_folder, "Data.json")
                            self.json_file = str(self.path)
                            jsonpath = self.json_file
                            dialog = SegmentAndMap(image_path, jsonpath, position, self)
                            dialog.dataUpdated.connect(self.update_from_interaction)

                            for i in reversed(range(self.viewer_layout2D.count())): 
                                self.viewer_layout2D.itemAt(i).widget().setParent(None)
                            
                            self.viewer_layout2D.addWidget(dialog)
                            self.tabs.setCurrentIndex(1) 
                            return
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read Assets.json: {e}")
        image_path = self.image_paths.get(position)
        if image_path:
            self.path = os.path.join(self.active_folder, "Data.json")
            self.json_file = str(self.path)
            jsonpath = self.json_file
            dialog = SegmentAndMap(image_path, jsonpath, position, self)
            dialog.dataUpdated.connect(self.update_from_interaction)
            
            for i in reversed(range(self.viewer_layout2D.count())): 
                self.viewer_layout2D.itemAt(i).widget().setParent(None)
            
            self.viewer_layout2D.addWidget(dialog)
            self.tabs.setCurrentIndex(1)  
        else:
            QMessageBox.warning(self, "Error", "Please load an image for the selected orientation.")

    def create_plane(self, position, width, height, texture):
        self.configure_plotter()
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
                back = self.plotter3D.add_mesh(back_plane, texture=texture, name=f"{position}_plane")
                self.planes.append(back_plane)
                self.mesh_map[back] = "Back"  
            elif position == "front":
                rotationAngle = 90
                front_plane = front_plane.rotate_y(rotationAngle, point=plane_center[position])
                front_plane = front_plane.rotate_z(180, point=plane_center[position])
                front = self.plotter3D.add_mesh(front_plane, texture=texture, name=f"{position}_plane")
                self.planes.append(front_plane)
                self.mesh_map[front] = "Front"
            elif position == "left":
                left_plane.rotate_z(180)
                left = self.plotter3D.add_mesh(left_plane, texture=texture, name=f"{position}_plane")
                self.planes.append(left_plane)
                self.mesh_map[left] = "Left"
            elif position == "right":
                right = self.plotter3D.add_mesh(right_plane, texture=texture, name=f"{position}_plane")
                self.planes.append(right_plane)
                self.mesh_map[right] = "Right"
            elif position == "floor":
                floor = self.plotter3D.add_mesh(floor_plane, texture=texture, name=f"{position}_plane",lighting=False)
                self.planes.append(floor_plane)
                self.mesh_map[floor] = "Floor"
                
    def delete_plane(self, plane):
        assets_json_path = os.path.join(self.active_folder, "Assets.json")
        if os.path.exists(assets_json_path):
            try:
                with open(assets_json_path, 'r') as f:
                    assets_data = json.load(f)
                    for position, relative_path in assets_data.items():
                        full_path = os.path.join(self.active_folder, relative_path)
                        if full_path == self.image_paths.get(position):
                            del assets_data[position]
                            os.remove(full_path)
                            break
                with open(assets_json_path, 'w') as f:
                    json.dump(assets_data, f, indent=4)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete plane: {e}")
                return
        else:
            QMessageBox.warning(self, "Error", "Assets.json not found.")
            return
        self.plotter3D.remove_actor(plane)

    def add_plane_with_image(self, position):
        if not self.active_folder:
            QMessageBox.warning(self, "Error", "No active folder selected.")
            return

        assets_json_path = os.path.join(self.active_folder, "Assets.json")
        assets_dir = os.path.join(self.active_folder, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        if os.path.exists(assets_json_path):
            try:
                with open(assets_json_path, 'r') as f:
                    assets_data = json.load(f)
                    if position in assets_data:
                        scaled_image_path = os.path.join(self.active_folder, assets_data[position]["scaled"])
                        if os.path.exists(scaled_image_path):
                            try:
                                with Image.open(scaled_image_path) as img:
                                    width, height = img.size
                                texture = pv.read_texture(scaled_image_path)
                                self.default_size = (width, height)
                                self.textures[position] = texture
                                self.image_paths[position] = scaled_image_path
                                self.create_plane(position, width, height, texture)
                                return
                            except Exception as e:
                                QMessageBox.warning(self, "Error", f"Failed to load existing texture: {e}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to read Assets.json: {e}")

        width, height, texture, image_path = self.load_image()
        if not image_path:
            return
        
        scale_factor = 0.2
        try:
            with Image.open(image_path) as img:
                old_width, old_height = img.size
                new_width = int(old_width * scale_factor)
                new_height = int(old_height * scale_factor)
                img_resized = img.resize((new_width, new_height))

                _, ext = os.path.splitext(image_path)
                original_filename = f"{position}_original{ext}"
                scaled_filename = f"{position}{ext}"
                original_image_path = os.path.join(assets_dir, original_filename)
                scaled_image_path = os.path.join(assets_dir, scaled_filename)
                
                img.save(original_image_path)  # Save original size
                img_resized.save(scaled_image_path)  # Save scaled image

                self.default_size = (new_width, new_height)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to process images: {e}")
            return

        try:
            if os.path.exists(assets_json_path):
                with open(assets_json_path, 'r') as f:
                    assets_data = json.load(f)
            else:
                assets_data = {}

            assets_data[position] = {"original": os.path.join("assets", original_filename), "scaled": os.path.join("assets", scaled_filename)}
            
            with open(assets_json_path, 'w') as f:
                json.dump(assets_data, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update Assets.json: {e}")
            return

        if texture:
            actors_to_remove = [actor for actor in self.plotter3D.renderer.GetActors() if isinstance(actor, vtk.vtkActor) or isinstance(actor, vtk.vtkFollower) and not actor.GetTexture()]
            
            for actor in actors_to_remove:
                self.plotter3D.renderer.RemoveActor(actor)

            self.end_points = []
            self.average_end_point = np.array([0.0, 0.0, 0.0])

            self.textures[position] = texture
            self.image_paths[position] = scaled_image_path
            self.create_plane(position, new_width, new_height, texture)
        else:
            width, height = self.default_size
            self.create_plane(position, width, height, None)

    def on_pick(self, obj, event):
        click_pos = self.plotter3D.iren.get_event_position()
        self.picker.Pick(click_pos[0], click_pos[1], 0, self.plotter3D.renderer)
        
        actor = self.picker.GetActor()
        if actor and actor in self.mesh_map:
            self.selected_plane.setText(f"Selected Plane: {self.mesh_map[actor]}")
            keyboard.press_and_release('p')
            index = self.texture_select.findText(self.mesh_map[actor])
            print(self.mesh_map[actor])
            print(index)
            if index != -1:
                self.texture_select.setCurrentIndex(index)
                print(index)

# * LINE and Report Functions
    def generate_3d_line(self, segment, color="red"):          
        self.update_object_list()

        label = segment["segment_number"]
        impact = segment["impact"]
        convergence = np.array(segment["convergence_angle_3d"])  
        start_point_2d = np.array(segment["center"])
        length = self.default_size[0] if self.default_size[0] > self.default_size[1] else self.default_size[1]
        orientation = segment.get("origin", self.texture_select.currentText().lower())

        image_width = self.default_size[0]
        image_height = self.default_size[1]

        Ax = (start_point_2d[0] * 0.2) - image_width / 2  
        Ay = -((start_point_2d[1] * 0.2) - image_height / 2)
        start_point = np.array([Ax, Ay, 0])  
        end_offset = np.array([length, 0, 0])  
        
        if convergence < 0:
            impact = - impact
        
        if orientation == "floor":
            rotation_z = R.from_euler('z', convergence, degrees=True)
            rotated_offset = rotation_z.apply(end_offset)

            rotation_x = R.from_euler('x', impact, degrees=True)
            final_offset = rotation_x.apply(rotated_offset)
            
        elif orientation == "right":
            start_point = np.array([(self.default_size[0] / 2), Ay, (self.default_size[0] / 2 - Ax)])
            end_offset = np.array([0, 0, -length])  
            rotation_z = R.from_euler('x', convergence, degrees=True) 
            rotated_offset = rotation_z.apply(end_offset)

            rotation_x = R.from_euler('z', impact, degrees=True)
            final_offset = rotation_x.apply(rotated_offset)    
                
        elif orientation == "left":
            start_point = np.array([-(self.default_size[0] / 2), Ay, (self.default_size[0] / 2 - Ax)])
            end_offset = np.array([0, 0, -length])  
            rotation_z = R.from_euler('x', convergence, degrees=True)
            rotated_offset = rotation_z.apply(end_offset)

            rotation_x = R.from_euler('z', -impact, degrees=True) 
            final_offset = rotation_x.apply(rotated_offset) 

        elif orientation == "front":
            end_offset = np.array([length, 0, 0])  
            start_point = np.array([Ax, (self.default_size[1] / 2), (self.default_size[1] / 2 + Ay)])
            rotation_z = R.from_euler('y', -convergence, degrees=True) 
            rotated_offset = rotation_z.apply(end_offset)

            rotation_x = R.from_euler('x', impact, degrees=True)
            final_offset = rotation_x.apply(rotated_offset)
        
        elif orientation == "back":
            start_point = np.array([Ax, -(self.default_size[1] / 2), (self.default_size[1] / 2 + Ay)])
            rotation_z = R.from_euler('y', convergence, degrees=True) 
            rotated_offset = rotation_z.apply(end_offset)

            rotation_x = R.from_euler('x', impact, degrees=True)
            final_offset = rotation_x.apply(rotated_offset)
            

        end_point = start_point + final_offset

        line = pv.Line(start_point, end_point)

        direction_vector = (start_point - end_point) / np.linalg.norm(start_point - end_point)

        cone_position = start_point
        cone_height = 50 
        cone_radius = 3

        cone = pv.Cone(center=cone_position, direction=direction_vector, radius=cone_radius, height=cone_height)
        
        actor = self.plotter3D.add_point_labels(
            [start_point], [label], render_points_as_spheres=False,
            font_size=12, text_color="white", shape_color=(0, 0, 0, 0.2),
            background_color=None, background_opacity=0.2
        )
        
        self.label_Actors.append(actor)
        
        self.plotter3D.add_mesh(line, color=color, line_width=1.4)
        self.plotter3D.add_mesh(cone, color=color)

        self.plotter3D.update()

        self.Conclusive.setText(f"Classification: Medium Velocity")

        self.end_points.append(end_point)
        self.average_end_point = np.mean(self.end_points, axis=0)

    def open_generate_report_dialog(self):
        self.report_dialog = GenerateReportDialog(self)
        self.report_dialog.exec_()
        
    def generate_report(self, case_number, investigator_name, location):
        if not self.active_folder:
            QMessageBox.warning(self, "Error", "No active case folder selected.")
            return

        file_name = QFileDialog.getSaveFileName(self, "Save Report", "", "Word Document (*.docx)")[0]
        if not file_name:
            return  

        data_path = os.path.join(self.active_folder, "Data.json")
        try:
            with open(data_path, 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.warning(self, "Error", "Failed to load Data.json.")
            return

        spatter_count = len(data) if data else 0
        avg_angle = sum(d["angle"] for d in data) / len(data) if data else 0

        doc = Document()
        doc.add_heading('Bloodstain Pattern Analysis Report', level=1).alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

        doc.add_heading('Case Details', level=2)
        doc.add_paragraph(f"Case Number: {case_number}")
        doc.add_paragraph(f"Investigator Name: {investigator_name}")
        doc.add_paragraph(f"Location of Incident: {location}")
        doc.add_paragraph(f"Date of Incident: {datetime.now().strftime('%Y-%m-%d')}")

        doc.add_heading('1. Evidence Analysis', level=2)
        doc.add_paragraph(f"Total Spatter Count: {spatter_count}")
        doc.add_paragraph(f"Average Impact Angle: {round(avg_angle, 2)}°")

        doc.add_heading('2. Interpretation', level=2)
        doc.add_paragraph("The data suggests a progression from low to medium bloodshed events. The patterns indicate possible blunt force trauma.")

        doc.add_heading('3. Conclusion', level=2)
        doc.add_paragraph(f"The analysis indicates that the blood source was positioned at an estimated impact angle of {round(avg_angle, 2)}°.")

        try:
            doc.save(file_name)
            QMessageBox.information(self, "Success", "Report saved successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save report: {e}")

# * JSON FUNCTIONS
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

        # Remove all 3D actors (including point labels)
        actors_to_remove = []
        for actor in self.plotter3D.renderer.GetActors():
            if isinstance(actor, vtk.vtkActor) or isinstance(actor, vtk.vtkFollower):
                if not actor.GetTexture():
                    actors_to_remove.append(actor)

        for actor in actors_to_remove:
            self.plotter3D.renderer.RemoveActor(actor)

        # Remove point labels
        if hasattr(self, 'label_actors') and self.label_actors:
            for actor in self.label_actors:
                self.plotter3D.remove_actor(actor)
            self.label_actors.clear()

        # Reset stored end points
        self.end_points = []
        self.average_end_point = np.array([0.0, 0.0, 0.0])

        # Redraw remaining spatters
        for segment in self.segments:
            self.generate_3d_line(segment)

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
        for actor in self.plotter3D.renderer.actors.values():
            if isinstance(actor, vtk.vtkActor):
                if not actor.GetTexture():
                    actors_to_remove.append(actor)
            
        for actor in actors_to_remove:
            self.plotter3D.renderer.RemoveActor(actor)
            
        for i, segment in enumerate(self.segments):
            color = "green" if i == index else "red"
            self.generate_3d_line(segment, color)

    def update_from_interaction(self, json_data):
        self.load_objects_from_json()
        
        actors_to_remove = []
        for actor in self.plotter3D.renderer.GetActors():
            if isinstance(actor, vtk.vtkActor) or isinstance(actor, vtk.vtkFollower):
                if not actor.GetTexture():
                    actors_to_remove.append(actor)
        
        for actor in actors_to_remove:
            self.plotter3D.renderer.RemoveActor(actor)
        
        self.end_points = []
        self.average_end_point = np.array([0.0, 0.0, 0.0])
        
        try:
            with open(self.json_file, 'r') as file:
                current_data = json.load(file)
                if current_data != self.previous_data:
                    self.segments = current_data
                    self.previous_data = current_data
                    
                    total_spatters = sum(segment["spatter_count"] for segment in self.segments)
                    avg_angle = sum(segment["angle"] for segment in self.segments) / len(self.segments) if self.segments else 0
                    
                    self.stainCount.setText(f"Spatter Count: {total_spatters}")
                    self.AngleReport.setText(f"Average Impact Angle: {round(avg_angle, 2)}°")
                    
                    avg_bz = 0
                    directions = []
                    for segment in self.segments:
                        start = segment["center"]
                        end = segment["line_endpoints"]["negative_direction"]
                        dx = end[0] - start[0]
                        dy = end[1] - start[1]
                        distance = math.sqrt(dx*dx + dy*dy)
                        bz = distance * math.sin(math.radians(segment["angle"]))
                        avg_bz += bz
                        
                        angle = math.degrees(math.atan2(dy, dx))
                        if angle < 0:
                            angle += 360
                        
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
                    
                    from collections import Counter
                    most_common_direction = Counter(directions).most_common(1)[0][0] if directions else "Unknown"
                    
                    self.HeightReport.setText(f"Average Point of Origin: {round(avg_bz, 2)} mm {most_common_direction}")
                    
                else:
                    QMessageBox.warning(self, "Error", "No changes detected in JSON file.")
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", f"File {self.json_file} not found.")
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error", "Error decoding JSON.")
            
        for segment in self.segments:
            self.generate_3d_line(segment)
            
    def load_objects_from_json(self):
        if not self.active_folder:
            QMessageBox.warning(self, "Error", "No active folder selected.")
            return

        self.path = os.path.join(self.active_folder, "Data.json")
        print(f"[DEBUG] Loading JSON from: {self.path}")  # Debugging log
        
        try:
            with open(self.path, 'r') as file:
                self.segments = json.load(file)
                self.update_object_list()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[DEBUG] Error loading JSON: {e}")  # Debugging log
            QMessageBox.warning(self, "Error", "Failure in loading data")
            self.segments = []

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.object_list.move(779, 5)
    sys.exit(app.exec_())
