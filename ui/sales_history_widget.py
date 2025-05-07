from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QLabel, QPushButton, QHeaderView,
                            QMessageBox, QMenu, QInputDialog, QComboBox, QGroupBox,
                            QDateEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QCursor

import database
from datetime import datetime, timedelta

class SalesHistoryWidget(QWidget):
    """
    Widget for displaying sales history and profit information.
    """
    def __init__(self, is_admin=False):
        super().__init__()
        
        # Store admin mode
        self.is_admin = is_admin
        
        # Current selected category for filtering
        self.current_category_id = None
        
        # Date range for filtering
        self.start_date = None
        self.end_date = None
        
        # Set up layout
        self.layout = QVBoxLayout(self)
        
        # Create filter section
        self.create_filter_section()
        
        # Create summary section
        self.create_summary_section()
        
        # Create sales history table
        self.create_sales_table()
        
        # Initialize data
        self.refresh_sales_history()
    
    def create_filter_section(self):
        """Create the filter section for sales history"""
        filter_group = QGroupBox("Filter Options")
        filter_layout = QHBoxLayout(filter_group)
        
        # Category filter
        category_layout = QHBoxLayout()
        category_label = QLabel("Category:")
        self.category_filter = QComboBox()
        self.category_filter.currentIndexChanged.connect(self.on_filter_changed)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_filter)
        
        # Date range filter
        date_layout = QHBoxLayout()
        
        # From date
        from_label = QLabel("From:")
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.dateChanged.connect(self.on_filter_changed)
        
        # To date
        to_label = QLabel("To:")
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.dateChanged.connect(self.on_filter_changed)
        
        date_layout.addWidget(from_label)
        date_layout.addWidget(self.from_date)
        date_layout.addWidget(to_label)
        date_layout.addWidget(self.to_date)
        
        # Quick date filters
        date_filter_layout = QHBoxLayout()
        
        today_btn = QPushButton("Today")
        today_btn.clicked.connect(lambda: self.set_date_filter("today"))
        
        week_btn = QPushButton("This Week")
        week_btn.clicked.connect(lambda: self.set_date_filter("week"))
        
        month_btn = QPushButton("This Month")
        month_btn.clicked.connect(lambda: self.set_date_filter("month"))
        
        all_btn = QPushButton("All Time")
        all_btn.clicked.connect(lambda: self.set_date_filter("all"))
        
        date_filter_layout.addWidget(today_btn)
        date_filter_layout.addWidget(week_btn)
        date_filter_layout.addWidget(month_btn)
        date_filter_layout.addWidget(all_btn)
        
        # Add all filters to the layout
        filter_layout.addLayout(category_layout)
        filter_layout.addLayout(date_layout)
        filter_layout.addLayout(date_filter_layout)
        
        self.layout.addWidget(filter_group)
    
    def create_summary_section(self):
        """Create the summary section with profit information"""
        summary_group = QGroupBox("Sales Summary")
        summary_layout = QHBoxLayout(summary_group)
        
        # Total sales count
        sales_count_label = QLabel("Total Sales:")
        sales_count_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.sales_count = QLabel("0")
        self.sales_count.setFont(QFont("Arial", 10))
        
        # Total revenue
        revenue_label = QLabel("Total Revenue:")
        revenue_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.total_revenue = QLabel("$0.00")
        self.total_revenue.setFont(QFont("Arial", 10))
        
        # Total profit
        profit_label = QLabel("Total Profit:")
        profit_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.total_profit = QLabel("$0.00")
        self.total_profit.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_profit.setStyleSheet("color: green;")
        
        # Profit margin
        margin_label = QLabel("Profit Margin:")
        margin_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.profit_margin = QLabel("0%")
        self.profit_margin.setFont(QFont("Arial", 10))
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(self.style().standardIcon(self.style().SP_BrowserReload))
        refresh_button.clicked.connect(self.refresh_sales_history)
        
        # Clear history button (admin only)
        self.clear_button = QPushButton("Clear History")
        self.clear_button.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
        self.clear_button.clicked.connect(self.clear_sales_history)
        self.clear_button.setVisible(self.is_admin)
        
        # Add to layout
        summary_layout.addWidget(sales_count_label)
        summary_layout.addWidget(self.sales_count)
        summary_layout.addSpacing(20)
        
        summary_layout.addWidget(revenue_label)
        summary_layout.addWidget(self.total_revenue)
        summary_layout.addSpacing(20)
        
        summary_layout.addWidget(profit_label)
        summary_layout.addWidget(self.total_profit)
        summary_layout.addSpacing(20)
        
        summary_layout.addWidget(margin_label)
        summary_layout.addWidget(self.profit_margin)
        summary_layout.addStretch()
        
        summary_layout.addWidget(refresh_button)
        summary_layout.addWidget(self.clear_button)
        
        self.layout.addWidget(summary_group)
    
    def create_sales_table(self):
        """Create the sales history table"""
        # Table container
        table_group = QGroupBox("Sales History")
        table_layout = QVBoxLayout(table_group)
        
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(8)
        self.sales_table.setHorizontalHeaderLabels([
            "Date", "Time", "Key Number", "Product Name", "Category", 
            "Quantity", "Sale Price", "Profit"
        ])
        font = QFont("Arial", 8)  # Smaller font size for table content
        self.sales_table.setFont(font)
        self.sales_table.setRowHeight(0, 20)
        # Set table properties
        self.sales_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.sales_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.sales_table.verticalHeader().setVisible(False)
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Enable context menu
        self.sales_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sales_table.customContextMenuRequested.connect(self.show_context_menu)
        
        table_layout.addWidget(self.sales_table)
        
        # Create action button section (for admin only)
        if self.is_admin:
            action_layout = QHBoxLayout()
            delete_btn = QPushButton("Delete Selected Sale")
            delete_btn.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
            delete_btn.clicked.connect(self.delete_selected_sale)
            action_layout.addWidget(delete_btn)
            action_layout.addStretch()
            
            table_layout.addLayout(action_layout)
        
        self.layout.addWidget(table_group)
    
    def refresh_categories(self):
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
    
    def refresh_sales_history(self):
        """Refresh the sales history table with current data"""
        # Refresh categories first
        self.refresh_categories()
        
        # Get sales history with filters applied
        sales = self.get_filtered_sales()
        
        # Update sales count
        self.sales_count.setText(str(len(sales)))
        
        # Calculate totals for filtered sales
        total_revenue = sum(sale["sale_price"] * sale["quantity"] for sale in sales)
        total_profit = sum(sale["profit"] for sale in sales)
        
        # Update total displays
        self.total_revenue.setText(f"${total_revenue:.2f}")
        self.total_profit.setText(f"${total_profit:.2f}")
        
        # Calculate and update profit margin
        if total_revenue > 0:
            margin = (total_profit / total_revenue) * 100
            self.profit_margin.setText(f"{margin:.1f}%")
        else:
            self.profit_margin.setText("0%")
        
        # Clear table
        self.sales_table.setRowCount(0)
        
        # Populate table with sales
        for row, sale in enumerate(sales):
            self.sales_table.insertRow(row)
            
            # Format date and time
            try:
                sale_datetime = datetime.strptime(sale["sale_date"], "%Y-%m-%d %H:%M:%S")
                date_str = sale_datetime.strftime("%Y-%m-%d")
                time_str = sale_datetime.strftime("%H:%M:%S")
            except ValueError:
                date_str = "Unknown"
                time_str = "Unknown"
            
            # Date
            self.sales_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Time
            self.sales_table.setItem(row, 1, QTableWidgetItem(time_str))
            
            # Key Number
            key_item = QTableWidgetItem(str(sale["key_number"]))
            # Store the sale ID for easier retrieval
            key_item.setData(Qt.UserRole, sale["id"])
            self.sales_table.setItem(row, 2, key_item)
            
            # Product Name
            self.sales_table.setItem(row, 3, QTableWidgetItem(sale["name"]))
            
            # Category
            self.sales_table.setItem(row, 4, QTableWidgetItem(sale["category_name"]))
            
            # Quantity
            quantity_item = QTableWidgetItem(str(sale["quantity"]))
            quantity_item.setTextAlignment(Qt.AlignCenter)
            self.sales_table.setItem(row, 5, quantity_item)
            
            # Sale Price
            price_item = QTableWidgetItem(f"${sale['sale_price']:.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.sales_table.setItem(row, 6, price_item)
            
            # Profit
            profit_item = QTableWidgetItem(f"${sale['profit']:.2f}")
            profit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Color code the profit
            if sale['profit'] > 0:
                profit_item.setForeground(Qt.darkGreen)
            elif sale['profit'] < 0:
                profit_item.setForeground(Qt.red)
            
            self.sales_table.setItem(row, 7, profit_item)
        
        # Sort by date (newest first)
        self.sales_table.sortItems(0, Qt.DescendingOrder)
    
    def get_filtered_sales(self):
        """Get sales history with filters applied"""
        # Apply category filter
        if self.current_category_id is not None:
            sales = database.get_sales_by_category(self.current_category_id)
        else:
            sales = database.get_sales_history()
        
        # Apply date filter if set
        if self.start_date and self.end_date:
            # Convert QDate to string format for comparison
            start_str = self.start_date.toString("yyyy-MM-dd")
            
            # Add one day to end date to include the end date in the range
            end_date_plus = self.end_date.addDays(1)
            end_str = end_date_plus.toString("yyyy-MM-dd")
            
            # Filter sales by date
            sales = [
                sale for sale in sales 
                if start_str <= sale["sale_date"].split()[0] < end_str
            ]
        
        return sales
    
    def on_filter_changed(self, *args):
        """Handle filter changes"""
        # Update category filter
        if isinstance(self.sender(), QComboBox):
            self.current_category_id = self.category_filter.currentData()
        
        # Update date filters
        if isinstance(self.sender(), QDateEdit):
            self.start_date = self.from_date.date()
            self.end_date = self.to_date.date()
            
            # Validate date range
            if self.start_date > self.end_date:
                # Swap dates if end is before start
                self.from_date.setDate(self.end_date)
                self.to_date.setDate(self.start_date)
                self.start_date, self.end_date = self.end_date, self.start_date
        
        # Refresh the data
        self.refresh_sales_history()
    
    def set_date_filter(self, period):
        """Set date filter to predefined periods"""
        today = QDate.currentDate()
        
        if period == "today":
            self.from_date.setDate(today)
            self.to_date.setDate(today)
        
        elif period == "week":
            # Get the first day of the current week (Monday)
            days_to_monday = today.dayOfWeek() - 1  # Qt Monday=1, Sunday=7
            monday = today.addDays(-days_to_monday)
            self.from_date.setDate(monday)
            self.to_date.setDate(today)
        
        elif period == "month":
            # Get the first day of the current month
            first_day = QDate(today.year(), today.month(), 1)
            self.from_date.setDate(first_day)
            self.to_date.setDate(today)
        
        elif period == "all":
            # Set to a date far in the past to show all records
            self.from_date.setDate(QDate(2000, 1, 1))
            self.to_date.setDate(today)
        
        # Update the filter
        self.on_filter_changed()
    
    def show_context_menu(self, position):
        """Show context menu for right-click on sales items"""
        if not self.is_admin:
            return
            
        menu = QMenu()
        delete_action = menu.addAction("Delete Sale")
        
        # Only show the menu if a row is selected
        if not self.sales_table.selectedItems():
            return
            
        # Show the context menu
        action = menu.exec_(self.sales_table.mapToGlobal(position))
        
        # Handle menu actions
        if action == delete_action:
            self.delete_selected_sale()
    
    def delete_selected_sale(self):
        """Delete the selected sale"""
        if not self.is_admin:
            return
            
        selected_items = self.sales_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a sale to delete")
            return
        
        # Get the sale ID from the stored data
        row = selected_items[0].row()
        key_item = self.sales_table.item(row, 2)
        if not key_item:
            return
        
        sale_id = key_item.data(Qt.UserRole)
        product_name = self.sales_table.item(row, 3).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete this sale for '{product_name}'?\n\n"
            f"This will remove the sale record and adjust the inventory accordingly.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = database.delete_sale(sale_id)
            if success:
                QMessageBox.information(self, "Success", "Sale has been deleted")
                self.refresh_sales_history()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete sale")
    
    def clear_sales_history(self):
        """Clear all sales history"""
        if not self.is_admin:
            return
            
        reply = QMessageBox.question(
            self, 
            "Confirm Clear History",
            "Are you sure you want to clear ALL sales history?\n\n"
            "This will delete ALL sales records and reset inventory sold counts.\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Add an extra confirmation step since this is destructive
            verify_reply = QMessageBox.warning(
                self,
                "Final Confirmation",
                "ALL sales history will be permanently deleted and profit data will be lost.\n\n"
                "Type DELETE in the next dialog to confirm this action.",
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            
            if verify_reply == QMessageBox.Ok:
                # Ask for the confirmation text
                confirm_text, ok = QInputDialog.getText(
                    self,
                    "Type DELETE to confirm",
                    "Type DELETE (all capital letters) to confirm deletion:"
                )
                
                if ok and confirm_text == "DELETE":
                    deleted_count = database.clear_sales_history()
                    QMessageBox.information(
                        self, 
                        "History Cleared", 
                        f"Sales history has been cleared. {deleted_count} records were deleted."
                    )
                    self.refresh_sales_history()
