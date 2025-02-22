import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, 
                           QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, 
                           QPushButton, QLabel, QCheckBox, QProgressDialog,
                           QGraphicsEllipseItem, QFileDialog,)
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QLineF, QPointF
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QImage, QCursor, QColor
from segment_anything import sam_model_registry, SamPredictor
from sklearn.cluster import DBSCAN
import os
import math
import json
import torch
import sys

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

        try:
            self.analyzing = True
            self.analyze_button.setEnabled(False)
            progress = QProgressDialog("Analyzing selections...", None, 0, len(self.selection_boxes), self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)

            self.predictor.set_image(self.image_np)

            for i, box in enumerate(self.selection_boxes):
                input_box = np.array([box['x1'], box['y1'], box['x2'], box['y2']])
                input_box = torch.tensor(input_box, device=self.device)

                masks, _, _ = self.predictor.predict(box=input_box[None, :].cpu().numpy(), multimask_output=False)

                if masks is not None and len(masks) > 0:
                    mask_item = self.display_mask(masks[0])
                    if mask_item:
                        self.segmented_masks.append(mask_item)
                        impact_angle, segment_data = self.process_spatter(masks[0])
                        self.update_json(segment_data)
                        json_data = json.dumps(segment_data)
                        self.dataUpdated.emit(json_data)

                progress.setValue(i + 1)

            self.draw_convergence_area()

        except Exception as e:
            print(f"Analysis error: {str(e)}")

        finally:
            self.analyzing = False
            self.clear_selections()
            progress.close()

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
        
        angle = self.calculate_angle(mask)
        
        line_endpoints = self.draw_convergence_line(center_x, center_y, angle)

        impact_angle = self.calculate_impact_angle(angle)

        num_spatters = len(self.segmented_masks)

        segment_data = {
            "center": [center_x, center_y], 
            "angle": float(impact_angle),  
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

    def calculate_impact_angle(self, angle):
        return 90 - angle
    
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