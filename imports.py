from PyQt5.QtWidgets import QApplication, QMainWindow,QLineEdit,QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFileDialog, QLabel, QComboBox, QListWidget, QListWidgetItem, QVBoxLayout, QMessageBox,QWidget, QHBoxLayout, QPushButton, QLabel,QPushButton, QMenu,QFileDialog, QInputDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QSize, Qt, QPoint,pyqtSignal
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from PyQt5.QtGui import QPixmap, QIcon, QImage
from SegmentAndMap import SegmentAndMap 
from pyvistaqt import QtInteractor
from datetime import datetime
from docx import Document
from PIL import Image
import pyvista as pv
import numpy as np
import subprocess
import json
import math
import sys
import os