from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

import database

class CustomerInfoDialog(QDialog):
    """
    Dialog for entering customer information for a sale.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Customer Information")
        self.setMinimumWidth(600)  # Even wider dialog
        self.setMinimumHeight(500)  # Even taller dialog
        
        # Make the dialog open in maximized state
        self.showMaximized()
        
        # Set up the dialog
        self.customer_id = None
        self.create_ui()
        self.load_existing_customers()
        
        # Force to New Customer mode on startup with a timer and explicitly set current index
        QTimer.singleShot(100, self.force_new_customer_mode)
    
    def force_new_customer_mode(self):
        """Force the dialog to show New Customer mode on startup"""
        self.customer_type.setCurrentIndex(0)  # Select "New Customer" option
        self.customer_form_widget.setVisible(True)
        print("Forcing NEW customer mode on startup")
    
    def create_ui(self):
        """Create the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Customer selection or new customer entry
        self.create_customer_selection(layout)
        
        # Customer information form
        self.create_customer_form(layout)
        
        # Buttons for dialog actions
        self.create_buttons(layout)
        
        # Initial UI state
        self.update_ui_for_customer_type()
    
    def create_customer_selection(self, layout):
        """Create the section for selecting existing customer or creating new one"""
        # Add a main title label at the top
        title_label = QLabel("CUSTOMER INFORMATION")
        title_font = QFont("Arial", 12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2a5885; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        selection_layout = QHBoxLayout()
        
        # Option to select existing or new customer - with clear labeling
        type_label = QLabel("Select Option:")
        type_font = QFont("Arial", 10)
        type_font.setBold(True)
        type_label.setFont(type_font)
        selection_layout.addWidget(type_label)
        
        self.customer_type = QComboBox()
        self.customer_type.addItem("➕ New Customer", "new")  # Added icon for better visibility
        self.customer_type.addItem("👤 Existing Customer", "existing") 
        self.customer_type.addItem("🏃 Walk-in Customer (No Info)", "walkin")
        self.customer_type.setFont(QFont("Arial", 12))  # Larger font size
        self.customer_type.setStyleSheet("QComboBox { min-height: 30px; min-width: 250px; background-color: white; }")
        # Force the initial selection to be "New Customer"
        self.customer_type.setCurrentIndex(0)
        self.customer_type.currentIndexChanged.connect(self.update_ui_for_customer_type)
        
        selection_layout.addWidget(self.customer_type)
        
        layout.addLayout(selection_layout)
        
        # Existing customer selection
        self.existing_customer = QComboBox()
        self.existing_customer.setMinimumWidth(250)
        
        # Search bar for customers
        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Search customers...")
        self.customer_search.textChanged.connect(self.filter_customers)
        
        existing_layout = QFormLayout()
        existing_layout.addRow("Search:", self.customer_search)
        existing_layout.addRow("Select Customer:", self.existing_customer)
        
        self.existing_customer_widget = QLabel()
        self.existing_customer_widget.setLayout(existing_layout)
        
        layout.addWidget(self.existing_customer_widget)
    
    def create_customer_form(self, layout):
        """Create the form for entering customer details"""
        form_layout = QFormLayout()
        
        # Set label font for all form labels - smaller to match input fields
        label_font = QFont("Arial", 12)
        label_font.setBold(True)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        # Add less spacing between form rows for a more compact layout
        form_layout.setVerticalSpacing(10)
        
        # Customer name (required) - smaller size but still readable
        self.name_input = QLineEdit()
        self.name_input.setFont(QFont("Arial", 11))
        self.name_input.setMinimumHeight(30)  # Smaller height
        self.name_input.setStyleSheet("background-color: #f0f8ff;")  # Light blue background
        name_label = QLabel("Name*:")
        name_label.setFont(label_font)
        form_layout.addRow(name_label, self.name_input)
        
        # Phone number
        self.phone_input = QLineEdit()
        self.phone_input.setFont(QFont("Arial", 11))
        self.phone_input.setMinimumHeight(30)  # Smaller height
        self.phone_input.setPlaceholderText("Optional")
        phone_label = QLabel("Phone:")
        phone_label.setFont(label_font)
        form_layout.addRow(phone_label, self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setFont(QFont("Arial", 11))
        self.email_input.setMinimumHeight(30)  # Smaller height
        self.email_input.setPlaceholderText("Optional")
        email_label = QLabel("Email:")
        email_label.setFont(label_font)
        form_layout.addRow(email_label, self.email_input)
        
        # Address
        self.address_input = QLineEdit()
        self.address_input.setFont(QFont("Arial", 11))
        self.address_input.setMinimumHeight(30)  # Smaller height
        self.address_input.setPlaceholderText("Optional")
        address_label = QLabel("Address:")
        address_label.setFont(label_font)
        form_layout.addRow(address_label, self.address_input)
        
        # Required fields note
        note = QLabel("* Required field")
        font = QFont("Arial", 12)
        font.setItalic(True)  # This is the correct way to set italic
        note.setFont(font)
        note.setStyleSheet("color: #FF0000;")  # Red color
        form_layout.addRow("", note)
        
        # Create a container widget with smaller margin
        self.customer_form_widget = QLabel()
        self.customer_form_widget.setLayout(form_layout)
        self.customer_form_widget.setStyleSheet("QLabel { padding: 12px; background-color: white; border-radius: 8px; }")
        
        layout.addWidget(self.customer_form_widget)
    
    def create_buttons(self, layout):
        """Create dialog buttons"""
        # Add some space before buttons
        layout.addSpacing(20)
        
        button_layout = QHBoxLayout()
        
        # Cancel button - larger with icon
        cancel_button = QPushButton("❌ Cancel")
        cancel_font = QFont("Arial", 14)
        cancel_font.setBold(True)
        cancel_button.setFont(cancel_font)
        cancel_button.setMinimumHeight(50)
        cancel_button.setMinimumWidth(200)
        cancel_button.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        cancel_button.clicked.connect(self.reject)
        
        # Continue button - larger with icon
        self.continue_button = QPushButton("✅ Continue with Sale")
        continue_font = QFont("Arial", 14)
        continue_font.setBold(True)
        self.continue_button.setFont(continue_font)
        self.continue_button.setMinimumHeight(50)
        self.continue_button.setMinimumWidth(250)
        self.continue_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.continue_button.clicked.connect(self.process_customer)
        
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        button_layout.addWidget(self.continue_button)
        
        # Add some space before buttons
        layout.addSpacing(20)
        
        # Add the button layout directly
        layout.addLayout(button_layout)
    
    def load_existing_customers(self):
        """Load existing customers from the database"""
        self.all_customers = database.get_all_customers()
        self.update_customer_combo()
    
    def update_customer_combo(self, filtered_customers=None):
        """Update the customer combo box with all or filtered customers"""
        customers = filtered_customers if filtered_customers is not None else self.all_customers
        
        self.existing_customer.clear()
        
        # Add each customer
        for customer in customers:
            display_text = f"{customer['name']}"
            if customer['phone']:
                display_text += f" ({customer['phone']})"
            
            self.existing_customer.addItem(display_text, customer['id'])
    
    def filter_customers(self, search_text):
        """Filter the customers based on search text"""
        if not search_text:
            # If search is empty, show all customers
            self.update_customer_combo()
            return
        
        # Filter customers based on name or phone containing the search text
        filtered = [c for c in self.all_customers 
                    if search_text.lower() in c['name'].lower() or
                       (c['phone'] and search_text.lower() in c['phone'].lower())]
        
        self.update_customer_combo(filtered)
    
    def update_ui_for_customer_type(self):
        """Update the UI based on the selected customer type"""
        customer_type = self.customer_type.currentData()
        
        # Debug current selection
        print(f"Selected customer type: {customer_type}")
        
        if customer_type == "new":
            # Show form, hide existing selection
            self.existing_customer_widget.setVisible(False)
            self.customer_form_widget.setVisible(True)
            print("Setting NEW customer form to visible")
            
            # Clear form fields
            self.name_input.clear()
            self.phone_input.clear()
            self.email_input.clear()
            self.address_input.clear()
            
            # Set window title to indicate mode
            self.setWindowTitle("Customer Information - New Customer")
            
        elif customer_type == "existing":
            # Show existing selection, hide form
            self.existing_customer_widget.setVisible(True)
            self.customer_form_widget.setVisible(False)
            print("Setting EXISTING customer selection to visible")
            
            # Set window title to indicate mode
            self.setWindowTitle("Customer Information - Select Existing Customer")
            
        else:  # Walk-in customer
            # Hide both form and selection
            self.existing_customer_widget.setVisible(False)
            self.customer_form_widget.setVisible(False)
            print("Setting WALK-IN customer mode (no forms)")
            
            # Set window title to indicate mode
            self.setWindowTitle("Customer Information - Walk-in Customer")
    
    def process_customer(self):
        """Process the customer information for the sale"""
        customer_type = self.customer_type.currentData()
        print(f"Processing customer with type: {customer_type}")
        
        if customer_type == "walkin":
            # No customer info needed
            self.customer_id = None
            print("Using walk-in customer (no info)")
            self.accept()
            return
        
        elif customer_type == "existing":
            # Get the selected customer ID
            index = self.existing_customer.currentIndex()
            if index >= 0:
                self.customer_id = self.existing_customer.itemData(index)
                name = self.existing_customer.currentText().split("(")[0].strip()
                print(f"Selected existing customer: {name}, ID: {self.customer_id}")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Please select a customer.")
        
        else:  # New customer
            # Validate name (required)
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "Missing Information", "Customer name is required.")
                print("Customer name is empty - showing warning")
                return
            
            # Get the customer information from the form
            name = self.name_input.text().strip()
            phone = self.phone_input.text().strip() or None
            email = self.email_input.text().strip() or None
            address = self.address_input.text().strip() or None
            
            print(f"Sending new customer data: name={name}, phone={phone}, email={email}, address={address}")
            
            try:
                # Add the new customer to the database with error handling
                customer_id = database.add_customer(
                    name=name,
                    phone=phone,
                    email=email,
                    address=address
                )
                
                if customer_id:
                    self.customer_id = customer_id
                    print(f"Successfully added customer: {name}, ID: {customer_id}")
                    QMessageBox.information(self, "Success", f"Customer '{name}' added successfully!")
                    self.accept()
                else:
                    print("Database returned None for customer_id")
                    QMessageBox.critical(self, "Error", "Failed to add customer to the database. No ID returned.")
            except Exception as e:
                print(f"Exception adding customer: {str(e)}")
                QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
    
    def get_customer_id(self):
        """Return the selected or created customer ID"""
        return self.customer_id