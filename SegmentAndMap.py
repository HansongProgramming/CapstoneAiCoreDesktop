import numpy as np
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QPushButton, QLabel, QCheckBox
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QImage
from segment_anything import sam_model_registry, SamPredictor
import os
import math
import json
import torch
import sys

class SegmentAndMap(QDialog):
    dataUpdated = pyqtSignal(str)  

    def __init__(self, image_path, jsonPath ,parent=None):
        super().__init__(parent)
        self.json_file = jsonPath
        self.setWindowTitle("Image Interaction")
        self.image_path = image_path
        self.model_path = os.path.abspath(self.get_resource_path('models/sam_vit_b_01ec64.pth'))
        self.sam_model = sam_model_registry['vit_b'](checkpoint=self.model_path)
        self.predictor = SamPredictor(self.sam_model)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.image_label = QLabel(self)
        self.segmented_masks = []
        self.selection_history = []
        self.mask_item = None
        self.is_ai_select = False
        self.convergence_lines = []
        self.selection_rect = None
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        print(self.device)
        sidebar_layout = QVBoxLayout()

        self.undo_button = QPushButton("Undo", self)
        self.undo_button.clicked.connect(self.undo_selection)
        sidebar_layout.addWidget(self.undo_button)

        self.ai_select_checkbox = QCheckBox("Ai Select", self)
        self.ai_select_checkbox.toggled.connect(self.toggle_ai_select)
        sidebar_layout.addWidget(self.ai_select_checkbox)

        self.manual_select_checkbox = QCheckBox("Manual Select", self)
        self.manual_select_checkbox.toggled.connect(self.toggle_manual_select)
        sidebar_layout.addWidget(self.manual_select_checkbox)

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

        self.layout.addLayout(sidebar_layout)

        self.graphics_view.mousePressEvent = self.mouse_press_event
        self.graphics_view.mouseReleaseEvent = self.mouse_release_event
        self.graphics_view.mouseMoveEvent = self.mouse_move_event
        self.setStyleSheet(self.load_stylesheet(self.get_resource_path("style/style.css")))

    def get_resource_path(self, relative_path):
        if getattr(sys, 'frozen', False):  # If the script is run from an executable
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

        
    def load_stylesheet(self, file_path):
        with open(file_path, 'r') as f:
            return f.read()

    def toggle_ai_select(self, checked):
        self.is_ai_select = checked

    def toggle_manual_select(self, checked):
        self.is_ai_select = not checked

    def mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = self.graphics_view.mapToScene(event.pos())
            self.selection_rect = QGraphicsRectItem()
            self.selection_rect.setPen(QPen(Qt.red, 2, Qt.DashLine))
            self.selection_rect.setBrush(QBrush(Qt.transparent))
            self.scene.addItem(self.selection_rect)

    def mouse_move_event(self, event):
        if self.start_point:
            self.end_point = self.graphics_view.mapToScene(event.pos())
            rect = QRectF(self.start_point, self.end_point).normalized()
            self.selection_rect.setRect(rect)

    def mouse_release_event(self, event):
        if self.start_point and self.selection_rect:
            self.end_point = self.graphics_view.mapToScene(event.pos())
            x1, y1 = int(self.start_point.x()), int(self.start_point.y())
            x2, y2 = int(self.end_point.x()), int(self.end_point.y())
            input_box = np.array([x1, y1, x2, y2])

            self.predictor.set_image(self.image_np)
            masks, _, _ = self.predictor.predict(
                box=input_box[None, :],
                multimask_output=False
            )

            if masks is not None and len(masks) > 0:
                mask_item = self.display_mask(masks[0])
                self.segmented_masks.append(mask_item)

                impact_angle, segment_data = self.process_spatter(masks[0])
                self.selection_history.append(self.selection_rect)
                self.start_point = None
                self.end_point = None

                # Update Data.json with the new segment data
                self.update_json(segment_data)

                json_data = json.dumps(segment_data)
                self.dataUpdated.emit(json_data)

    def update_json(self, segment_data):
        self.json_file
        if os.path.exists(self.json_file):
            with open(self.json_file, "r") as file:
                data = json.load(file)
        else:
            data = []

        segment_data["segment_number"] = len(data) + 1
        data.append(segment_data)

        with open(self.json_file, "w") as file:
            json.dump(data, file, indent=4)
            
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

        # Count the current number of spatters
        num_spatters = len(self.segmented_masks)

        # Get the origin plane from the parent window's texture_select
        origin_plane = self.parent().texture_select.currentText().lower()

        segment_data = {
            "center": [center_x, center_y], 
            "angle": float(impact_angle),  
            "line_endpoints": {
                "positive_direction": [int(line_endpoints[0][0]), int(line_endpoints[0][1])],
                "negative_direction": [int(line_endpoints[1][0]), int(line_endpoints[1][1])]
            },
            "spatter_count": num_spatters,
            "origin": origin_plane  # Add the origin plane information
        }
        print(center_x, center_y)
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

    def undo_selection(self):
        if self.segmented_masks:
            last_mask = self.segmented_masks.pop()
            self.scene.removeItem(last_mask)

        if self.convergence_lines:
            last_lines = self.convergence_lines.pop()
            self.scene.removeItem(last_lines[0])
            self.scene.removeItem(last_lines[1])

        if self.selection_history:
            last_selection = self.selection_history.pop()
            self.scene.removeItem(last_selection)
            if self.selection_history:
                self.scene.addItem(self.selection_history[-1])

    def get_selected_rect(self):
        if self.selection_rect:
            rect = self.selection_rect.rect()
            x1, y1 = int(rect.left()), int(rect.top())
            x2, y2 = int(rect.right()), int(rect.bottom())
            return x1, y1, x2, y2
        return None
