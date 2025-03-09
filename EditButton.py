from imports import *

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