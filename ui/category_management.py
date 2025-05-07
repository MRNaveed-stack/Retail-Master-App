from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QInputDialog, QMessageBox, QLineEdit,
                            QDialog, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal

import database

class CategoryDialog(QDialog):
    """Dialog for adding or editing a category"""
    def __init__(self, parent=None, category_id=None, category_name="", category_description=""):
        super().__init__(parent)
        
        self.category_id = category_id
        is_new = category_id is None
        
        # Set window title
        self.setWindowTitle("Add New Category" if is_new else "Edit Category")
        self.setMinimumWidth(350)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create form
        form = QFormLayout()
        
        # Category name field
        self.name_input = QLineEdit(category_name)
        form.addRow("Category Name:", self.name_input)
        
        # Category description field
        self.description_input = QLineEdit(category_description)
        form.addRow("Description:", self.description_input)
        
        layout.addLayout(form)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        # Save button
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept_category)
        save_btn.setDefault(True)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def accept_category(self):
        """Validate and accept the category"""
        name = self.name_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Missing Information", "Category name is required.")
            return
        
        # Store values for retrieval after dialog is closed
        self.category_name = name
        self.category_description = self.description_input.text().strip()
        
        self.accept()

class CategoryManagementWidget(QWidget):
    """Widget for managing product categories"""
    
    def __init__(self, on_category_changed=None):
        super().__init__()
        
        # Store callback function
        self.on_category_changed = on_category_changed
        
        # Create layout
        self.layout = QVBoxLayout(self)
        
        # Create button section
        button_layout = QHBoxLayout()
        
        # Add Category button
        add_button = QPushButton("Add New Category")
        add_button.setIcon(self.style().standardIcon(self.style().SP_FileDialogNewFolder))
        add_button.clicked.connect(self.add_category)
        button_layout.addWidget(add_button)
        
        # Edit Category button
        self.edit_button = QPushButton("Edit Selected Category")
        self.edit_button.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))
        self.edit_button.clicked.connect(self.edit_category)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        # Delete Category button
        self.delete_button = QPushButton("Delete Selected Category")
        self.delete_button.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
        self.delete_button.clicked.connect(self.delete_category)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        
        self.layout.addLayout(button_layout)
        
        # Instructions
        instructions = QLabel("Manage product categories to better organize your inventory.")
        instructions.setStyleSheet("color: #666; font-style: italic;")
        self.layout.addWidget(instructions)
        
        # Create categories table
        self.create_category_table()
        
        # Refresh categories
        self.refresh_categories()
    
    def create_category_table(self):
        """Create the categories table"""
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(3)
        self.category_table.setHorizontalHeaderLabels(["ID", "Category Name", "Description"])
        
        # Set table properties
        self.category_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.category_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.category_table.verticalHeader().setVisible(False)
        self.category_table.setAlternatingRowColors(True)
        self.category_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.category_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Connect selection change
        self.category_table.itemSelectionChanged.connect(self.on_category_selected)
        
        self.layout.addWidget(self.category_table)
        
        # Statistics section
        stats_layout = QHBoxLayout()
        
        self.categories_count = QLabel("Categories: 0")
        stats_layout.addWidget(self.categories_count)
        
        stats_layout.addStretch()
        
        self.layout.addLayout(stats_layout)
    
    def refresh_categories(self):
        """Refresh the categories table with current data"""
        # Get all categories
        categories = database.get_all_categories()
        
        # Update categories count
        self.categories_count.setText(f"Categories: {len(categories)}")
        
        # Clear table
        self.category_table.setRowCount(0)
        
        # Populate table with categories
        for row, category in enumerate(categories):
            self.category_table.insertRow(row)
            
            # ID
            id_item = QTableWidgetItem(str(category["id"]))
            id_item.setData(Qt.UserRole, category["id"])
            self.category_table.setItem(row, 0, id_item)
            
            # Category Name
            name_item = QTableWidgetItem(category["name"])
            self.category_table.setItem(row, 1, name_item)
            
            # Description
            desc_item = QTableWidgetItem(category["description"] or "")
            self.category_table.setItem(row, 2, desc_item)
            
            # Special styling for default category
            if category["id"] == 1:  # Default category
                id_item.setBackground(Qt.lightGray)
                name_item.setBackground(Qt.lightGray)
                desc_item.setBackground(Qt.lightGray)
                
                # Add note
                name_item.setToolTip("Default category - cannot be deleted")
                desc_item.setToolTip("Default category - cannot be deleted")
    
    def on_category_selected(self):
        """Handle category selection in the table"""
        selected_items = self.category_table.selectedItems()
        
        if selected_items:
            row = selected_items[0].row()
            category_id = self.category_table.item(row, 0).data(Qt.UserRole)
            
            # Enable/disable edit and delete buttons
            self.edit_button.setEnabled(True)
            
            # Only allow deleting non-default categories
            self.delete_button.setEnabled(category_id != 1)
        else:
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
    
    def add_category(self):
        """Show dialog to add a new category"""
        dialog = CategoryDialog(self)
        if dialog.exec_():
            name = dialog.category_name
            description = dialog.category_description
            
            # Add the category to the database
            category_id = database.add_category(name, description)
            if category_id:
                self.refresh_categories()
                
                # Notify about category change
                if self.on_category_changed:
                    self.on_category_changed()
            else:
                QMessageBox.warning(
                    self, 
                    "Category Exists", 
                    f"A category with the name '{name}' already exists."
                )
    
    def edit_category(self):
        """Edit the selected category"""
        selected_items = self.category_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        category_id = self.category_table.item(row, 0).data(Qt.UserRole)
        category_name = self.category_table.item(row, 1).text()
        category_description = self.category_table.item(row, 2).text()
        
        dialog = CategoryDialog(
            self,
            category_id=category_id,
            category_name=category_name,
            category_description=category_description
        )
        
        if dialog.exec_():
            name = dialog.category_name
            description = dialog.category_description
            
            # Update the category
            success = database.update_category(category_id, name, description)
            if success:
                self.refresh_categories()
                
                # Notify about category change
                if self.on_category_changed:
                    self.on_category_changed()
            else:
                QMessageBox.warning(
                    self, 
                    "Update Failed", 
                    f"Failed to update category. A category with the name '{name}' may already exist."
                )
    
    def delete_category(self):
        """Delete the selected category"""
        selected_items = self.category_table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        category_id = self.category_table.item(row, 0).data(Qt.UserRole)
        category_name = self.category_table.item(row, 1).text()
        
        # Don't allow deleting the default category
        if category_id == 1:
            QMessageBox.warning(
                self,
                "Cannot Delete Default",
                "The default category cannot be deleted."
            )
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the category '{category_name}'?\n\n"
            "All products in this category will be moved to the default category.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = database.delete_category(category_id)
            if success:
                self.refresh_categories()
                
                # Notify about category change
                if self.on_category_changed:
                    self.on_category_changed()
            else:
                QMessageBox.warning(
                    self,
                    "Delete Failed",
                    f"Failed to delete category '{category_name}'."
                )
