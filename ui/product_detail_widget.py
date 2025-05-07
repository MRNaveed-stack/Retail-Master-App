from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFormLayout, QLineEdit, QComboBox,
                            QDoubleSpinBox, QGroupBox, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import base64
import os

import database
from ui.image_selector import ImageSelector

class ProductDetailWidget(QWidget):
    """
    Widget for displaying product details and handling image management.
    """
    # Signal emitted when a product image is updated
    on_image_updated = pyqtSignal()
    
    def __init__(self, for_customer=False):
        super().__init__()
        
        # Store mode
        self.for_customer = for_customer
        self.current_product = None
        
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Create widget contents
        if for_customer:
            self.create_customer_view()
        else:
            self.create_admin_view()
    
    def create_customer_view(self):
        """Create a read-only view for customers"""
        # Product details group
        product_group = QGroupBox("Product Details")
        product_layout = QVBoxLayout(product_group)
        
        # Product image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(200)
        self.image_label.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd;")
        product_layout.addWidget(self.image_label)
        
        # Product info
        info_form = QFormLayout()
        
        # Product name
        self.product_name_label = QLabel()
        self.product_name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        info_form.addRow("Product:", self.product_name_label)
        
        # Category
        self.category_label = QLabel()
        info_form.addRow("Category:", self.category_label)
        
        # Price
        self.price_label = QLabel()
        self.price_label.setStyleSheet("color: green; font-weight: bold;")
        info_form.addRow("Price:", self.price_label)
        
        # Availability
        self.availability_label = QLabel()
        info_form.addRow("Availability:", self.availability_label)
        
        product_layout.addLayout(info_form)
        self.layout.addWidget(product_group)
    
    def create_admin_view(self):
        """Create an editable view for admin"""
        # Product details group
        product_group = QGroupBox("Product Details")
        product_layout = QVBoxLayout(product_group)
        
        # Create image selector widget
        self.image_selector = ImageSelector()
        self.image_selector.image_selected.connect(self.on_image_selected)
        product_layout.addWidget(self.image_selector)
        
        # Product info form
        info_form = QFormLayout()
        
        # Key number (read-only)
        self.key_number_input = QLineEdit()
        self.key_number_input.setReadOnly(True)
        info_form.addRow("Key Number:", self.key_number_input)
        
        # Product name (editable)
        self.name_input = QLineEdit()
        info_form.addRow("Product Name:", self.name_input)
        
        # Category selection (editable)
        self.category_combo = QComboBox()
        info_form.addRow("Category:", self.category_combo)
        
        # Purchase price (editable)
        self.purchase_price_input = QDoubleSpinBox()
        self.purchase_price_input.setPrefix("$ ")
        self.purchase_price_input.setRange(0.01, 9999.99)
        self.purchase_price_input.setDecimals(2)
        info_form.addRow("Purchase Price:", self.purchase_price_input)
        
        # Sale price (editable)
        self.sale_price_input = QDoubleSpinBox()
        self.sale_price_input.setPrefix("$ ")
        self.sale_price_input.setRange(0.01, 9999.99)
        self.sale_price_input.setDecimals(2)
        info_form.addRow("Sale Price:", self.sale_price_input)
        
        # Profit margin (calculated)
        self.profit_margin_label = QLabel()
        self.profit_margin_label.setStyleSheet("color: green;")
        info_form.addRow("Profit Margin:", self.profit_margin_label)
        
        # Connect signals for auto-calculation
        self.purchase_price_input.valueChanged.connect(self.update_profit_margin)
        self.sale_price_input.valueChanged.connect(self.update_profit_margin)
        
        # Inventory
        self.inventory_label = QLabel()
        info_form.addRow("Inventory:", self.inventory_label)
        
        product_layout.addLayout(info_form)
        
        # Button to save changes
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setIcon(self.style().standardIcon(self.style().SP_DialogSaveButton))
        self.save_btn.clicked.connect(self.save_changes)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        
        product_layout.addLayout(button_layout)
        
        self.layout.addWidget(product_group)
        
        # Refresh categories in dropdown
        self.refresh_categories()
    
    def refresh_categories(self):
        """Refresh the category dropdown"""
        if self.for_customer or not hasattr(self, 'category_combo'):
            return
            
        self.category_combo.clear()
        
        categories = database.get_all_categories()
        for category in categories:
            self.category_combo.addItem(category["name"], category["id"])
    
    def set_product(self, product):
        """
        Set the product to display
        
        Args:
            product (dict): Product information from database
        """
        self.current_product = product
        
        if self.for_customer:
            # Update customer view
            self.product_name_label.setText(product["name"])
            self.category_label.setText(product["category_name"])
            self.price_label.setText(f"${product['sale_price']:.2f}")
            
            # Set availability text and style
            remaining = product["remaining"]
            if remaining <= 0:
                self.availability_label.setText("Out of Stock")
                self.availability_label.setStyleSheet("color: red; font-weight: bold;")
            elif remaining <= 5:
                self.availability_label.setText(f"Low Stock ({remaining} left)")
                self.availability_label.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.availability_label.setText(f"In Stock ({remaining} available)")
                self.availability_label.setStyleSheet("color: green;")
            
            # Display image if available
            self.display_product_image(product)
        else:
            # Update admin view
            self.key_number_input.setText(str(product["key_number"]))
            self.name_input.setText(product["name"])
            
            # Set category
            index = self.category_combo.findData(product["category_id"])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            
            # Set prices
            self.purchase_price_input.setValue(product["purchase_price"])
            self.sale_price_input.setValue(product["sale_price"])
            
            # Update profit margin
            self.update_profit_margin()
            
            # Update inventory info
            total = product["total_added"]
            sold = product["sold"]
            remaining = product["remaining"]
            self.inventory_label.setText(f"Total: {total}, Sold: {sold}, Remaining: {remaining}")
            
            # Display image if available
            self.image_selector.set_image_data(product.get("image_data"), product.get("image_path"))
    
    def clear(self):
        """Clear the product display"""
        self.current_product = None
        
        if self.for_customer:
            # Clear customer view
            self.product_name_label.setText("")
            self.category_label.setText("")
            self.price_label.setText("")
            self.availability_label.setText("")
            self.image_label.clear()
            self.image_label.setText("No product selected")
        else:
            # Clear admin view
            self.key_number_input.clear()
            self.name_input.clear()
            self.purchase_price_input.setValue(0)
            self.sale_price_input.setValue(0)
            self.profit_margin_label.setText("")
            self.inventory_label.setText("")
            self.image_selector.clear()
    
    def display_product_image(self, product):
        """Display the product image in customer view"""
        if not self.for_customer or not hasattr(self, 'image_label'):
            return
        
        # Try to load image from image_data first
        image_data = product.get("image_data")
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
        
        # If no image_data or loading failed, try image_path
        image_path = product.get("image_path")
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
        self.image_label.clear()
        self.image_label.setText("No image available")
    
    def update_profit_margin(self):
        """Calculate and display profit margin"""
        if self.for_customer or not hasattr(self, 'profit_margin_label'):
            return
            
        purchase_price = self.purchase_price_input.value()
        sale_price = self.sale_price_input.value()
        
        if purchase_price > 0:
            profit = sale_price - purchase_price
            margin_percent = (profit / purchase_price) * 100
            
            self.profit_margin_label.setText(f"${profit:.2f} ({margin_percent:.1f}%)")
            
            # Color code based on margin
            if margin_percent < 10:
                self.profit_margin_label.setStyleSheet("color: red;")
            elif margin_percent < 20:
                self.profit_margin_label.setStyleSheet("color: orange;")
            else:
                self.profit_margin_label.setStyleSheet("color: green;")
        else:
            self.profit_margin_label.setText("N/A")
            self.profit_margin_label.setStyleSheet("")
    
    def on_image_selected(self, image_path, image_data):
        """Handle image selection from ImageSelector"""
        if not self.current_product:
            return
            
        # Update image in database
        key_number = self.current_product["key_number"]
        success = database.update_product_image(key_number, image_path, image_data)
        
        if success:
            # Emit signal that image was updated
            self.on_image_updated.emit()
            QMessageBox.information(self, "Success", "Product image updated successfully")
        else:
            QMessageBox.warning(self, "Error", "Failed to update product image")
    
    def save_changes(self):
        """Save changes to the product"""
        if self.for_customer or not self.current_product:
            return
            
        key_number = int(self.key_number_input.text())
        name = self.name_input.text().strip()
        category_id = self.category_combo.currentData()
        purchase_price = self.purchase_price_input.value()
        sale_price = self.sale_price_input.value()
        
        # Validate
        if not name:
            QMessageBox.warning(self, "Missing Information", "Product name cannot be empty")
            return
        
        if sale_price < purchase_price:
            reply = QMessageBox.question(
                self,
                "Low Sale Price",
                "Sale price is lower than purchase price, which will result in a loss. Continue anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Update product
        success = database.update_product(
            key_number,
            name=name,
            purchase_price=purchase_price,
            sale_price=sale_price,
            category_id=category_id
        )
        
        if success:
            QMessageBox.information(self, "Success", "Product updated successfully")
            
            # Refresh product details
            product = database.get_product_by_key(key_number)
            if product:
                self.set_product(product)
                
                # Emit signal to refresh inventory
                self.on_image_updated.emit()
        else:
            QMessageBox.warning(self, "Error", "Failed to update product")
