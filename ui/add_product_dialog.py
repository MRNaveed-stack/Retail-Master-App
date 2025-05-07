from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QFormLayout,
                            QSpinBox, QDoubleSpinBox, QComboBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator

import database
from ui.image_selector import ImageSelector

class AddProductDialog(QDialog):
    """
    Dialog for adding a new product to the inventory.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Add New Product")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create form sections
        self.create_product_info_section()
        self.create_pricing_section()
        self.create_category_section()
        self.create_image_section()
        
        # Create buttons layout
        self.create_buttons()
        
        # Initialize categories
        self.refresh_categories()
        
        # Store product name for access after dialog is closed
        self.product_name = ""
    
    def create_product_info_section(self):
        """Create the basic product information section"""
        group = QGroupBox("Product Information")
        form_layout = QFormLayout(group)
        
        # Key Number input
        self.key_number_input = QLineEdit()
        self.key_number_input.setValidator(QIntValidator(1, 999999))
        self.key_number_input.setPlaceholderText("Enter unique product key (e.g., 7777)")
        form_layout.addRow("Key Number:", self.key_number_input)
        
        # Name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name (e.g., Luxury Firm)")
        form_layout.addRow("Product Name:", self.name_input)
        
        self.layout.addWidget(group)
    
    def create_pricing_section(self):
        """Create the pricing and quantity section"""
        group = QGroupBox("Pricing and Inventory")
        form_layout = QFormLayout(group)
        
        # Purchase Price input
        self.purchase_price_input = QDoubleSpinBox()
        self.purchase_price_input.setPrefix("$ ")
        self.purchase_price_input.setRange(0.01, 9999999.99)
        self.purchase_price_input.setDecimals(2)
        self.purchase_price_input.setSingleStep(1.00)
        self.purchase_price_input.valueChanged.connect(self.update_profit_margin)
        form_layout.addRow("Purchase Price:", self.purchase_price_input)
        
        # Sale Price input
        self.sale_price_input = QDoubleSpinBox()
        self.sale_price_input.setPrefix("$ ")
        self.sale_price_input.setRange(0.01, 9999999.99)
        self.sale_price_input.setDecimals(2)
        self.sale_price_input.setSingleStep(1.00)
        self.sale_price_input.valueChanged.connect(self.update_profit_margin)
        form_layout.addRow("Sale Price:", self.sale_price_input)
        
        # Profit margin (calculated)
        self.profit_margin_label = QLabel("0%")
        self.profit_margin_label.setStyleSheet("color: green; font-weight: bold;")
        form_layout.addRow("Profit Margin:", self.profit_margin_label)
        
        # Total Quantity input
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 9999)
        self.quantity_input.setSingleStep(1)
        form_layout.addRow("Total Quantity:", self.quantity_input)
        
        self.layout.addWidget(group)
    
    def create_category_section(self):
        """Create the category selection section"""
        group = QGroupBox("Product Category")
        form_layout = QFormLayout(group)
        
        # Category selection
        self.category_combo = QComboBox()
        form_layout.addRow("Category:", self.category_combo)
        
        self.layout.addWidget(group)
    
    def create_image_section(self):
        """Create the image selection section"""
        group = QGroupBox("Product Image")
        image_layout = QVBoxLayout(group)
        
        # Add image selector
        self.image_selector = ImageSelector()
        image_layout.addWidget(self.image_selector)
        
        self.layout.addWidget(group)
    
    def create_buttons(self):
        """Create the action buttons"""
        buttons_layout = QHBoxLayout()
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        # Add button
        self.add_button = QPushButton("Add Product")
        self.add_button.setDefault(True)
        self.add_button.clicked.connect(self.add_product)
        self.add_button.setStyleSheet("background-color: #4CAF50; color: white;")
        
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_button)
        
        self.layout.addLayout(buttons_layout)
    
    def refresh_categories(self):
        """Refresh the categories in the dropdown"""
        # Clear the dropdown
        self.category_combo.clear()
        
        # Get all categories
        categories = database.get_all_categories()
        
        # Add categories to the dropdown
        for category in categories:
            self.category_combo.addItem(category["name"], category["id"])
    
    def update_profit_margin(self):
        """Calculate and display the profit margin"""
        purchase_price = self.purchase_price_input.value()
        sale_price = self.sale_price_input.value()
        
        if purchase_price > 0:
            profit = sale_price - purchase_price
            margin_percent = (profit / purchase_price) * 100
            
            # Update the label with the calculated margin
            self.profit_margin_label.setText(f"${profit:.2f} ({margin_percent:.1f}%)")
            
            # Color code based on margin
            if margin_percent < 10:
                self.profit_margin_label.setStyleSheet("color: red;")
            elif margin_percent < 20:
                self.profit_margin_label.setStyleSheet("color: orange;")
            else:
                self.profit_margin_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.profit_margin_label.setText("N/A")
            self.profit_margin_label.setStyleSheet("")
    
    def add_product(self):
        """Add a new product to the database"""
        # Validate inputs
        if not self._validate_inputs():
            return
        
        # Get values from inputs
        key_number = int(self.key_number_input.text())
        name = self.name_input.text()
        purchase_price = self.purchase_price_input.value()
        sale_price = self.sale_price_input.value()
        total_added = self.quantity_input.value()
        category_id = self.category_combo.currentData()
        
        # Get image data
        image_path = self.image_selector.image_path
        image_data = self.image_selector.image_data
        
        # Try to add the product
        success = database.add_product(
            key_number, 
            name, 
            purchase_price, 
            sale_price, 
            total_added,
            category_id,
            image_path,
            image_data
        )
        
        if success:
            # Store product name for reference
            self.product_name = name
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Duplicate Key Number",
                f"A product with key number {key_number} already exists. Please use a different key number."
            )
    
    def _validate_inputs(self):
        """Validate that all inputs are properly filled"""
        if not self.key_number_input.text():
            QMessageBox.warning(self, "Missing Information", "Please enter a Key Number.")
            return False
        
        if not self.name_input.text():
            QMessageBox.warning(self, "Missing Information", "Please enter a Product Name.")
            return False
        
        if self.purchase_price_input.value() <= 0:
            QMessageBox.warning(self, "Invalid Price", "Please enter a valid Purchase Price.")
            return False
        
        if self.sale_price_input.value() <= 0:
            QMessageBox.warning(self, "Invalid Price", "Please enter a valid Sale Price.")
            return False
        
        if self.quantity_input.value() <= 0:
            QMessageBox.warning(self, "Invalid Quantity", "Please enter a valid Total Quantity.")
            return False
        
        # Validate that sale price is not lower than purchase price
        purchase_price = self.purchase_price_input.value()
        sale_price = self.sale_price_input.value()
        
        if sale_price < purchase_price:
            reply = QMessageBox.question(
                self, 
                "Low Sale Price", 
                "Sale price is lower than purchase price, which will result in a loss. Continue anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return False
        
        return True
