import vtk
from PyQt5.QtWidgets import (QFrame, QGridLayout, QApplication, QMainWindow, QLineEdit, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFileDialog, 
                             QLabel, QComboBox, QListWidget, QListWidgetItem, QMessageBox, 
                             QMenu, QInputDialog, QMessageBox,QTabWidget, QDialog, 
                             QGraphicsDropShadowEffect,QGraphicsView,QGraphicsScene,
                             QGraphicsPixmapItem,QGraphicsRectItem,QCheckBox,QProgressDialog,
                             QGraphicsEllipseItem, QStackedWidget,QGraphicsOpacityEffect
                             )
from PyQt5.QtCore import (QSize, Qt, QPoint, pyqtSignal, Qt, QRectF, QLineF, QPointF,QEvent) 
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from PyQt5.QtGui import (QPixmap, QIcon, QImage, QColor,QPainter,QPen,QBrush,QCursor)
from segment_anything import sam_model_registry, SamPredictor
from sklearn.cluster import DBSCAN
from pyvistaqt import QtInteractor
from datetime import datetime
from docx import Document
from PIL import Image
import pyvista as pv
import numpy as np
import subprocess
import shutil
import torch
import json
import math
import sys
import os