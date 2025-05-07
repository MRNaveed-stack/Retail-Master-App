from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QLabel, QLineEdit, QPushButton,
                            QHeaderView, QMessageBox, QMenu, QComboBox,
                            QGroupBox)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QCursor

import database
from ui.product_detail_widget import ProductDetailWidget

class InventoryWidget(QWidget):
    """
    Widget for displaying and managing inventory.
    """
    def __init__(self, is_admin=False):
        super().__init__()
        
        # Store admin mode
        self.is_admin = is_admin
        
        # Current selected category
        self.current_category_id = None
        
        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create top controls (search and category filter)
        self.create_top_controls()
        
        # Create a horizontal layout for inventory table and product detail
        content_layout = QHBoxLayout()
        
        # Create inventory table
        self.create_inventory_table()
        content_layout.addWidget(self.inventory_table, 3)  # 3/4 of the width
        
        # Create product detail widget if in admin mode
        if self.is_admin:
            self.product_detail = ProductDetailWidget(for_customer=False)
            self.product_detail.on_image_updated.connect(self.refresh_inventory)
            content_layout.addWidget(self.product_detail, 1)  # 1/4 of the width
        
        self.layout.addLayout(content_layout)
        
        # Create action buttons at the bottom
        if self.is_admin:
            self.create_action_buttons()
        
        # Initialize the inventory table
        self.refresh_inventory()
    
    def create_top_controls(self):
        """Create the top controls section with search and category filter"""
        controls_layout = QHBoxLayout()
        
        # Search section
        search_layout = QHBoxLayout()
        
        # Search label
        search_label = QLabel("Search:")
        search_layout.addWidget(search_label)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter key number or product name...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)
        
        # Clear search button
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_button)
        
        controls_layout.addLayout(search_layout, 2)  # 2/3 of the width for search
        
        # Category filter
        category_layout = QHBoxLayout()
        
        # Category label
        category_label = QLabel("Category:")
        category_layout.addWidget(category_label)
        
        # Category dropdown
        self.category_filter = QComboBox()
        self.category_filter.currentIndexChanged.connect(self.on_category_filter_changed)
        category_layout.addWidget(self.category_filter)
        
        controls_layout.addLayout(category_layout, 1)  # 1/3 of the width for category filter
        
        self.layout.addLayout(controls_layout)
    
    def create_inventory_table(self):
        """Create the inventory table"""
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(7)
        self.inventory_table.setHorizontalHeaderLabels([
            "Key Number", "Product Name", "Purchase Price", "Sale Price",
            "Total Added", "Sold", "Remaining"
        ])
        
        # Set table properties
        self.inventory_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.inventory_table.verticalHeader().setVisible(False)
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.inventory_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Connect selection change
        self.inventory_table.itemSelectionChanged.connect(self.on_product_selected)
        
        # Setup context menu for right-click
        self.inventory_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.inventory_table.customContextMenuRequested.connect(self.show_context_menu)
    
    def create_action_buttons(self):
        """Create action buttons at the bottom"""
        action_layout = QHBoxLayout()
        
        # Delete product button
        self.delete_btn = QPushButton("Delete Selected Product")
        self.delete_btn.clicked.connect(self.delete_selected_product)
        self.delete_btn.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
        action_layout.addWidget(self.delete_btn)
        
        action_layout.addStretch()
        
        self.layout.addLayout(action_layout)
    
    def refresh_inventory(self):
        """Refresh the inventory table with current data"""
        # Refresh category filter first
        self.refresh_category_filter()
        
        search_term = self.search_input.text().strip()
        
        # Get products based on search and category filter
        if search_term:
            products = database.search_products(search_term)
            # Further filter by category if one is selected
            if self.current_category_id is not None:
                products = [p for p in products if p["category_id"] == self.current_category_id]
        elif self.current_category_id is not None:
            products = database.get_products_by_category(self.current_category_id)
        else:
            products = database.get_all_products()
        
        # Clear table
        self.inventory_table.setRowCount(0)
        
        # Populate table with products
        for row, product in enumerate(products):
            self.inventory_table.insertRow(row)
            
            # Key Number
            key_item = QTableWidgetItem(str(product["key_number"]))
            # Store the key number as item data for easier retrieval
            key_item.setData(Qt.UserRole, product["key_number"])
            self.inventory_table.setItem(row, 0, key_item)
            
            # Product Name
            name_item = QTableWidgetItem(product["name"])
            name_item.setToolTip(f"Category: {product['category_name']}")
            self.inventory_table.setItem(row, 1, name_item)
            
            # Purchase Price
            purchase_price_item = QTableWidgetItem(f"${product['purchase_price']:.2f}")
            purchase_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.inventory_table.setItem(row, 2, purchase_price_item)
            
            # Sale Price
            sale_price_item = QTableWidgetItem(f"${product['sale_price']:.2f}")
            sale_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            # Color the sale price green
            sale_price_item.setForeground(Qt.darkGreen)
            self.inventory_table.setItem(row, 3, sale_price_item)
            
            # Total Added
            total_added_item = QTableWidgetItem(str(product["total_added"]))
            total_added_item.setTextAlignment(Qt.AlignCenter)
            self.inventory_table.setItem(row, 4, total_added_item)
            
            # Sold
            sold_item = QTableWidgetItem(str(product["sold"]))
            sold_item.setTextAlignment(Qt.AlignCenter)
            self.inventory_table.setItem(row, 5, sold_item)
            
            # Remaining
            remaining = product["remaining"]
            remaining_item = QTableWidgetItem(str(remaining))
            remaining_item.setTextAlignment(Qt.AlignCenter)
            
            # Color code the remaining based on stock level
            if remaining <= 0:
                remaining_item.setBackground(Qt.red)
                remaining_item.setForeground(Qt.white)
            elif remaining <= 5:
                remaining_item.setBackground(Qt.yellow)
            
            self.inventory_table.setItem(row, 6, remaining_item)
        
        # Reset the product detail view if no products or none selected
        if hasattr(self, 'product_detail') and (self.inventory_table.rowCount() == 0 or not self.inventory_table.selectedItems()):
            self.product_detail.clear()
    
    def refresh_category_filter(self):
        """Refresh the category filter dropdown"""
        # Remember current selection
        current_id = self.current_category_id
        
        # Clear and refill the category filter
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        
        # Add "All Categories" option
        self.category_filter.addItem("All Categories", None)
        
        # Add each category
        categories = database.get_all_categories()
        selected_index = 0
        
        for i, category in enumerate(categories):
            self.category_filter.addItem(category["name"], category["id"])
            if category["id"] == current_id:
                selected_index = i + 1  # +1 for "All Categories"
        
        # Restore selection
        self.category_filter.setCurrentIndex(selected_index)
        self.category_filter.blockSignals(False)
    
    @pyqtSlot(str)
    def on_search_changed(self, text):
        """Handle search input changes"""
        self.refresh_inventory()
    
    def on_category_filter_changed(self, index):
        """Handle category filter changes"""
        if index >= 0:
            self.current_category_id = self.category_filter.itemData(index)
            self.refresh_inventory()
    
    def clear_search(self):
        """Clear the search input and refresh"""
        self.search_input.clear()
        self.refresh_inventory()
    
    def on_product_selected(self):
        """Handle product selection in the table"""
        if not hasattr(self, 'product_detail'):
            return
            
        selected_items = self.inventory_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            key_item = self.inventory_table.item(row, 0)
            if key_item:
                key_number = key_item.data(Qt.UserRole)
                product = database.get_product_by_key(key_number)
                if product:
                    self.product_detail.set_product(product)
        else:
            self.product_detail.clear()
    
    def show_context_menu(self, position):
        """Show context menu for right-click on inventory items"""
        if not self.is_admin:
            return
            
        menu = QMenu()
        delete_action = menu.addAction("Delete Product")
        
        # Only show the menu if a row is selected
        if not self.inventory_table.selectedItems():
            return
            
        # Show the context menu
        action = menu.exec_(self.inventory_table.mapToGlobal(position))
        
        # Handle menu actions
        if action == delete_action:
            self.delete_selected_product()
    
    def delete_selected_product(self):
        """Delete the selected product"""
        if not self.is_admin:
            return
            
        selected_items = self.inventory_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a product to delete")
            return
        
        # Get the key number from the first column
        row = selected_items[0].row()
        key_item = self.inventory_table.item(row, 0)
        if not key_item:
            return
            
        key_number = key_item.data(Qt.UserRole)
        product_name = self.inventory_table.item(row, 1).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete product '{product_name}' (Key: {key_number})?\n\n"
            f"This action cannot be undone. Products with sales records cannot be deleted.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = database.delete_product(key_number)
            if success:
                QMessageBox.information(self, "Success", f"Product '{product_name}' has been deleted")
                self.refresh_inventory()
                if hasattr(self, 'product_detail'):
                    self.product_detail.clear()
            else:
                QMessageBox.warning(
                    self, 
                    "Cannot Delete", 
                    f"Unable to delete product '{product_name}'.\n\n"
                    f"Products with sales records cannot be deleted to maintain sales history integrity."
                )
