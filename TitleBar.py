from imports import *

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
        self.minimizeIcon = QPixmap(self.get_resource_path("images/dark/minimize.png"))
        self.scaled_pixmap = self.minimizeIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.maximizeIcon = QPixmap(self.get_resource_path("images/dark/maximize.png"))
        self.scaled_pixmap = self.maximizeIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.exitIcon = QPixmap(self.get_resource_path("images/dark/exit.png"))
        self.scaled_pixmap = self.exitIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
        self.minimize_btn = QPushButton()
        self.maximize_btn = QPushButton()
        self.close_btn = QPushButton()
        self.minimize_btn.setIcon(QIcon(self.minimizeIcon))
        self.maximize_btn.setIcon(QIcon(self.maximizeIcon)) 
        self.close_btn.setIcon(QIcon(self.exitIcon))
        self.placer = QLabel("AiCore x SpatterSense")
        
        self.sidebarIcon = QPixmap(self.get_resource_path("images/dark/sidebar.png"))
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
