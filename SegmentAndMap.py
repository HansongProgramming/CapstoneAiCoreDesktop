from imports import *
class SegmentAndMap(QWidget):
    dataUpdated = pyqtSignal(str)  

    def __init__(self, image_path, jsonPath, position,main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window  # Store reference to MainWindow
        self.json_file = jsonPath
        self.position = position 
        self.image_path = image_path
        self.model_path = os.path.abspath(self.get_resource_path('models/sam_vit_b_01ec64.pth'))
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
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
        self.apply_theme(self.main_window.is_dark_theme)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
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
        
        
    def apply_theme(self, is_dark):
        print(f"Applying theme in SegmentAndMap: {'Dark' if is_dark else 'Light'}")  # Debugging
        stylesheet = self.main_window.load_stylesheet(
            self.main_window.get_resource_path("style/dark.css" if is_dark else "style/light.css")
        )
        self.setStyleSheet(stylesheet)
    def export_scene(self):
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

    def queue_mask_display(self, mask, index):
        self.mask_display_queue.append((mask, index))
        QTimer.singleShot(0, self.process_mask_queue)

    def process_mask_queue(self):
        if self.mask_display_queue:
            mask, index = self.mask_display_queue.pop(0)
            self.display_mask(mask)
            
    def update_progress(self, value):
        self.progress.setValue(value)

    def on_analysis_complete(self, results):
        for segment_data in results:
            self.update_json(segment_data)
            json_data = json.dumps(segment_data)
            self.dataUpdated.emit(json_data)

        QTimer.singleShot(0, self.draw_convergence_area)

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
        if self.mask_item is not None:
            self.scene.removeItem(self.mask_item)
        self.mask_item = mask_item
        self.scene.addItem(self.mask_item)

        return mask_item

# ! CALCULATIONS AND SPATTER PROCESSING

    def process_spatter(self, mask):
        y, x = np.where(mask > 0)
        
        if len(x) == 0 or len(y) == 0:  # Avoid NaN errors
            print("Warning: Empty mask detected in process_spatter")
            return None, None  # Return None instead of crashing

        center_x = int(np.mean(x))
        center_y = int(np.mean(y))
        
        line_angle = self.calculate_angle(mask)  
        line_endpoints = self.draw_convergence_line(center_x, center_y, line_angle)
        impact_angle = self.calculate_impact_angle(mask)

        num_spatters = len(self.segmented_masks)

        if hasattr(self, "convergence_area_center") and hasattr(self, "convergence_area_radius"):
            entry_point = self.find_line_circle_intersection(line_endpoints, self.convergence_area_center, self.convergence_area_radius)
        else:
            entry_point = None

        if entry_point:
            dx = entry_point[0] - center_x
            dy = entry_point[1] - center_y
            raw_angle = math.degrees(math.atan2(dy, dx))  
            angle_3d = -raw_angle  
        else:
            angle_3d = None  

        # Ensure positive_direction is closest to convergence_area_center
        if hasattr(self, "convergence_area_center"):
            cx, cy = self.convergence_area_center

            # Compute distances from both endpoints to convergence center
            d1 = (line_endpoints[0][0] - cx) ** 2 + (line_endpoints[0][1] - cy) ** 2
            d2 = (line_endpoints[1][0] - cx) ** 2 + (line_endpoints[1][1] - cy) ** 2

            # Assign based on closest distance
            if d1 < d2:
                positive_direction = line_endpoints[0]
                negative_direction = line_endpoints[1]
            else:
                positive_direction = line_endpoints[1]
                negative_direction = line_endpoints[0]
        else:
            positive_direction = line_endpoints[0]
            negative_direction = line_endpoints[1]

        segment_data = {
            "center": [center_x, center_y],
            "angle": float(90 - line_angle),  
            "impact": float(impact_angle),  
            "line_endpoints": {
                "positive_direction": [int(positive_direction[0]), int(positive_direction[1])],
                "negative_direction": [int(negative_direction[0]), int(negative_direction[1])]
            },
            "spatter_count": num_spatters,
            "origin": self.position,
            "convergence_entry_point": entry_point,  
            "convergence_angle_3d": angle_3d  
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
            points = np.array(intersections)

            clustering = DBSCAN(eps=20, min_samples=2).fit(points)
            labels = clustering.labels_

            unique_labels, counts = np.unique(labels[labels != -1], return_counts=True)
            if unique_labels.size > 0:
                max_cluster_label = unique_labels[np.argmax(counts)]
                cluster_points = points[labels == max_cluster_label]

                avg_x, avg_y = np.mean(cluster_points, axis=0)
                self.convergence_area_center = [int(avg_x), int(avg_y)]
                self.convergence_area_radius = 30  

                circle = QGraphicsEllipseItem(avg_x - self.convergence_area_radius, avg_y - self.convergence_area_radius,
                                            self.convergence_area_radius * 2, self.convergence_area_radius * 2)
                circle.setPen(QPen(Qt.blue, 3))
                circle.setBrush(QBrush(QColor(0, 0, 255, 80)))
                circle.setZValue(3)
                self.scene.addItem(circle)
                
    def find_line_circle_intersection(self, line_endpoints, circle_center, radius):
        (x1, y1), (x2, y2) = line_endpoints
        cx, cy = circle_center

        dx = x2 - x1
        dy = y2 - y1
        fx = x1 - cx
        fy = y1 - cy

        a = dx * dx + dy * dy
        b = 2 * (fx * dx + fy * dy)
        c = (fx * fx + fy * fy) - radius * radius

        discriminant = b * b - 4 * a * c

        if discriminant < 0:

            dist1 = math.sqrt((x1 - cx) ** 2 + (y1 - cy) ** 2)
            dist2 = math.sqrt((x2 - cx) ** 2 + (y2 - cy) ** 2)
            
            closest_point = (x1, y1) if dist1 < dist2 else (x2, y2)
            return closest_point 

        discriminant = math.sqrt(discriminant)

        t1 = (-b - discriminant) / (2 * a)
        t2 = (-b + discriminant) / (2 * a)

        intersections = []
        for t in [t1, t2]:
            if 0 <= t <= 1:  
                inter_x = x1 + t * dx
                inter_y = y1 + t * dy
                intersections.append((inter_x, inter_y))

        if intersections:
            return intersections[0]  

        dist1 = math.sqrt((x1 - cx) ** 2 + (y1 - cy) ** 2)
        dist2 = math.sqrt((x2 - cx) ** 2 + (y2 - cy) ** 2)
        
        closest_point = (x1, y1) if dist1 < dist2 else (x2, y2)
        return closest_point

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

    def analyze_selections(self):
        if self.analyzing or not self.selection_boxes:
            return

        self.analyzing = True
        self.analyze_button.setEnabled(False)

        self.progress = QProgressDialog("Analyzing selections...", None, 0, 100, self)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setMinimumDuration(0)
        self.progress.setValue(0)

        results = []

        self.predictor.set_image(self.image_np)

        for i, box in enumerate(self.selection_boxes):
            input_box = np.array([box['x1'], box['y1'], box['x2'], box['y2']])
            input_box = torch.tensor(input_box, device=self.device)

            masks, _, _ = self.predictor.predict(
                box=input_box[None, :].cpu().numpy(),
                multimask_output=False
            )

            if masks is not None and len(masks) > 0:
                self.display_mask(masks[0]) 
                self.process_spatter(masks[0]) 

        self.draw_convergence_area()

        if not hasattr(self, "convergence_area_center") or not hasattr(self, "convergence_area_radius"):
            self.analyzing = False
            self.analyze_button.setEnabled(True)
            return  

        for i, box in enumerate(self.selection_boxes):
            input_box = np.array([box['x1'], box['y1'], box['x2'], box['y2']])
            input_box = torch.tensor(input_box, device=self.device)

            masks, _, _ = self.predictor.predict(
                box=input_box[None, :].cpu().numpy(),
                multimask_output=False
            )

            if masks is not None and len(masks) > 0:
                impact_angle, segment_data = self.process_spatter(masks[0])  
                results.append(segment_data)

        for segment_data in results:
            self.update_json(segment_data)
            json_data = json.dumps(segment_data)
            self.dataUpdated.emit(json_data)

        self.analyzing = False
        self.clear_selections()
        self.progress.close()
        self.analyze_button.setEnabled(True)