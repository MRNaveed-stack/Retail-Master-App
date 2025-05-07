from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox, 
                             QSpinBox, QDoubleSpinBox, QGroupBox, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QDialog, QTextEdit, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QImage, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
import base64
import os
from datetime import datetime

import database

class GenerateBillWidget(QWidget):
    """
    Widget for generating bills and recording sales.
    """

    # Signal when a sale is completed
    sale_completed = pyqtSignal()

    def __init__(self, on_sale_callback=None):
        super().__init__()

        # Store the callback function
        self.on_sale_callback = on_sale_callback

        # Set up the layout
        self.layout = QVBoxLayout(self)

        # Create product selection section
        self.create_product_selection()

        # Create cart section to accumulate multiple items (moved to top for visibility)
        self.create_cart_section()

        # Create bill preview section
        self.create_bill_preview()

        # Create action buttons section
        self.create_action_buttons()

        # Initialize the product list
        self.refresh_product_list()

    def create_product_selection(self):
        """Create the product selection section"""
        product_group = QGroupBox("Select Product")
        product_layout = QFormLayout(product_group)

        # Category filter
        self.category_combo = QComboBox()
        self.category_combo.currentIndexChanged.connect(self.on_category_selected)
        product_layout.addRow("Category:", self.category_combo)

        # Product key number selection
        self.key_number_combo = QComboBox()
        self.key_number_combo.setEditable(True)
        self.key_number_combo.setMinimumWidth(150)
        self.key_number_combo.currentIndexChanged.connect(self.on_product_selected)
        product_layout.addRow("Key Number:", self.key_number_combo)

        # Product name display (read-only)
        self.product_name = QLineEdit()
        self.product_name.setReadOnly(True)
        product_layout.addRow("Product Name:", self.product_name)

        # Product image display (small preview)
        image_layout = QHBoxLayout()
        self.product_image = QLabel()
        self.product_image.setFixedSize(100, 80)
        self.product_image.setAlignment(Qt.AlignCenter)
        self.product_image.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd;")
        image_layout.addWidget(self.product_image)
        image_layout.addStretch(1)
        product_layout.addRow("Product Image:", self.product_image)

        # Sale price display (editable)
        self.product_sale_price = QDoubleSpinBox()
        self.product_sale_price.setPrefix("$ ")
        self.product_sale_price.setRange(0.01, 9999999.99)
        self.product_sale_price.setDecimals(2)
        self.product_sale_price.valueChanged.connect(self.update_bill_preview)
        product_layout.addRow("Sale Price:", self.product_sale_price)

        # Available quantity display (read-only)
        self.available_qty = QLineEdit()
        self.available_qty.setReadOnly(True)
        product_layout.addRow("Available Quantity:", self.available_qty)

        # Quantity to sell
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 9999)
        self.quantity_input.setSingleStep(1)
        self.quantity_input.valueChanged.connect(self.update_bill_preview)
        product_layout.addRow("Quantity:", self.quantity_input)

        # Add to cart button
        add_to_cart_layout = QHBoxLayout()
        self.add_to_cart_btn = QPushButton("➕ Add to Cart")
        self.add_to_cart_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogNewFolder))
        self.add_to_cart_btn.clicked.connect(self.add_to_cart)
        self.add_to_cart_btn.setEnabled(False)
        # Make button bigger with custom styling
        self.add_to_cart_btn.setMinimumWidth(150)
        self.add_to_cart_btn.setMinimumHeight(40)
        self.add_to_cart_btn.setFont(QFont("Arial", 11, QFont.Bold))
        self.add_to_cart_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        add_to_cart_layout.addStretch()
        add_to_cart_layout.addWidget(self.add_to_cart_btn)
        product_layout.addRow("", add_to_cart_layout)

        self.layout.addWidget(product_group)

    def create_cart_section(self):
        """Create the cart section for multiple items"""
        # Add a big heading to make the shopping cart more prominent
        cart_header = QLabel("SHOPPING CART")
        cart_header.setFont(QFont("Arial", 12, QFont.Bold))
        cart_header.setAlignment(Qt.AlignCenter)
        cart_header.setStyleSheet("color: #2a5885; margin: 5px 0;")
        self.layout.addWidget(cart_header)

        cart_group = QGroupBox()  # No title since we added a header
        cart_layout = QVBoxLayout(cart_group)
        cart_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding

        # Create cart table with reduced height but clear styling
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels([
            "Key", "Product", "Price", "Quantity", "Total"
        ])
        self.cart_table.setMinimumHeight(100)  # Ensure minimum height
        self.cart_table.setMaximumHeight(150)  # Limit height to fit screen

        # Set table properties for compact but visible display
        self.cart_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.cart_table.horizontalHeader().setDefaultSectionSize(80)  # Smaller column width
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cart_table.setStyleSheet("QTableWidget { border: 1px solid #3a76d8; }")  # Blue border

        # Set font size explicitly for the table
        table_font = QFont("Arial", 9)
        self.cart_table.setFont(table_font)

        # Make column headers more visible
        header_font = QFont("Arial", 9, QFont.Bold)
        self.cart_table.horizontalHeader().setFont(header_font)

        cart_layout.addWidget(self.cart_table)

        # Cart controls in a more compact layout
        cart_controls = QHBoxLayout()

        # Remove from cart button (clearer text)
        self.remove_from_cart_btn = QPushButton("🗑️ Remove Item")
        self.remove_from_cart_btn.clicked.connect(self.remove_from_cart)
        self.remove_from_cart_btn.setToolTip("Remove selected item from cart")
        cart_controls.addWidget(self.remove_from_cart_btn)

        # Clear cart button (clearer text)
        self.clear_cart_btn = QPushButton("🧹 Clear All")
        self.clear_cart_btn.clicked.connect(self.clear_cart)
        self.clear_cart_btn.setToolTip("Remove all items from cart")
        cart_controls.addWidget(self.clear_cart_btn)

        cart_controls.addStretch()

        cart_layout.addLayout(cart_controls)

        # Ensure the cart is visible with enough space
        cart_group.setMaximumHeight(250)  # Enough height for table and buttons

        self.layout.addWidget(cart_group)

        # Cart status label (shows how many items are in cart)
        self.cart_status = QLabel("Cart is empty")
        self.cart_status.setAlignment(Qt.AlignCenter)
        self.cart_status.setStyleSheet("font-style: italic;")
        self.layout.addWidget(self.cart_status)

        # Initialize cart
        self.cart_items = []

    def create_bill_preview(self):
        """Create the bill preview section"""
        preview_group = QGroupBox("Bill Preview")
        preview_layout = QVBoxLayout(preview_group)

        # Current date display
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        date_label.setFont(QFont("Arial", 10))
        self.date_display = QLabel(datetime.now().strftime("%Y-%m-%d %H:%M"))
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_display)
        date_layout.addStretch()

        preview_layout.addLayout(date_layout)

        # Total amount
        total_layout = QHBoxLayout()
        total_label = QLabel("Total Amount:")
        total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_amount = QLabel("$0.00")
        self.total_amount.setFont(QFont("Arial", 14, QFont.Bold))
        self.total_amount.setStyleSheet("color: blue;")
        total_layout.addWidget(total_label)
        total_layout.addStretch()
        total_layout.addWidget(self.total_amount)

        # Profit (only visible to admin)
        profit_layout = QHBoxLayout()
        profit_label = QLabel("Estimated Profit:")
        profit_label.setFont(QFont("Arial", 10))
        self.profit_amount = QLabel("$0.00")
        self.profit_amount.setFont(QFont("Arial", 10))
        self.profit_amount.setStyleSheet("color: green;")
        profit_layout.addWidget(profit_label)
        profit_layout.addStretch()
        profit_layout.addWidget(self.profit_amount)

        preview_layout.addLayout(total_layout)
        preview_layout.addLayout(profit_layout)

        self.layout.addWidget(preview_group)

    def create_action_buttons(self):
        """Create action buttons section"""
        buttons_layout = QHBoxLayout()

        # Clear button
        clear_button = QPushButton("Clear Form")
        clear_button.clicked.connect(self.clear_form)

        # Complete Sale button
        self.complete_sale_button = QPushButton("Complete Sale")
        self.complete_sale_button.setEnabled(False)
        self.complete_sale_button.clicked.connect(self.complete_sale)
        self.complete_sale_button.setStyleSheet("background-color: #4CAF50; color: white;")

        buttons_layout.addWidget(clear_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.complete_sale_button)

        self.layout.addLayout(buttons_layout)

    def refresh_product_list(self):
        """Refresh the list of products in the combo box"""
        # Refresh categories in the dropdown
        self.refresh_categories()

        # Save the current selection if any
        current_key = self.key_number_combo.currentText() if self.key_number_combo.count() > 0 else ""

        # Clear the combo box
        self.key_number_combo.clear()

        # Get all products or products for the current category
        category_id = self.category_combo.currentData()
        if category_id is not None:
            products = database.get_products_by_category(category_id)
        else:
            products = database.get_all_products()

        # Add products to combo box
        for product in products:
            if product["remaining"] > 0:  # Only show products with stock
                self.key_number_combo.addItem(
                    f"{product['key_number']} - {product['name']}",
                    product["key_number"]
                )

        # Try to restore the previous selection
        if current_key:
            index = self.key_number_combo.findText(current_key, Qt.MatchStartsWith)
            if index >= 0:
                self.key_number_combo.setCurrentIndex(index)

    def refresh_categories(self):
        """Refresh the category dropdown for filtering products"""
        # Remember current selection
        current_id = self.category_combo.currentData()

        # Clear and refill the category dropdown
        self.category_combo.blockSignals(True)
        self.category_combo.clear()

        # Add "All Categories" option
        self.category_combo.addItem("All Categories", None)

        # Add each category
        categories = database.get_all_categories()
        selected_index = 0

        for i, category in enumerate(categories):
            self.category_combo.addItem(category["name"], category["id"])
            if category["id"] == current_id:
                selected_index = i + 1  # +1 for "All Categories"

        # Restore selection
        self.category_combo.setCurrentIndex(selected_index)
        self.category_combo.blockSignals(False)

    def on_category_selected(self, index):
        """Handle category selection changes"""
        # Refresh product list for this category
        self.refresh_product_list()

    def on_product_selected(self, index):
        """Handle product selection changes"""
        if index >= 0:
            key_number = self.key_number_combo.itemData(index)
            if key_number:
                product = database.get_product_by_key(key_number)
                if product:
                    self.product_name.setText(product["name"])

                    # Set the product sale price from product
                    self.product_sale_price.setValue(product["sale_price"])

                    self.available_qty.setText(str(product["remaining"]))

                    # Set maximum quantity to available stock
                    self.quantity_input.setMaximum(product["remaining"])

                    # Display product image if available
                    self.display_product_image(product)

                    # Update bill preview
                    self.update_bill_preview()

                    # Enable add to cart button
                    self.add_to_cart_btn.setEnabled(True)
                    return

        # Clear product details if no valid selection
        self.product_name.clear()
        self.product_sale_price.setValue(0)
        self.available_qty.clear()
        self.product_image.clear()
        self.add_to_cart_btn.setEnabled(False)

    def display_product_image(self, product):
        """Display the product image"""
        # Clear previous image
        self.product_image.clear()

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
                        100, 80, 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.product_image.setPixmap(pixmap)
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
                        100, 80, 
                        Qt.KeepAspectRatio, 
                        Qt.SmoothTransformation
                    )
                    self.product_image.setPixmap(pixmap)
                    return
            except Exception as e:
                print(f"Error loading image from path: {e}")

        # If no image or loading failed
        self.product_image.setText("No image")

    def add_to_cart(self):
        """Add the current product to the cart"""
        index = self.key_number_combo.currentIndex()
        if index < 0:
            QMessageBox.warning(self, "Error", "Please select a product.")
            return

        key_number = self.key_number_combo.itemData(index)
        product_name = self.product_name.text()
        sale_price = self.product_sale_price.value()
        quantity = self.quantity_input.value()

        # Get product details for profit calculation
        product = database.get_product_by_key(key_number)
        if not product:
            QMessageBox.warning(self, "Error", "Product not found.")
            return

        purchase_price = product["purchase_price"]

        # Check if this product is already in the cart
        for i, item in enumerate(self.cart_items):
            if item["key_number"] == key_number:
                # Update the quantity
                new_quantity = item["quantity"] + quantity

                # Check if we have enough stock
                if new_quantity > product["remaining"]:
                    QMessageBox.warning(
                        self, 
                        "Not Enough Stock", 
                        f"The requested quantity exceeds available stock.\n\n"
                        f"Available: {product['remaining']}\n"
                        f"In Cart: {item['quantity']}\n"
                        f"Requested: {quantity}\n"
                        f"Total: {new_quantity}"
                    )
                    return

                # Update the cart item
                item["quantity"] = new_quantity
                item["total"] = new_quantity * sale_price

                # Update the table
                self.update_cart_table()
                self.update_bill_preview()
                return

        # Add new item to cart
        self.cart_items.append({
            "key_number": key_number,
            "name": product_name,
            "price": sale_price,
            "quantity": quantity,
            "total": sale_price * quantity,
            "purchase_price": purchase_price
        })

        # Update the cart table
        self.update_cart_table()

        # Update bill preview
        self.update_bill_preview()

        # Enable complete sale button if cart has items
        self.complete_sale_button.setEnabled(len(self.cart_items) > 0)

    def update_cart_table(self):
        """Update the cart table with current items"""
        # Clear the table
        self.cart_table.setRowCount(0)

        # Populate with items
        for row, item in enumerate(self.cart_items):
            self.cart_table.insertRow(row)

            # Key Number
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(item["key_number"])))

            # Product Name
            self.cart_table.setItem(row, 1, QTableWidgetItem(item["name"]))

            # Price
            price_item = QTableWidgetItem(f"${item['price']:.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.cart_table.setItem(row, 2, price_item)

            # Quantity
            qty_item = QTableWidgetItem(str(item["quantity"]))
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.cart_table.setItem(row, 3, qty_item)

            # Total
            total_item = QTableWidgetItem(f"${item['total']:.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.cart_table.setItem(row, 4, total_item)

    def remove_from_cart(self):
        """Remove the selected item from the cart"""
        selected_items = self.cart_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an item to remove")
            return

        row = selected_items[0].row()

        # Remove the item from the cart list
        if 0 <= row < len(self.cart_items):
            del self.cart_items[row]

            # Update the cart table
            self.update_cart_table()

            # Update bill preview
            self.update_bill_preview()

            # Enable/disable complete sale button
            self.complete_sale_button.setEnabled(len(self.cart_items) > 0)

    def clear_cart(self):
        """Clear all items from the cart"""
        if not self.cart_items:
            return

        reply = QMessageBox.question(
            self,
            "Clear Cart",
            "Are you sure you want to clear all items from the cart?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.cart_items = []
            self.update_cart_table()
            self.update_bill_preview()
            self.complete_sale_button.setEnabled(False)

    def update_bill_preview(self):
        """Update the bill preview based on current inputs"""
        # Update the single product selection preview
        sale_price = self.product_sale_price.value()
        quantity = self.quantity_input.value()
        single_total = sale_price * quantity

        # Calculate cart total
        cart_total = sum(item["total"] for item in self.cart_items)

        # Show total amount
        total = cart_total
        self.total_amount.setText(f"${total:.2f}")

        # Calculate profit from cart items
        profit = sum((item["price"] - item["purchase_price"]) * item["quantity"] for item in self.cart_items)
        self.profit_amount.setText(f"${profit:.2f}")

        # Update date/time
        self.date_display.setText(datetime.now().strftime("%Y-%m-%d %H:%M"))

        # Update cart status label with total quantity
        total_quantity = sum(item["quantity"] for item in self.cart_items)
        if total_quantity > 0:
            self.cart_status.setText(f"{total_quantity} item{'s' if total_quantity>1 else ''} in cart")
            self.cart_status.show()
        else:
            self.cart_status.setText("Cart is empty")
            self.cart_status.show()


    def complete_sale(self):
        """Complete the sale and record it in the database"""
        if not self.cart_items:
            empty_cart_msg = QMessageBox(QMessageBox.Warning, "Empty Cart", "Please add items to the cart before completing the sale.")
            empty_cart_msg.setStyleSheet("QLabel { font-size: 11pt; }")
            empty_cart_msg.exec_()
            return

        # Confirm the sale
        total = sum(item["total"] for item in self.cart_items)
        profit = sum((item["price"] - item["purchase_price"]) * item["quantity"] for item in self.cart_items)

        confirm_msg_box = QMessageBox(
            QMessageBox.Question,
            "Complete Sale",
            f"Complete this sale for ${total:.2f}?"
        )
        confirm_msg_box.setStyleSheet("QLabel { font-size: 11pt; }")
        confirm_msg_box.addButton(QMessageBox.Yes)
        confirm_msg_box.addButton(QMessageBox.No)
        confirm_msg_box.setDefaultButton(QMessageBox.Yes)
        reply = confirm_msg_box.exec_()

        if reply == QMessageBox.Yes:
            # Get customer information
            from ui.customer_info_dialog import CustomerInfoDialog
            customer_dialog = CustomerInfoDialog(self)
            result = customer_dialog.exec_()

            if result == QDialog.Accepted:
                customer_id = customer_dialog.get_customer_id()
                success = True
                last_sale_id = None

                # Record each item as a separate sale
                for item in self.cart_items:
                    sale_id = database.record_sale(
                        item["key_number"],
                        item["quantity"],
                        item["price"],
                        customer_id
                    )

                    if not sale_id:
                        success = False
                        error_msg_box = QMessageBox(
                            QMessageBox.Warning,
                            "Error",
                            f"Failed to record sale for product {item['name']} (Key: {item['key_number']}).\n"
                            f"Please check that the product exists and has sufficient stock."
                        )
                        error_msg_box.setStyleSheet("QLabel { font-size: 11pt; }")
                        error_msg_box.exec_()
                    else:
                        last_sale_id = sale_id

                if success:
                    msg_box = QMessageBox(QMessageBox.Information, "Sale Completed", f"Sale recorded successfully!\n\nTotal Amount: ${total:.2f}")
                    msg_box.setStyleSheet("QLabel { font-size: 11pt; }")  # Set smaller font size
                    msg_box.exec_()

                    # Show print bill option with smaller font
                    if last_sale_id:
                        print_msg_box = QMessageBox(
                            QMessageBox.Question,
                            "Print Bill",
                            "Would you like to print a bill for this sale?"
                        )
                        print_msg_box.setStyleSheet("QLabel { font-size: 11pt; }")
                        print_msg_box.addButton(QMessageBox.Yes)
                        print_msg_box.addButton(QMessageBox.No)
                        print_msg_box.setDefaultButton(QMessageBox.Yes)
                        print_reply = print_msg_box.exec_()

                        if print_reply == QMessageBox.Yes:
                            from ui.bill_printer import BillPreviewDialog
                            bill_dialog = BillPreviewDialog(last_sale_id, self)
                            bill_dialog.exec_()

                    # Clear the cart and form
                    self.cart_items = []
                    self.update_cart_table()
                    self.clear_form()

                    # Refresh the product list
                    self.refresh_product_list()

                    # Notify about the completed sale
                    if self.on_sale_callback:
                        self.on_sale_callback()

    def clear_form(self):
        """Clear all form inputs"""
        self.key_number_combo.setCurrentIndex(-1)
        self.product_name.clear()
        self.product_image.clear()
        self.product_sale_price.setValue(0)
        self.available_qty.clear()
        self.quantity_input.setValue(1)
        self.total_amount.setText("$0.00")
        self.profit_amount.setText("$0.00")
        self.add_to_cart_btn.setEnabled(False)
        self.complete_sale_button.setEnabled(len(self.cart_items) > 0)