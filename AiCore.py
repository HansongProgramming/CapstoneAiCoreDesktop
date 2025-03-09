from imports import *

if getattr(sys, 'frozen', False):
    import pyi_splash

global canEnable
canEnable = False
global active_folder
active_folder = None
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
class MenuButton(QPushButton):
    def __init__(self, main_window, parent=None):
        super().__init__("File", parent)
        self.main_window = main_window
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
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
        self.menu.addAction("Generate Report") 
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
                
                data_file = os.path.join(case_folder, "Data.json")
                with open(data_file, 'w') as json_file:
                    json.dump([], json_file)
                
                assets_file = os.path.join(case_folder, "Assets.json")
                with open(assets_file, 'w') as json_file:
                    json.dump({}, json_file)
                    
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

                # ✅ Reset the 3D Plotter to clear all previous objects
                self.main_window.plotter3D.clear()  # Clears all actors
                self.main_window.plotter3D.renderer.RemoveAllViewProps()  # Ensures complete reset
                self.main_window.plotter3D.update()  # Force refresh

                # ✅ Clear stored references to objects
                self.main_window.segments.clear()
                self.main_window.end_points.clear()
                self.main_window.average_end_point = np.array([0.0, 0.0, 0.0])
                self.main_window.label_Actors.clear()

                # ✅ Reset UI elements related to analysis
                self.main_window.stainCount.setText("Spatter Count: 0")
                self.main_window.AngleReport.setText("Impact Angle: 0")
                self.main_window.HeightReport.setText("Point of Origin: 0")
                self.main_window.Conclusive.setText("")

                # Load assets from the new case
                assets_file = os.path.join(active_folder, "Assets.json")
                if os.path.exists(assets_file):
                    try:
                        with open(assets_file, 'r') as f:
                            assets_data = json.load(f)

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

                                self.main_window.add_plane_with_image(position)
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to load assets: {e}")

                self.main_window.load_objects_from_json()

        elif action.text() == "Generate Report": 
            self.main_window.open_generate_report_dialog()
class EditButton(QPushButton):
    def __init__(self, main_window, parent=None):
        super().__init__("Edit", parent)
        self.main_window = main_window
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
            }
        """)
        
        self.menu = QMenu(self)
        self.dark_menu_style = """
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
        """
        self.light_menu_style = """
            QMenu {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
            }
            QMenu::item:selected {
                background-color: #e6e6e6;
            }
        """
        self.menu.setStyleSheet(self.dark_menu_style)
        
        self.menu.addAction("Undo Action")
        self.menu.addSeparator()
        self.theme_action = self.menu.addAction("Switch to Light Theme")
        self.setMenu(self.menu)
        
        self.menu.triggered.connect(self.handleMenuAction)
        
        self.previous_states = []
        self.is_dark_theme = True

    def handleMenuAction(self, action):
        if action.text() == "Undo Action":
            self.undo_last_action()
        elif action.text() in ["Switch to Light Theme", "Switch to Dark Theme"]:
            self.toggle_theme()

    def toggle_theme(self):
        if self.is_dark_theme:
            stylesheet = self.main_window.load_stylesheet(self.main_window.get_resource_path("style/light.css"))
            self.theme_action.setText("Switch to Dark Theme")
            self.menu.setStyleSheet(self.light_menu_style)
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #333333;
                    border: none;
                }
                QPushButton:hover {
                    background: rgba(0,0,0,0.1);
                }
            """)
            self.main_window.title_bar.file_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #333333;
                    border: none;
                }
                QPushButton:hover {
                    background: rgba(0,0,0,0.1);
                }
            """)
            self.main_window.plotter3D.set_background("white")
            self.main_window.plotter3D.renderer.SetBackground(1, 1, 1)  # Force white background
            self.main_window.plotter3D.render()  # Force update
        else:
            stylesheet = self.main_window.load_stylesheet(self.main_window.get_resource_path("style/style.css"))
            self.theme_action.setText("Switch to Light Theme")
            self.menu.setStyleSheet(self.dark_menu_style)
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
            self.main_window.title_bar.file_btn.setStyleSheet("""
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
            self.main_window.plotter3D.set_background("#3f3f3f")
            self.main_window.plotter3D.renderer.SetBackground(0.25, 0.25, 0.25)  # Force dark gray background
            self.main_window.plotter3D.render()  # Force update


        self.main_window.setStyleSheet(stylesheet)
        self.is_dark_theme = not self.is_dark_theme

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
    def __init__(self, main_window,parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.title = QLabel("AiCore x SpatterSense")
        self.title.setStyleSheet("color: white; font-size: 12px;")
        self.main = main_window

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
        self.placer = QLabel("AiCore x SpatterSense")
        
        self.sidebarIcon = QPixmap(self.get_resource_path("images/sidebar.png"))
        self.scaled_pixmap = self.sidebarIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.toggle_sidebar_btn = QPushButton("")
        self.toggle_sidebar_btn.setObjectName("sidebarButton")
        self.toggle_sidebar_btn.setIcon(QIcon(self.scaled_pixmap))
        self.toggle_sidebar_btn.setIconSize(QSize(30,30))
        self.toggle_sidebar_btn.clicked.connect(self.main.toggle_sidebar)
        
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
        self.layout.addWidget(self.placer)
        self.layout.addStretch(1)
        self.layout.addWidget(self.toggle_sidebar_btn)
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

class AnalysisThread(QThread):
    progress_updated = pyqtSignal(int)
    analysis_done = pyqtSignal(list)
    mask_ready = pyqtSignal(object, object)  # New signal for mask display

    def __init__(self, segment_map_instance, selection_boxes, predictor, image_np, device):
        super().__init__()
        self.segment_map = segment_map_instance  # ✅ Store reference to SegmentAndMap instance
        self.selection_boxes = selection_boxes
        self.predictor = predictor
        self.image_np = image_np
        self.device = device

    def run(self):
        """Runs the selection analysis in a separate thread."""
        try:
            self.predictor.set_image(self.image_np)
            results = []

            for i, box in enumerate(self.selection_boxes):
                # Convert box coordinates to tensor
                input_box = np.array([box['x1'], box['y1'], box['x2'], box['y2']])
                input_box = torch.tensor(input_box, device=self.device)

                # Get masks from predictor
                masks, _, _ = self.predictor.predict(
                    box=input_box[None, :].cpu().numpy(), 
                    multimask_output=False
                )

                if masks is not None and len(masks) > 0:
                    # Process mask in main thread
                    self.mask_ready.emit(masks[0], i)
                    
                    # Calculate angles and data
                    impact_angle, segment_data = self.segment_map.process_spatter(masks[0])
                    results.append(segment_data)

                # Update progress
                self.progress_updated.emit(int((i + 1) / len(self.selection_boxes) * 100))

            self.analysis_done.emit(results)

        except Exception as e:
            print(f"Error in analysis thread: {e}")
class SegmentAndMap(QWidget):
    dataUpdated = pyqtSignal(str)  

    def __init__(self, image_path, jsonPath, position, parent=None):
        super().__init__(parent)
        self.json_file = jsonPath
        self.position = position 
        self.setWindowTitle("Image Interaction")
        self.image_path = image_path
        self.model_path = os.path.abspath(self.get_resource_path('models/sam_vit_b_01ec64.pth'))
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        self.sam_model = sam_model_registry['vit_b'](checkpoint=self.model_path)
        self.sam_model.to(device=self.device)
        self.predictor = SamPredictor(self.sam_model)
        
        self.image_label = QLabel(self)
        self.segmented_masks = []
        self.selection_boxes = []  
        self.selection_rects = []  
        self.mask_item = None
        self.is_ai_select = False
        self.convergence_lines = []
        self.selection_rect = None
        self.analyzing = False  
        self.scale_factor = 1.0
        self.space_pressed = False
        self.mask_display_queue = []
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        print(f"Running on: {self.device}")
        button_layout = QHBoxLayout()
        
        self.analyze_button = QPushButton("Analyze Selections", self)
        self.analyze_button.clicked.connect(self.analyze_selections)
        self.analyze_button.setEnabled(False) 
        button_layout.addWidget(self.analyze_button)

        self.clear_button = QPushButton("Clear All", self)
        self.clear_button.clicked.connect(self.clear_selections)
        button_layout.addWidget(self.clear_button)
        
        self.export_button = QPushButton("Export Scene", self)
        self.export_button.clicked.connect(self.export_scene)
        button_layout.addWidget(self.export_button)

        self.layout.addLayout(button_layout)

        self.graphics_view = QGraphicsView(self)
        self.layout.addWidget(self.graphics_view)

        self.scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)

        self.pixmap = QPixmap(self.image_path)
        self.image_item = QGraphicsPixmapItem(self.pixmap)
        self.image_item.setZValue(0)
        self.scene.addItem(self.image_item)

        img = self.pixmap.toImage()
        ptr = img.bits()
        ptr.setsize(img.byteCount())
        img_array = np.array(ptr).reshape((img.height(), img.width(), 4))
        self.image_np = img_array[:, :, :3]

        self.start_point = None
        self.end_point = None

        self.graphics_view.setMouseTracking(True)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.graphics_view.setDragMode(QGraphicsView.NoDrag)
        
        self.graphics_view.mousePressEvent = self.mouse_press_event
        self.graphics_view.mouseReleaseEvent = self.mouse_release_event
        self.graphics_view.mouseMoveEvent = self.mouse_move_event
        self.graphics_view.wheelEvent = self.wheel_event
        
        self.graphics_view.keyPressEvent = self.key_press_event
        self.graphics_view.keyReleaseEvent = self.key_release_event
        
        self.graphics_view.setFocusPolicy(Qt.StrongFocus)
        
        self.setStyleSheet(self.load_stylesheet(self.get_resource_path("style/style.css")))
        
    def export_scene(self):
        """Export the entire scene as a PNG image."""
        scene_rect = self.scene.sceneRect()
        
        image = QImage(int(scene_rect.width()), int(scene_rect.height()), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        
        self.scene.render(painter, QRectF(image.rect()), scene_rect)
        painter.end()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Scene",
            "",
            "PNG Files (*.png);;All Files (*)"
        )
        
        if file_path:
            if not file_path.lower().endswith('.png'):
                file_path += '.png'
            
            image.save(file_path)

    def get_resource_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_stylesheet(self, file_path):
        with open(file_path, 'r') as f:
            return f.read()

    def wheel_event(self, event):
        if event.modifiers() == Qt.ControlModifier:
            factor = 1.2 if event.angleDelta().y() > 0 else 1/1.2
            self.scale_factor *= factor
            self.graphics_view.scale(factor, factor)
        else:
            super(QGraphicsView, self.graphics_view).wheelEvent(event)

    def key_press_event(self, event):
        if event.key() == Qt.Key_Space:
            self.space_pressed = True
            self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
            self.graphics_view.setCursor(QCursor(Qt.OpenHandCursor))
        super().keyPressEvent(event)

    def key_release_event(self, event):
        if event.key() == Qt.Key_Space:
            self.space_pressed = False
            self.graphics_view.setDragMode(QGraphicsView.NoDrag)
            self.graphics_view.setCursor(QCursor(Qt.ArrowCursor))
        super().keyReleaseEvent(event)

    def mouse_press_event(self, event):
        if event.button() == Qt.LeftButton and not self.analyzing and not self.space_pressed:
            self.start_point = self.graphics_view.mapToScene(event.pos())
            self.selection_rect = QGraphicsRectItem()
            self.selection_rect.setPen(QPen(Qt.red, 2, Qt.DashLine))
            self.selection_rect.setBrush(QBrush(Qt.transparent))
            self.scene.addItem(self.selection_rect)

    def mouse_move_event(self, event):
        if self.start_point and not self.analyzing and not self.space_pressed:
            self.end_point = self.graphics_view.mapToScene(event.pos())
            rect = QRectF(self.start_point, self.end_point).normalized()
            self.selection_rect.setRect(rect)

    def mouse_release_event(self, event):
        if self.start_point and self.selection_rect and not self.analyzing and not self.space_pressed:
            self.end_point = self.graphics_view.mapToScene(event.pos())
            rect = self.selection_rect.rect()
            
            selection_box = {
                'x1': int(rect.left()),
                'y1': int(rect.top()),
                'x2': int(rect.right()),
                'y2': int(rect.bottom())
            }
            self.selection_boxes.append(selection_box)
            self.selection_rects.append(self.selection_rect)
            
            self.analyze_button.setEnabled(True)
            
            self.selection_rect = None
            self.start_point = None
            self.end_point = None

    def analyze_selections(self):
        if self.analyzing or not self.selection_boxes:
            return

        self.analyzing = True
        self.analyze_button.setEnabled(False)

        # Create progress dialog
        self.progress = QProgressDialog("Analyzing selections...", None, 0, 100, self)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setMinimumDuration(0)
        self.progress.setValue(0)

        # Create analysis thread with proper connections
        self.analysis_thread = AnalysisThread(
            self, 
            self.selection_boxes,
            self.predictor,
            self.image_np,
            self.device
        )

        self.analysis_thread.progress_updated.connect(self.update_progress)
        self.analysis_thread.analysis_done.connect(self.on_analysis_complete)
        self.analysis_thread.mask_ready.connect(self.queue_mask_display)

        self.analysis_thread.start()
    def queue_mask_display(self, mask, index):
        """Queue mask for display in main thread"""
        self.mask_display_queue.append((mask, index))
        QTimer.singleShot(0, self.process_mask_queue)

    def process_mask_queue(self):
        """Process queued masks in main thread"""
        if self.mask_display_queue:
            mask, index = self.mask_display_queue.pop(0)
            self.display_mask(mask)
            
    def update_progress(self, value):
        """Updates progress bar in UI"""
        self.progress.setValue(value)

    def on_analysis_complete(self, results):
        """Handles results after analysis finishes."""
        for segment_data in results:
            self.update_json(segment_data)
            json_data = json.dumps(segment_data)
            self.dataUpdated.emit(json_data)

        QTimer.singleShot(0, self.draw_convergence_area)  # ✅ Runs after event loop resumes

        self.analyzing = False
        self.clear_selections()
        self.progress.close()
        self.analyze_button.setEnabled(True)

    def clear_selections(self):
        for rect in self.selection_rects:
            self.scene.removeItem(rect)
        
        self.selection_boxes.clear()
        self.selection_rects.clear()
        
        self.analyze_button.setEnabled(False)

    def display_mask(self, mask):
        if mask is None or mask.sum() == 0:
            return None

        mask_color = np.zeros((*mask.shape, 4), dtype=np.uint8)
        mask_color[mask > 0] = [255, 0, 0, 100]

        height, width = mask.shape
        qimage = QImage(mask_color.data, width, height, QImage.Format_RGBA8888)
        mask_pixmap = QPixmap.fromImage(qimage)
        mask_item = QGraphicsPixmapItem(mask_pixmap)
        mask_item.setZValue(1)
        self.scene.addItem(mask_item)

        return mask_item

    def process_spatter(self, mask):
        y, x = np.where(mask > 0)

        center_x = int(np.mean(x))
        center_y = int(np.mean(y))

        line_angle = self.calculate_angle(mask)  # Used for rotation

        line_endpoints = self.draw_convergence_line(center_x, center_y, line_angle)

        # 🔥 Corrected impact angle calculation using selection width/length
        impact_angle = self.calculate_impact_angle(mask)

        num_spatters = len(self.segmented_masks)

        segment_data = {
            "center": [center_x, center_y],
            "angle": float(90-line_angle),  # Used for rotation
            "impact": float(impact_angle),  # Corrected impact angle
            "line_endpoints": {
                "positive_direction": [int(line_endpoints[0][0]), int(line_endpoints[0][1])],
                "negative_direction": [int(line_endpoints[1][0]), int(line_endpoints[1][1])]
            },
            "spatter_count": num_spatters,
            "origin": self.position
        }
        return impact_angle, segment_data

    def calculate_angle(self, mask):
        y, x = np.where(mask > 0)
        center_x = np.mean(x)
        center_y = np.mean(y)

        points = np.column_stack((x - center_x, y - center_y))
        covariance_matrix = np.cov(points.T)

        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)

        major_axis = eigenvectors[:, 1]

        eccentricity = np.sqrt(1 - (eigenvalues[0] / eigenvalues[1]))

        if eccentricity < 0.3: 
            return 0
        else:
            angle = math.atan2(major_axis[1], major_axis[0]) * 180 / math.pi
            return angle

    def calculate_impact_angle(self, mask):
        """Calculates the impact angle with bounds checking"""
        y, x = np.where(mask > 0)
        
        if len(x) == 0 or len(y) == 0:
            return 0.0

        width = np.ptp(x)
        length = np.ptp(y)

        if length == 0:
            return 0.0

        ratio = np.clip(width / length, -1.0, 1.0)
        
        impact_angle = np.arcsin(ratio) * (180 / np.pi)
        return np.clip(impact_angle, -90.0, 90.0)  

    def draw_convergence_area(self):
        intersections = self.calculate_intersections()

        if intersections:
            # Convert intersections to numpy array
            points = np.array(intersections)

            # Apply DBSCAN clustering to find dense clusters of intersection points
            clustering = DBSCAN(eps=20, min_samples=2).fit(points)
            labels = clustering.labels_

            # Find the largest cluster (excluding noise points labeled as -1)
            unique_labels, counts = np.unique(labels[labels != -1], return_counts=True)
            if unique_labels.size > 0:
                max_cluster_label = unique_labels[np.argmax(counts)]
                cluster_points = points[labels == max_cluster_label]

                # Compute the centroid of the most intersected cluster
                avg_x, avg_y = np.mean(cluster_points, axis=0)

                # Draw a bigger circle at the centroid of the densest cluster
                radius = 30  # Increased radius size
                circle = QGraphicsEllipseItem(avg_x - radius, avg_y - radius, radius * 2, radius * 2)
                circle.setPen(QPen(Qt.blue, 3))  # Thicker blue outline
                circle.setBrush(QBrush(QColor(0, 0, 255, 80)))  # Semi-transparent fill
                circle.setZValue(3)
                self.scene.addItem(circle)
            
    def calculate_intersections(self):
        intersections = []
        lines = [line for pair in self.convergence_lines for line in pair]

        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                p1, p2 = lines[i].line().p1(), lines[i].line().p2()
                p3, p4 = lines[j].line().p1(), lines[j].line().p2()

                intersection_point = self.line_intersection((p1.x(), p1.y(), p2.x(), p2.y()),
                                                            (p3.x(), p3.y(), p4.x(), p4.y()))
                if intersection_point:
                    intersections.append(intersection_point)

        return intersections
    
    def line_intersection(self, line1, line2):
        x1, y1, x2, y2 = line1
        x3, y3, x4, y4 = line2

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None 

        intersect_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
        intersect_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

        return intersect_x, intersect_y

    def draw_convergence_line(self, center_x, center_y, angle):
        step_size = 5

        def draw_line_in_direction(start_x, start_y, angle):
            current_x, current_y = start_x, start_y
            while True:
                next_x = current_x + step_size * math.cos(math.radians(angle))
                next_y = current_y + step_size * math.sin(math.radians(angle))
                if next_x < 0 or next_x > self.pixmap.width() or next_y < 0 or next_y > self.pixmap.height():
                    break
                current_x, current_y = next_x, next_y
            return current_x, current_y

        end_x_pos, end_y_pos = draw_line_in_direction(center_x, center_y, angle)
        end_x_neg, end_y_neg = draw_line_in_direction(center_x, center_y, angle + 180)

        positive_direction = QLineF(QPointF(center_x, center_y),QPointF(end_x_pos, end_y_pos))
        line_item_pos = self.scene.addLine(positive_direction, QPen(Qt.green, 2))
        line_item_pos.setZValue(2)
        self.scene.addItem(line_item_pos)
        
        negative_direction = QLineF(QPointF(center_x, center_y),QPointF(end_x_neg, end_y_neg))
        line_item_neg = self.scene.addLine(negative_direction, QPen(Qt.green, 2))
        line_item_neg.setZValue(2)
        self.scene.addItem(line_item_neg)

        self.convergence_lines.append((line_item_pos, line_item_neg))

        return (end_x_pos, end_y_pos), (end_x_neg, end_y_neg)

    def update_json(self, segment_data):
        highest_number = 0
        
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, "r") as file:
                    data = json.load(file)
                    if data: 
                        highest_number = max(
                            (item.get("segment_number", 0) for item in data),
                            default=0
                        )
            except json.JSONDecodeError:
                data = []
        else:
            data = []

        segment_data["segment_number"] = highest_number + 1
        data.append(segment_data)

        with open(self.json_file, "w") as file:
            json.dump(data, file, indent=4)
class MainWindow(QMainWindow):
    dataUpdated = pyqtSignal(str)
    def __init__(self):
        global canEnable
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

        self.enableUI(canEnable)
        self.resizeEvent(None)

        self.setStyleSheet(self.load_stylesheet(self.get_resource_path("style/style.css")))
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

    def load_objects_from_json(self):
        global active_folder
        if not active_folder:
            QMessageBox.warning(self, "Error", "No active folder selected.")

        self.path = os.path.join(active_folder, "Data.json")
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
            item = QListWidgetItem(f"Spatter {i+1}: {round(int(segment['angle']),2)}")
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
        for actor in self.plotter3D.renderer.actors.values():
            if isinstance(actor, vtk.vtkActor):
                if not actor.GetTexture():
                    actors_to_remove.append(actor)
            
        for actor in actors_to_remove:
            self.plotter3D.renderer.RemoveActor(actor)
            
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

    def load_stylesheet(self, file_path):
        with open(file_path, 'r') as f:
            return f.read()
    
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

        assets_json_path = os.path.join(active_folder, "Assets.json")
        if os.path.exists(assets_json_path):
            try:
                with open(assets_json_path, 'r') as f:
                    assets_data = json.load(f)
                    if position in assets_data:
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

                assets_dir = os.path.join(active_folder, "assets")
                os.makedirs(assets_dir, exist_ok=True)

                _, ext = os.path.splitext(image_path)
                new_filename = f"{position}{ext}"
                new_image_path = os.path.join(assets_dir, new_filename)

                img_resized.save(new_image_path)

                self.default_size = (new_width, new_height)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to downscale image: {e}")
            return

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
            # Clear all existing point labels before adding new plane
            actors_to_remove = []
            for actor in self.plotter3D.renderer.GetActors():
                if isinstance(actor, vtk.vtkActor) or isinstance(actor, vtk.vtkFollower):
                    if not actor.GetTexture():
                        actors_to_remove.append(actor)
            
            for actor in actors_to_remove:
                self.plotter3D.renderer.RemoveActor(actor)

            # Reset end points list when changing planes
            self.end_points = []
            self.average_end_point = np.array([0.0, 0.0, 0.0])

            self.textures[position] = texture
            self.image_paths[position] = new_image_path
            self.create_plane(position, new_width, new_height, texture)
        else:
            width, height = self.default_size
            self.create_plane(position, width, height, None)

    def add_head(self):
        model = self.get_resource_path("figure/head.stl")
        head = pv.read(model)
        translation_vector = self.average_end_point
        head.translate(translation_vector,inplace=True)
        head.scale(5.0)
        self.plotter3D.add_mesh(head, name="head",smooth_shading=False,ambient=0.2,color="white",specular=0.5,specular_power=20)
        
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
        else:
            QMessageBox.warning(self, "Error", "Assets.json not found.")
            return
        self.plotter3D.remove_actor(plane)
        
    def open_image_with_interaction(self):
        global active_folder
        position = self.texture_select.currentText().lower()
        
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
            self.path = os.path.join(active_folder, "Data.json")
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

    def update_from_interaction(self, json_data):
        self.load_objects_from_json()
        
        # Clear all actors including point labels
        actors_to_remove = []
        for actor in self.plotter3D.renderer.GetActors():
            if isinstance(actor, vtk.vtkActor) or isinstance(actor, vtk.vtkFollower):
                if not actor.GetTexture():
                    actors_to_remove.append(actor)
        
        for actor in actors_to_remove:
            self.plotter3D.renderer.RemoveActor(actor)
        
        # Reset end points list when updating
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

    def generate_3d_line(self, segment, color="red"):          
        self.update_object_list()

        label = segment["segment_number"]
        angle = segment["angle"]
        impact = segment["impact"]
        start_point_2d = segment["center"]
        length = self.default_size[0]
        orientation = segment.get("origin", self.texture_select.currentText().lower())
        print(angle)
        print(impact)
        image_width = self.default_size[0]
        image_height = self.default_size[1]

        Ax = start_point_2d[0] - image_width / 2
        Ay = -(start_point_2d[1] - image_height / 2)
        start_point = np.array([Ax, Ay, 0])  
        end_offset = np.array([length, 0, 0])  

        if orientation == "floor":
            rotation_z = R.from_euler('z', (90 + angle), degrees=True) if angle > 0 else R.from_euler('z', (90-angle), degrees=True)
            rotated_offset = rotation_z.apply(end_offset)

            rotation_x = R.from_euler('x', impact, degrees=True) if angle > 0 else R.from_euler('x', -impact, degrees=True)
            final_offset = rotation_x.apply(rotated_offset)
            
        elif orientation == "right":
            start_point = np.array([(self.default_size[0] / 2), Ay, (self.default_size[0] / 2 - Ax)])
            end_offset = np.array([length, 0, 0])  
            rotation_z = R.from_euler('z', -(90 + angle), degrees=True) if angle > 0 else  R.from_euler('z', (90 - angle), degrees=True)
            rotated_offset = rotation_z.apply(end_offset)

            rotation_x = R.from_euler('x', impact, degrees=True)  if angle > 0 else R.from_euler('x', -impact, degrees=True)
            final_offset = rotation_x.apply(rotated_offset)    
                
        elif orientation == "left":
            start_point = np.array([-(self.default_size[0] / 2), Ay, (self.default_size[0] / 2 - Ax)])
            end_offset = np.array([length, 0, 0])  
            rotation_z = R.from_euler('z', -(90 - angle), degrees=True) if angle > 0 else  R.from_euler('z', (90 - angle), degrees=True)
            rotated_offset = rotation_z.apply(end_offset)

            rotation_x = R.from_euler('x', impact, degrees=True)  if angle > 0 else R.from_euler('x', -impact, degrees=True)
            final_offset = rotation_x.apply(rotated_offset) 

        elif orientation == "front":
            start_point = np.array([Ax, (self.default_size[1] / 2), (self.default_size[1] / 2 + Ay)])
            rotation_z = R.from_euler('z', -(90 - angle), degrees=True) if angle > 0 else R.from_euler('z', (90 + -(-angle)), degrees=True)
            rotated_offset = rotation_z.apply(end_offset)

            rotation_x = R.from_euler('x', impact, degrees=True) if angle > 0 else R.from_euler('x', -impact, degrees=True)
            final_offset = rotation_x.apply(rotated_offset)
        
        elif orientation == "back":
            start_point = np.array([Ax, -(self.default_size[1] / 2), (self.default_size[1] / 2 + Ay)])
            rotation_z = R.from_euler('z', (90 - angle), degrees=True) if angle > 0 else R.from_euler('z', (90 + angle), degrees=True)
            rotated_offset = rotation_z.apply(end_offset)

            rotation_x = R.from_euler('x', -impact, degrees=True) if angle > 0 else R.from_euler('x', -impact, degrees=True)
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

        # Store the end points for averaging
        self.end_points.append(end_point)
        self.average_end_point = np.mean(self.end_points, axis=0)

    def open_generate_report_dialog(self):
        self.report_dialog = GenerateReportDialog(self)
        self.report_dialog.exec_()
        
    def generate_report(self, case_number, investigator_name, location):
        if not active_folder:
            QMessageBox.warning(self, "Error", "No active case folder selected.")
            return

        file_name = QFileDialog.getSaveFileName(self, "Save Report", "", "Word Document (*.docx)")[0]
        if not file_name:
            return  

        data_path = os.path.join(active_folder, "Data.json")
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

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.object_list.move(779, 5)
    sys.exit(app.exec_())

