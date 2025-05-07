from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QGridLayout, QScrollArea, QSplitter,
                            QGroupBox, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal

from ui.generate_bill_widget import GenerateBillWidget
from ui.product_detail_widget import ProductDetailWidget
import database

class CategoryButton(QPushButton):
    """Custom button for category selection"""
    def __init__(self, category_id, category_name):
        super().__init__(category_name)
        self.category_id = category_id
        self.setMinimumHeight(40)
        self.setCheckable(True)

class CustomerPanel(QWidget):
    """
    Customer panel for viewing products and generating bills.
    """
    def __init__(self, on_sale_callback=None):
        super().__init__()
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        # Store callback function
        self.on_sale_callback = on_sale_callback
        
        # Create a splitter for the two main sections
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        
        # Create left panel (categories and products)
        self.create_product_panel()
        
        # Create right panel (billing)
        self.create_billing_panel()
        
        # Add panels to splitter
        self.splitter.addWidget(self.product_panel)
        self.splitter.addWidget(self.billing_panel)
        
        # Set initial sizes (40% left, 60% right)
        self.splitter.setSizes([400, 600])
        
        # Add splitter to layout
        self.layout.addWidget(self.splitter)
        
        # Initialize with default category
        self.current_category_id = 1
        self.refresh_data()
    
    def create_product_panel(self):
        """Create the product browsing panel"""
        self.product_panel = QWidget()
        product_layout = QVBoxLayout(self.product_panel)
        
        # Category selection section
        category_group = QGroupBox("Product Categories")
        category_layout = QVBoxLayout(category_group)
        
        # Category dropdown
        self.category_combo = QComboBox()
        self.category_combo.currentIndexChanged.connect(self.on_category_selected)
        category_layout.addWidget(self.category_combo)
        
        # Category buttons scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.category_button_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        category_layout.addWidget(scroll_area)
        
        # Add to layout
        product_layout.addWidget(category_group)
        
        # Product details section
        self.product_detail_widget = ProductDetailWidget(for_customer=True)
        product_layout.addWidget(self.product_detail_widget, 1)
    
    def create_billing_panel(self):
        """Create the billing panel"""
        self.billing_panel = QWidget()
        billing_layout = QVBoxLayout(self.billing_panel)
        
        # Billing title
        billing_title = QLabel("Generate Customer Bill")
        billing_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2a5885;")
        billing_title.setAlignment(Qt.AlignCenter)
        billing_layout.addWidget(billing_title)
        
        # Bill generation widget
        self.bill_widget = GenerateBillWidget(self.on_sale_completed)
        billing_layout.addWidget(self.bill_widget)
    
    def refresh_data(self):
        """Refresh all data in the customer panel"""
        self.refresh_categories()
        self.product_detail_widget.clear()
        self.bill_widget.refresh_product_list()
    
    def refresh_categories(self):
        """Refresh the category list"""
        # Remember current selection
        current_id = self.current_category_id
        
        # Get all categories
        categories = database.get_all_categories()
        
        # Clear existing buttons
        for i in reversed(range(self.category_button_layout.count())): 
            widget = self.category_button_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Clear combobox
        self.category_combo.clear()
        
        # Add categories to dropdown and buttons
        selected_index = 0
        for i, category in enumerate(categories):
            # Add to dropdown
            self.category_combo.addItem(category["name"], category["id"])
            
            # Create button
            btn = CategoryButton(category["id"], category["name"])
            btn.clicked.connect(self.on_category_button_clicked)
            self.category_button_layout.addWidget(btn)
            
            # Check if this is the current category
            if category["id"] == current_id:
                selected_index = i
                btn.setChecked(True)
        
        # Set the current index in the dropdown
        if categories:
            self.category_combo.setCurrentIndex(selected_index)
        
        # Add stretch to push buttons to the top
        self.category_button_layout.addStretch()
        
        # Load products for the current category
        self.load_category_products(current_id)
    
    def load_category_products(self, category_id):
        """Load products for the selected category"""
        products = database.get_products_by_category(category_id)
        if products:
            # Show the first product detail
            self.product_detail_widget.set_product(products[0])
        else:
            self.product_detail_widget.clear()
    
    def on_category_selected(self, index):
        """Handle category selection from dropdown"""
        if index >= 0:
            category_id = self.category_combo.itemData(index)
            self.current_category_id = category_id
            
            # Update button selection
            for i in range(self.category_button_layout.count()):
                widget = self.category_button_layout.itemAt(i).widget()
                if isinstance(widget, CategoryButton):
                    widget.setChecked(widget.category_id == category_id)
            
            # Load products for this category
            self.load_category_products(category_id)
    
    def on_category_button_clicked(self):
        """Handle category button click"""
        button = self.sender()
        if isinstance(button, CategoryButton):
            category_id = button.category_id
            self.current_category_id = category_id
            
            # Update dropdown selection
            index = self.category_combo.findData(category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            
            # Update other buttons
            for i in range(self.category_button_layout.count()):
                widget = self.category_button_layout.itemAt(i).widget()
                if isinstance(widget, CategoryButton) and widget != button:
                    widget.setChecked(False)
            
            # Load products for this category
            self.load_category_products(category_id)
    
    def on_sale_completed(self):
        """Handle completed sale event"""
        # Refresh the product data and notify parent window
        self.refresh_data()
        if self.on_sale_callback:
            self.on_sale_callback()
