import numpy as np
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGraphicsView, 
                           QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, 
                           QPushButton, QLabel, QCheckBox, QProgressDialog)
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QImage, QCursor
from segment_anything import sam_model_registry, SamPredictor
import os
import math
import json
import torch
import sys

class SegmentAndMap(QDialog):
    dataUpdated = pyqtSignal(str)  

    def __init__(self, image_path, jsonPath, parent=None):
        super().__init__(parent)
        self.json_file = jsonPath
        self.setWindowTitle("Image Interaction")
        self.image_path = image_path
        self.model_path = os.path.abspath(self.get_resource_path('models/sam_vit_b_01ec64.pth'))
        
        # Initialize device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Load model and move to appropriate device
        self.sam_model = sam_model_registry['vit_b'](checkpoint=self.model_path)
        self.sam_model.to(device=self.device)
        self.predictor = SamPredictor(self.sam_model)
        
        self.image_label = QLabel(self)
        self.segmented_masks = []
        self.selection_boxes = []  # Store selection boxes
        self.selection_rects = []  # Store QGraphicsRectItems
        self.mask_item = None
        self.is_ai_select = False
        self.convergence_lines = []
        self.selection_rect = None
        self.analyzing = False  # Flag to prevent multiple simultaneous analyses
        self.scale_factor = 1.0
        self.space_pressed = False
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        print(f"Running on: {self.device}")
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Create analyze button
        self.analyze_button = QPushButton("Analyze Selections", self)
        self.analyze_button.clicked.connect(self.analyze_selections)
        self.analyze_button.setEnabled(False)  # Disabled until selections are made
        button_layout.addWidget(self.analyze_button)

        # Create clear button
        self.clear_button = QPushButton("Clear All", self)
        self.clear_button.clicked.connect(self.clear_selections)
        button_layout.addWidget(self.clear_button)

        self.layout.addLayout(button_layout)

        # Set up graphics view
        self.graphics_view = QGraphicsView(self)
        self.layout.addWidget(self.graphics_view)

        self.scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)

        # Load and display image
        self.pixmap = QPixmap(self.image_path)
        self.image_item = QGraphicsPixmapItem(self.pixmap)
        self.image_item.setZValue(0)
        self.scene.addItem(self.image_item)

        # Convert image for processing
        img = self.pixmap.toImage()
        ptr = img.bits()
        ptr.setsize(img.byteCount())
        img_array = np.array(ptr).reshape((img.height(), img.width(), 4))
        self.image_np = img_array[:, :, :3]

        self.start_point = None
        self.end_point = None

        # Enable mouse tracking for the graphics view
        self.graphics_view.setMouseTracking(True)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.graphics_view.setDragMode(QGraphicsView.NoDrag)
        
        # Set up mouse events
        self.graphics_view.mousePressEvent = self.mouse_press_event
        self.graphics_view.mouseReleaseEvent = self.mouse_release_event
        self.graphics_view.mouseMoveEvent = self.mouse_move_event
        self.graphics_view.wheelEvent = self.wheel_event
        
        # Set up keyboard events
        self.graphics_view.keyPressEvent = self.key_press_event
        self.graphics_view.keyReleaseEvent = self.key_release_event
        
        # Make graphics view focusable
        self.graphics_view.setFocusPolicy(Qt.StrongFocus)
        
        # Load stylesheet
        self.setStyleSheet(self.load_stylesheet(self.get_resource_path("style/style.css")))

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
            # Zoom
            factor = 1.2 if event.angleDelta().y() > 0 else 1/1.2
            self.scale_factor *= factor
            self.graphics_view.scale(factor, factor)
        else:
            # Normal scroll
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
            
            # Store the selection box coordinates
            selection_box = {
                'x1': int(rect.left()),
                'y1': int(rect.top()),
                'x2': int(rect.right()),
                'y2': int(rect.bottom())
            }
            self.selection_boxes.append(selection_box)
            self.selection_rects.append(self.selection_rect)
            
            # Enable analyze button when there are selections
            self.analyze_button.setEnabled(True)
            
            # Reset for next selection
            self.selection_rect = None
            self.start_point = None
            self.end_point = None

    def analyze_selections(self):
        if self.analyzing or not self.selection_boxes:
            return
            
        try:
            self.analyzing = True
            self.analyze_button.setEnabled(False)
            
            # Create progress dialog
            progress = QProgressDialog("Analyzing selections...", None, 0, len(self.selection_boxes), self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            
            # Set image for predictor once
            self.predictor.set_image(self.image_np)
            
            # Process each selection box
            for i, box in enumerate(self.selection_boxes):
                input_box = np.array([box['x1'], box['y1'], box['x2'], box['y2']])
                input_box = torch.tensor(input_box, device=self.device)
                
                try:
                    masks, _, _ = self.predictor.predict(
                        box=input_box[None, :].cpu().numpy(),
                        multimask_output=False
                    )

                    if masks is not None and len(masks) > 0:
                        mask_item = self.display_mask(masks[0])
                        if mask_item:
                            self.segmented_masks.append(mask_item)
                            impact_angle, segment_data = self.process_spatter(masks[0])
                            self.update_json(segment_data)
                            json_data = json.dumps(segment_data)
                            self.dataUpdated.emit(json_data)
                
                except Exception as e:
                    print(f"Error processing selection: {str(e)}")
                    continue
                
                progress.setValue(i + 1)
                
        except Exception as e:
            print(f"Analysis error: {str(e)}")
        
        finally:
            self.analyzing = False
            self.clear_selections()
            progress.close()

    def clear_selections(self):
        # Remove all selection rectangles from scene
        for rect in self.selection_rects:
            self.scene.removeItem(rect)
        
        # Clear all stored selections
        self.selection_boxes.clear()
        self.selection_rects.clear()
        
        # Disable analyze button
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

        print(f"Impact Angle: {impact_angle}")

        num_spatters = len(self.segmented_masks)

        origin_plane = self.parent().texture_select.currentText().lower()

        segment_data = {
            "center": [center_x, center_y], 
            "angle": float(impact_angle),  
            "line_endpoints": {
                "positive_direction": [int(line_endpoints[0][0]), int(line_endpoints[0][1])],
                "negative_direction": [int(line_endpoints[1][0]), int(line_endpoints[1][1])]
            },
            "spatter_count": num_spatters,
            "origin": origin_plane
        }
        return impact_angle, segment_data

    def calculate_angle(self, mask):
        y, x = np.where(mask > 0)
        center_x = np.mean(x)
        center_y = np.mean(y)

        max_dist = 0
        max_angle = 0
        for i in range(len(x)):
            dx = x[i] - center_x
            dy = y[i] - center_y
            dist = np.sqrt(dx**2 + dy**2)
            if dist > max_dist:
                max_dist = dist
                max_angle = math.atan2(dy, dx) * 180 / math.pi

        return max_angle

    def calculate_impact_angle(self, angle):
        return 90 - angle

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

        line_item_pos = self.scene.addLine(center_x, center_y, end_x_pos, end_y_pos, QPen(Qt.green, 2))
        line_item_pos.setZValue(2)
        self.scene.addItem(line_item_pos)

        line_item_neg = self.scene.addLine(center_x, center_y, end_x_neg, end_y_neg, QPen(Qt.green, 2))
        line_item_neg.setZValue(2)
        self.scene.addItem(line_item_neg)

        self.convergence_lines.append((line_item_pos, line_item_neg))

        return (end_x_pos, end_y_pos), (end_x_neg, end_y_neg)

    def update_json(self, segment_data):
        if os.path.exists(self.json_file):
            with open(self.json_file, "r") as file:
                data = json.load(file)
        else:
            data = []

        segment_data["segment_number"] = len(data) + 1
        data.append(segment_data)

        with open(self.json_file, "w") as file:
            json.dump(data, file, indent=4)