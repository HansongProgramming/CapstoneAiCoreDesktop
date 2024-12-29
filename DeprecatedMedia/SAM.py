import numpy as np
import torch
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QPushButton
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush
from segment_anything import sam_model_registry, SamPredictor
import matplotlib.pyplot as plt

class ImageInteractionDialog(QDialog):
    def __init__(self, image_path, sam_model, predictor, device='cuda:0', parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Interaction")
        self.image_path = image_path
        self.sam_model = sam_model
        self.predictor = predictor
        self.device = device
        self.init_ui()

    def init_ui(self):
        """Initialize the UI for image interaction."""
        self.layout = QVBoxLayout(self)

        # Create a QGraphicsView to display the image
        self.graphics_view = QGraphicsView(self)
        self.layout.addWidget(self.graphics_view)

        # Create a QGraphicsScene to manage the image and interactions
        self.scene = QGraphicsScene(self)
        self.graphics_view.setScene(self.scene)

        # Load the image and add it to the scene
        self.pixmap = QPixmap(self.image_path)
        self.image_item = QGraphicsPixmapItem(self.pixmap)
        self.scene.addItem(self.image_item)

        # Load the image as a NumPy array for SAM
        self.image_np = self.pixmap.toImage().convertToFormat(4).bits().asarray()
        self.image_np = np.array(self.image_np, dtype=np.uint8).reshape(self.pixmap.height(), self.pixmap.width(), 4)[:, :, :3]

        # Enable selection of points
        self.start_point = None
        self.end_point = None
        self.selection_rect = None
        self.selection_history = []

        # Connect the mouse event to draw the selection box
        self.graphics_view.mousePressEvent = self.mouse_press_event
        self.graphics_view.mouseReleaseEvent = self.mouse_release_event
        self.graphics_view.mouseMoveEvent = self.mouse_move_event

        # Add Undo button
        self.undo_button = QPushButton("Undo", self)
        self.undo_button.clicked.connect(self.undo_selection)
        self.layout.addWidget(self.undo_button)

    def mouse_press_event(self, event):
        """Handle mouse press event to start drawing a selection."""
        if event.button() == Qt.LeftButton:
            self.start_point = self.graphics_view.mapToScene(event.pos())
            self.selection_rect = QGraphicsRectItem()
            self.selection_rect.setPen(QPen(Qt.red, 2, Qt.DashLine))
            self.selection_rect.setBrush(QBrush(Qt.transparent))
            self.scene.addItem(self.selection_rect)

    def mouse_move_event(self, event):
        """Handle mouse move event to update the selection box."""
        if self.start_point:
            self.end_point = self.graphics_view.mapToScene(event.pos())
            rect = QRectF(self.start_point, self.end_point).normalized()
            self.selection_rect.setRect(rect)

    def mouse_release_event(self, event):
        """Handle the mouse release event to finalize the selection box."""
        if self.start_point and self.selection_rect:
            self.end_point = self.graphics_view.mapToScene(event.pos())
            # Define bounding box for SAM
            x1, y1 = int(self.start_point.x()), int(self.start_point.y())
            x2, y2 = int(self.end_point.x()), int(self.end_point.y())
            input_box = np.array([x1, y1, x2, y2])

            # Run SAM prediction
            self.predictor.set_image(self.image_np)
            masks, _, _ = self.predictor.predict(
                box=input_box[None, :],
                multimask_output=False
            )

            # Overlay mask on the image
            self.display_mask(masks[0])

            # Add the selection to the history
            self.selection_history.append(self.selection_rect)
            self.start_point = None
            self.end_point = None

    def display_mask(self, mask):
        """Overlay the SAM mask on the image."""
        overlay = QPixmap(self.pixmap.size())
        overlay.fill(Qt.transparent)

        painter = QPainter(overlay)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.red, Qt.DiagCrossPattern))
        painter.drawRect(self.selection_rect.rect().toRect())
        painter.end()

        mask_item = QGraphicsPixmapItem(overlay)
        self.scene.addItem(mask_item)

    def undo_selection(self):
        """Undo the last selection."""
        if self.selection_history:
            last_selection = self.selection_history.pop()
            self.scene.removeItem(last_selection)

    def wheelEvent(self, event):
        """Handle zooming in and out with the mouse wheel."""
        zoom_factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.graphics_view.scale(zoom_factor, zoom_factor)

    def closeEvent(self, event):
        """Override close event."""
        event.accept()
