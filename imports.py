import sys
from PyQt5.QtWidgets import QApplication, QMainWindow,QLineEdit,QFormLayout, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFileDialog, QLabel, QComboBox, QListWidget, QListWidgetItem, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon,QIntValidator,QDoubleValidator,QFont
import pyvista as pv
from pyvistaqt import QtInteractor
from PIL import Image
from PyQt5.QtCore import Qt, pyqtSignal, QSize
import json
import numpy as np
from SegmentAndMap import SegmentAndMap 
import math
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from datetime import datetime
import subprocess
import os
import numpy as np
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QPushButton, QLabel, QCheckBox
from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QImage
from segment_anything import sam_model_registry, SamPredictor
import torch
import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon