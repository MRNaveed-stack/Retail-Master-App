from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                            QPushButton, QLabel, QSplitter, QMessageBox)
from PyQt5.QtCore import Qt

from ui.inventory_widget import InventoryWidget
from ui.sales_history_widget import SalesHistoryWidget
from ui.category_management import CategoryManagementWidget
from ui.add_product_dialog import AddProductDialog
import database

class AdminPanel(QWidget):
    """
    Admin panel for product management, inventory, and profit tracking.
    """
    def __init__(self):
        super().__init__()
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create action buttons
        self.create_action_buttons()
        
        # Create tabs for different admin functions
        self.tabs = QTabWidget()
        
        # Create widgets for tabs
        self.inventory_widget = InventoryWidget(is_admin=True)
        self.sales_history_widget = SalesHistoryWidget(is_admin=True) 
        self.category_management_widget = CategoryManagementWidget(
            on_category_changed=self.refresh_data
        )
        
        # Add widgets to tabs
        self.tabs.addTab(self.inventory_widget, "Inventory")
        self.tabs.addTab(self.sales_history_widget, "Sales History")
        self.tabs.addTab(self.category_management_widget, "Categories")
        
        # Add tabs to layout
        self.layout.addWidget(self.tabs)
        
        # Connect signals
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Initialize the first tab
        self.on_tab_changed(0)
    
    def create_action_buttons(self):
        """Create the action buttons for admin operations"""
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(10, 10, 10, 5)
        
        # Add product button
        add_product_btn = QPushButton("Add New Product")
        add_product_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogNewFolder))
        add_product_btn.setMinimumWidth(150)
        add_product_btn.clicked.connect(self.show_add_product_dialog)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.setIcon(self.style().standardIcon(self.style().SP_BrowserReload))
        refresh_btn.clicked.connect(self.refresh_data)
        
        # Add to layout
        button_layout.addWidget(add_product_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addStretch()
        
        self.layout.addLayout(button_layout)
    
    def show_add_product_dialog(self):
        """Show the dialog to add a new product"""
        dialog = AddProductDialog(self)
        result = dialog.exec_()
        
        if result:
            QMessageBox.information(
                self, 
                "Product Added", 
                f"Product '{dialog.product_name}' was added successfully."
            )
            self.refresh_data()
    
    def on_tab_changed(self, index):
        """Handle tab change events to refresh data"""
        if index == 0:  # Inventory tab
            self.inventory_widget.refresh_inventory()
        elif index == 1:  # Sales History tab
            self.sales_history_widget.refresh_sales_history()
        elif index == 2:  # Categories tab
            self.category_management_widget.refresh_categories()
    
    def refresh_data(self):
        """Refresh all data in the admin panel"""
        current_index = self.tabs.currentIndex()
        
        # Refresh the current tab
        if current_index == 0:
            self.inventory_widget.refresh_inventory()
        elif current_index == 1:
            self.sales_history_widget.refresh_sales_history()
        elif current_index == 2:
            self.category_management_widget.refresh_categories()
