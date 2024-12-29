import numpy as np
import torch
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QPushButton, QLabel, QCheckBox
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QImage
from segment_anything import sam_model_registry, SamPredictor
import os
import math


class ImageInteractionDialog(QDialog):
    def __init__(self, image_path, device='cuda:0', parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Interaction")
        self.image_path = image_path
        self.model_path = os.path.abspath(r'C:\Users\flore\Downloads\sam_vit_b_01ec64.pth')
        self.sam_model = sam_model_registry['vit_b'](checkpoint=self.model_path)
        self.predictor = SamPredictor(self.sam_model)
        self.device = device
        self.image_label = QLabel(self)
        self.segmented_masks = []  # Track all masks for undo functionality
        self.selection_history = []  # Track all selection rectangles for undo
        self.mask_item = None  # Initialize mask_item to None
        self.is_ai_select = False  # Track whether AI select is enabled
        self.convergence_lines = []  # Track the drawn convergence lines
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

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
        self.image_item.setZValue(0)  # Ensure it is below any masks
        self.scene.addItem(self.image_item)

        self.image_height, self.image_width = self.pixmap.height(), self.pixmap.width()

        img = self.pixmap.toImage()  # Convert QPixmap to QImage
        ptr = img.bits()
        ptr.setsize(img.byteCount())
        img_array = np.array(ptr).reshape((img.height(), img.width(), 4))  # RGBA image
        self.image_np = img_array[:, :, :3]  # Convert to RGB if necessary

        self.start_point = None
        self.end_point = None
        self.selection_rect = None

        self.layout.addLayout(sidebar_layout)

        self.graphics_view.mousePressEvent = self.mouse_press_event
        self.graphics_view.mouseReleaseEvent = self.mouse_release_event
        self.graphics_view.mouseMoveEvent = self.mouse_move_event

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
                mask_item = self.display_mask(masks[0])  # Capture the mask_item returned by display_mask
                self.segmented_masks.append(mask_item)  # Save the mask item for undo

                self.process_spatter(masks[0])

            self.selection_history.append(self.selection_rect)
            self.start_point = None
            self.end_point = None

    def display_mask(self, mask):
        if mask is None or mask.sum() == 0:
            return 

        mask_color = np.zeros((*mask.shape, 4), dtype=np.uint8)  # RGBA image
        mask_color[mask > 0] = [255, 0, 0, 100]  # Red with transparency

        height, width = mask.shape
        qimage = QImage(mask_color.data, width, height, QImage.Format_RGBA8888)
        mask_pixmap = QPixmap.fromImage(qimage)
        mask_item = QGraphicsPixmapItem(mask_pixmap)
        mask_item.setZValue(1)  # Ensure it is above the original image
        self.scene.addItem(mask_item)

        return mask_item

    def process_spatter(self, mask):
        # Find the center of the mask (spatter center)
        y, x = np.where(mask > 0)
        center_x = int(np.mean(x))
        center_y = int(np.mean(y))

        angle = self.calculate_angle(mask)

        self.draw_convergence_line(center_x, center_y, angle)

        impact_angle = self.calculate_impact_angle(angle)
        print(f"Impact Angle: {impact_angle}")


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
                max_angle = math.atan2(dy, dx) * 180 / math.pi  # Angle relative to center of mass

        return max_angle  # This angle represents the direction the spatter is facing
    

    def calculate_impact_angle(self, angle):
        # Assuming the angle between the spatter and the ground is the impact angle
        return 90 - angle  # This can be adjusted based on physical assumptions

    def draw_convergence_line(self, center_x, center_y, angle):
        step_size = 5  # Adjust this value as needed for smoother drawing

        def draw_line_in_direction(start_x, start_y, angle):
            current_x, current_y = start_x, start_y
            
            while True:
                next_x = current_x + step_size * math.cos(math.radians(angle))
                next_y = current_y + step_size * math.sin(math.radians(angle))
                
                if next_x < 0 or next_x > self.pixmap.width() or next_y < 0 or next_y > self.pixmap.height():
                    break  # Exit the loop if the next point is outside the image
                
                current_x, current_y = next_x, next_y
            
            return current_x, current_y

        end_x_pos, end_y_pos = draw_line_in_direction(center_x, center_y, angle)
        
        end_x_neg, end_y_neg = draw_line_in_direction(center_x, center_y, angle + 180)  # Reverse the angle by 180 degrees

        line_item_pos = self.scene.addLine(center_x, center_y, end_x_pos, end_y_pos, QPen(Qt.green, 2))
        line_item_pos.setZValue(2)  # Ensure it is above the mask
        self.scene.addItem(line_item_pos)
        
        line_item_neg = self.scene.addLine(center_x, center_y, end_x_neg, end_y_neg, QPen(Qt.green, 2))
        line_item_neg.setZValue(2)  # Ensure it is above the mask
        self.scene.addItem(line_item_neg)

        self.convergence_lines.append((line_item_pos, line_item_neg))

    def undo_selection(self):
        if self.segmented_masks:
            last_mask = self.segmented_masks.pop()
            self.scene.removeItem(last_mask)

        if self.convergence_lines:
            last_lines = self.convergence_lines.pop()
            self.scene.removeItem(last_lines[0])  # Remove the positive direction line
            self.scene.removeItem(last_lines[1])  # Remove the negative direction line

        if self.selection_history:
            last_selection = self.selection_history.pop()
            self.scene.removeItem(last_selection)
            if self.selection_history:
                self.scene.addItem(self.selection_history[-1])

    def get_selected_rect(self):
        return self.selection_rect
