from imports import *
class EditButton(QPushButton):
    def __init__(self, main_window, parent=None):
        super().__init__("Edit", parent)
        self.main_window = main_window
        self.settings_file = "settings.json"
        self.is_dark_theme = self.load_theme_setting()

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
        self.menu.addAction("Undo Action")
        self.menu.addSeparator()
        self.theme_action = self.menu.addAction("Switch to Light Theme" if self.is_dark_theme else "Switch to Dark Theme")
        self.setMenu(self.menu)
        self.menu.triggered.connect(self.handleMenuAction)
        self.apply_theme(self.is_dark_theme)  # Apply theme on startup
        
        QTimer.singleShot(100, lambda: self.update_icons(self.is_dark_theme)) 


    def handleMenuAction(self, action):
        if action.text() == "Undo Action":
            self.undo_last_action()
        elif action.text() in ["Switch to Light Theme", "Switch to Dark Theme"]:
            self.toggle_theme()

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme(self.is_dark_theme)
        self.save_theme_setting(self.is_dark_theme)

        # Force update the menus to match the theme
        menu_stylesheet = f"""
            QMenu {{
                background-color: {"#2d2d2d" if self.is_dark_theme else "#ffffff"};
                color: {"white" if self.is_dark_theme else "#333333"};
                border: 1px solid {"#3d3d3d" if self.is_dark_theme else "#cccccc"};
            }}
            QMenu::item:selected {{
                background-color: {"#3d3d3d" if self.is_dark_theme else "#e6e6e6"};
                color: {"white" if self.is_dark_theme else "black"};
            }}
        """

        self.menu.setStyleSheet(menu_stylesheet)
        self.main_window.title_bar.file_btn.menu.setStyleSheet(menu_stylesheet)



    def apply_theme(self, is_dark):
        if not hasattr(self.main_window, "plotter3D"):
            return  # Avoid accessing plotter3D before it's initialized

        stylesheet = self.main_window.load_stylesheet(
            self.main_window.get_resource_path("style/dark.css" if is_dark else "style/light.css")
        )
        self.theme_action.setText("Switch to Light Theme" if is_dark else "Switch to Dark Theme")
        self.main_window.setStyleSheet(stylesheet)
        
        for widget in self.main_window.viewer_layout2D.children():
            if isinstance(widget, SegmentAndMap):
                widget.apply_theme(is_dark)

        # Update button colors properly
        button_color = "white" if is_dark else "#333333"
        button_hover = "rgba(255,255,255,0.1)" if is_dark else "rgba(0,0,0,0.1)"

        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {button_color};
                border: none;
            }}
            QPushButton:hover {{
                background: {button_hover};
            }}
        """)

        # Also update the File button in TitleBar
        self.main_window.title_bar.file_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {button_color};
                border: none;
            }}
            QPushButton:hover {{
                background: {button_hover};
            }}
        """)

        # Update menus
        menu_stylesheet = f"""
            QMenu {{
                background-color: {"#2d2d2d" if is_dark else "#ffffff"};
                color: {"white" if is_dark else "#333333"};
                border: 1px solid {"#3d3d3d" if is_dark else "#cccccc"};
            }}
            QMenu::item:selected {{
                background-color: {"#3d3d3d" if is_dark else "#e6e6e6"};
                color: {"white" if is_dark else "black"};
            }}
        """

        self.menu.setStyleSheet(menu_stylesheet)
        self.main_window.title_bar.file_btn.menu.setStyleSheet(menu_stylesheet)

        self.main_window.title_bar.file_btn.menu.setStyleSheet(self.menu.styleSheet())

        # Update background colors safely
        if hasattr(self.main_window, "plotter3D"):
            self.main_window.plotter3D.set_background("#3f3f3f" if is_dark else "white")
            self.main_window.plotter3D.renderer.SetBackground((0.25, 0.25, 0.25) if is_dark else (1, 1, 1))
            self.main_window.plotter3D.render()

        # Update icons
        self.update_icons(is_dark)


    def update_icons(self, is_dark):
        theme_folder = "dark" if is_dark else "light"
        
        minimize_path = self.main_window.get_resource_path(f"images/{theme_folder}/minimize.png")
        maximize_path = self.main_window.get_resource_path(f"images/{theme_folder}/maximize.png")
        exit_path = self.main_window.get_resource_path(f"images/{theme_folder}/exit.png")
        sidebar_path = self.main_window.get_resource_path(f"images/{theme_folder}/sidebar.png")

        self.main_window.title_bar.minimize_btn.setIcon(QIcon(minimize_path))
        self.main_window.title_bar.maximize_btn.setIcon(QIcon(maximize_path))
        self.main_window.title_bar.close_btn.setIcon(QIcon(exit_path))
        self.main_window.title_bar.toggle_sidebar_btn.setIcon(QIcon(sidebar_path))


    def load_theme_setting(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    data = json.load(f)
                    return data.get("dark_mode", True)  # Default to dark mode
            except json.JSONDecodeError:
                return True
        return True

    def save_theme_setting(self, is_dark):
        with open(self.settings_file, "w") as f:
            json.dump({"dark_mode": is_dark}, f)

    def undo_last_action(self):
        if not self.main_window.active_folder:
            QMessageBox.warning(self, "Error", "No active folder selected.")
            return

        json_file = os.path.join(self.main_window.active_folder, "Data.json")
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
