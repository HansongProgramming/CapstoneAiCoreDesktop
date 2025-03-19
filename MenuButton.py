from imports import *

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
                self.main_window.active_folder = case_folder 
                self.main_window.enableUI(canEnable)
        elif action.text() == "Open":
            folder_path = QFileDialog.getExistingDirectory(self, "Select Directory for Case")
            if folder_path:
                canEnable = True
                self.main_window.active_folder = folder_path
                self.main_window.load_objects_from_json()
                self.main_window.enableUI(canEnable)
                self.main_window.json_file = os.path.join(folder_path, "Data.json")  # ✅ Ensure JSON is set
                print(f"JSON File Set: {self.main_window.json_file}")  # ✅ Debugging lin

                self.main_window.plotter3D.clear()
                self.main_window.plotter3D.renderer.RemoveAllViewProps()
                self.main_window.plotter3D.update()

                self.main_window.segments.clear()
                self.main_window.end_points.clear()
                self.main_window.average_end_point = np.array([0.0, 0.0, 0.0])
                self.main_window.label_Actors.clear()

                self.main_window.stainCount.setText("Spatter Count: 0")
                self.main_window.AngleReport.setText("Impact Angle: 0")
                self.main_window.HeightReport.setText("Point of Origin: 0")
                self.main_window.Conclusive.setText("")
                self.main_window.load_objects_from_json()

                assets_file = os.path.join(self.main_window.active_folder, "Assets.json")
                if os.path.exists(assets_file):
                    try:
                        with open(assets_file, 'r') as f:
                            assets_data = json.load(f)

                        for position, paths in assets_data.items():
                            if isinstance(paths, dict) and "scaled" in paths:
                                scaled_image_path = os.path.join(self.main_window.active_folder, paths["scaled"])
                                if os.path.exists(scaled_image_path):
                                    texture = pv.read_texture(scaled_image_path)
                                    img = QImage(scaled_image_path)
                                    width, height = img.width(), img.height()

                                    self.main_window.default_size = (width, height)
                                    self.main_window.textures[position] = texture
                                    self.main_window.image_paths[position] = scaled_image_path

                                    self.main_window.add_plane_with_image(position)
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to load assets: {e}")


        elif action.text() == "Generate Report": 
            self.main_window.open_generate_report_dialog()