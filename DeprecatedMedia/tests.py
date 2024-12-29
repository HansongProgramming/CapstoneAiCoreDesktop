def __init__(self):
    super().__init__()
    self.setWindowTitle("AiCore x SpatterSense")
    self.setGeometry(100, 100, 1200, 800)

    self.label = QLabel("AI Core Viewer", self)
    self.label.setGeometry(10, 10, 780, 30)

    self.default_size = (10, 10)
    self.textures = {}
    self.image_paths = {}
    self.segments = []

    self.main_widget = QWidget()
    self.setCentralWidget(self.main_widget)

    # Create a vertical layout for the entire window
    self.main_layout = QVBoxLayout(self.main_widget)

    # Create a horizontal layout for the main content (plotter and sidebar)
    self.content_layout = QHBoxLayout()

    # Plotter
    self.plotter = QtInteractor(self)
    self.content_layout.addWidget(self.plotter.interactor)

    # Sidebar
    self.sidebar = QWidget()
    self.sidebar.setFixedWidth(300)
    self.sidebar_layout = QVBoxLayout(self.sidebar)

    # Sidebar Widgets (Same as your original code)
    self.sidebarIcon = QPixmap("images/sidebar.png")
    self.scaled_pixmap = self.sidebarIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
    self.floorIcon = QPixmap("images/floor.png")
    self.scaled_pixmap1 = self.floorIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
    self.wallrIcon = QPixmap("images/wallR.png")
    self.scaled_pixmap2 = self.wallrIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
    self.walllIcon = QPixmap("images/wallL.png")
    self.scaled_pixmap3 = self.walllIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
    self.wallbIcon = QPixmap("images/wallB.png")
    self.scaled_pixmap4 = self.wallbIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
    self.wallfIcon = QPixmap("images/wallF.png")
    self.scaled_pixmap5 = self.wallfIcon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
    self.generateicon = QPixmap("images/generateicon.png")
    self.scaled_pixmap6 = self.generateicon.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)
    self.selectspatter = QPixmap("images/select spatter.png")
    self.scaled_pixmap7 = self.selectspatter.scaled(500, 500, aspectRatioMode=Qt.KeepAspectRatio)

    # 3D Assets Section
    self.Header3D = QLabel("3D Assets")
    self.add_floor_btn = QPushButton("Floor")
    self.add_floor_btn.clicked.connect(lambda: self.add_plane_with_image("floor"))
    self.add_floor_btn.setIcon(QIcon(self.scaled_pixmap1))
    self.add_floor_btn.setIconSize(QSize(40, 40))
    self.sidebar_layout.addWidget(self.add_floor_btn)

    self.add_right_wall_btn = QPushButton("Right Wall")
    self.add_right_wall_btn.clicked.connect(lambda: self.add_plane_with_image("right"))
    self.add_right_wall_btn.setIcon(QIcon(self.scaled_pixmap2))
    self.add_right_wall_btn.setIconSize(QSize(40, 40))
    self.sidebar_layout.addWidget(self.add_right_wall_btn)

    self.add_left_wall_btn = QPushButton("Left Wall")
    self.add_left_wall_btn.clicked.connect(lambda: self.add_plane_with_image("left"))
    self.add_left_wall_btn.setIcon(QIcon(self.scaled_pixmap3))
    self.add_left_wall_btn.setIconSize(QSize(40, 40))
    self.sidebar_layout.addWidget(self.add_left_wall_btn)

    self.add_back_wall_btn = QPushButton("Back Wall")
    self.add_back_wall_btn.clicked.connect(lambda: self.add_plane_with_image("back"))
    self.add_back_wall_btn.setIcon(QIcon(self.scaled_pixmap4))
    self.add_back_wall_btn.setIconSize(QSize(40, 40))
    self.sidebar_layout.addWidget(self.add_back_wall_btn)

    self.add_front_wall_btn = QPushButton("Front Wall")
    self.add_front_wall_btn.clicked.connect(lambda: self.add_plane_with_image("front"))
    self.add_front_wall_btn.setIcon(QIcon(self.scaled_pixmap5))
    self.add_front_wall_btn.setIconSize(QSize(40, 40))
    self.sidebar_layout.addWidget(self.add_front_wall_btn)

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
# Additional Sidebar Buttons (same as original code)
    # Add other widgets (Walls, etc.)
    self.sidebar_layout.addStretch()

        # Generate Report Button
    self.report = QPushButton("Generate Report")
    self.report.setIcon(QIcon(self.scaled_pixmap6))
    self.report.setIconSize(QSize(40, 40))
    self.report.clicked.connect(self.generateReport)  # Fixed connection
    self.sidebar_layout.addWidget(self.report)

    self.sidebar_layout.addStretch()

    self.add_points_btn = QPushButton("Add Points")
    self.add_points_btn.setIcon(QIcon(self.scaled_pixmap7))
    self.add_points_btn.setIconSize(QSize(40, 40))
    self.add_points_btn.clicked.connect(self.open_image_with_interaction)
    self.sidebar_layout.addWidget(self.add_points_btn)

    self.toggle_sidebar_btn = QPushButton("")
    self.toggle_sidebar_btn.setObjectName("sidebarButton")
    self.toggle_sidebar_btn.setFixedSize(40, 40)
    self.toggle_sidebar_btn.setIcon(QIcon(self.scaled_pixmap))
    self.toggle_sidebar_btn.setIconSize(QSize(40, 40))
    self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)
    self.content_layout.addWidget(self.toggle_sidebar_btn)

    self.content_layout.addWidget(self.sidebar)

    # Add the content layout to the main layout
    self.main_layout.addLayout(self.content_layout)

    # Bottom Bar
    self.bottom_bar = QWidget()
    self.bottom_bar_layout = QHBoxLayout(self.bottom_bar)

    self.texture_select = QComboBox()
    self.texture_select.addItem("Floor")
    self.texture_select.addItem("Right Wall")
    self.texture_select.addItem("Left Wall")
    self.texture_select.addItem("Back Wall")
    self.texture_select.addItem("Front Wall")
    self.sidebar_layout.addWidget(self.texture_select)
    # Move the Information widgets to the bottom bar
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

    # Add the bottom bar to the main layout
    self.main_layout.addWidget(self.bottom_bar)



    # Finalize styles and initialization
    self.setStyleSheet(self.load_stylesheet("style.qss"))
    self.init_plot()
