from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import base64
import os

class ImageSelector(QWidget):
    """
    Widget for selecting and displaying product images.
    """
    # Signal emitted when an image is selected
    image_selected = pyqtSignal(str, str)  # image_path, image_data
    
    def __init__(self):
        super().__init__()
        
        # Store image data
        self.image_path = None
        self.image_data = None
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create image display area
        self.image_label = QLabel("No image selected")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(200)
        self.image_label.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd;")
        self.layout.addWidget(self.image_label)
        
        # Create buttons
        buttons_layout = QHBoxLayout()
        
        # Select image button
        self.select_btn = QPushButton("Select Image")
        self.select_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogStart))
        self.select_btn.clicked.connect(self.select_image)
        buttons_layout.addWidget(self.select_btn)
        
        # Clear image button
        self.clear_btn = QPushButton("Clear Image")
        self.clear_btn.setIcon(self.style().standardIcon(self.style().SP_DialogCancelButton))
        self.clear_btn.clicked.connect(self.clear_image)
        buttons_layout.addWidget(self.clear_btn)
        
        self.layout.addLayout(buttons_layout)
    
    def select_image(self):
        """Open file dialog to select an image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Product Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            try:
                # Load the image
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    # Resize pixmap to fit label while maintaining aspect ratio
                    pixmap = pixmap.scaled(
                        self.image_label.width(), 
                        200, 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(pixmap)
                    
                    # Store image path
                    self.image_path = file_path
                    
                    # Store image data as base64
                    with open(file_path, "rb") as image_file:
                        binary_data = image_file.read()
                        self.image_data = base64.b64encode(binary_data).decode('utf-8')
                    
                    # Emit signal
                    self.image_selected.emit(self.image_path, self.image_data)
                else:
                    QMessageBox.warning(self, "Error", "Could not load the selected image")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error loading image: {e}")
    
    def clear_image(self):
        """Clear the selected image"""
        self.image_label.clear()
        self.image_label.setText("No image selected")
        
        # Clear stored image data
        old_path = self.image_path
        old_data = self.image_data
        
        self.image_path = None
        self.image_data = None
        
        # Emit signal if previously had an image
        if old_path or old_data:
            self.image_selected.emit("", "")
    
    def set_image_data(self, image_data, image_path=None):
        """
        Set the image from existing data
        
        Args:
            image_data (str): Base64 encoded image data
            image_path (str): Path to the image file
        """
        self.image_data = image_data
        self.image_path = image_path
        
        if image_data:
            try:
                # Decode from base64 to binary
                binary_data = base64.b64decode(image_data)
                image = QImage()
                image.loadFromData(binary_data)
                pixmap = QPixmap.fromImage(image)
                
                if not pixmap.isNull():
                    # Resize pixmap to fit label while maintaining aspect ratio
                    pixmap = pixmap.scaled(
                        self.image_label.width(), 
                        200, 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(pixmap)
                    return
            except Exception as e:
                print(f"Error loading image from data: {e}")
        
        # Try loading from path if data loading failed
        if image_path and os.path.exists(image_path):
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(
                        self.image_label.width(), 
                        200, 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(pixmap)
                    return
            except Exception as e:
                print(f"Error loading image from path: {e}")
        
        # If no image or loading failed
        self.clear()
    
    def clear(self):
        """Clear all image data"""
        self.image_label.clear()
        self.image_label.setText("No image selected")
        self.image_path = None
        self.image_data = None
