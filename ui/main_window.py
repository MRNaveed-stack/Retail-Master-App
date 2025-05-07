from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTabWidget, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from ui.admin_panel import AdminPanel
from ui.customer_panel import CustomerPanel
import database

class MainWindow(QMainWindow):
    """
    The main window of the application containing admin and customer panels.
    """
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Retail Master")
        self.setMinimumSize(1100, 700)
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create header
        self.create_header()
        
        # Create tab widget for panels
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setDocumentMode(True)
        
        # Create panels
        self.admin_panel = AdminPanel()
        self.customer_panel = CustomerPanel(self.on_sale_completed)
        
        # Add panels to tabs
        self.tabs.addTab(self.admin_panel, "Admin Panel")
        self.tabs.addTab(self.customer_panel, "Customer Panel")
        
        # Add tabs to main layout
        self.main_layout.addWidget(self.tabs)
        
        # Create footer with status
        self.create_footer()
        
        # Connect tab change signal
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Initialize first tab
        self.on_tab_changed(0)
    
    def create_header(self):
        """Create the header section with title and info"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # App title
        title = QLabel("Retail Master")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # Add to layout
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Panel description label
        self.panel_label = QLabel("Admin Panel")
        self.panel_label.setFont(QFont("Arial", 1, QFont.Bold))
        self.panel_label.setStyleSheet("color: #2a5885;")
        header_layout.addWidget(self.panel_label)
        
        self.main_layout.addWidget(header)
    
    def create_footer(self):
        """Create the footer with status and total profit display"""
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 5, 10, 5)
        
        # Status label
        self.status_label = QLabel("Ready")
        
        # Total profit display
        profit_label = QLabel("Total Profit:")
        profit_label.setStyleSheet("font-weight: bold;")
        
        self.profit_value = QLabel("$0.00")
        self.profit_value.setStyleSheet("color: green; font-weight: bold; font-size: 14px;")
        
        # Add to layout
        footer_layout.addWidget(self.status_label)
        footer_layout.addStretch()
        footer_layout.addWidget(profit_label)
        footer_layout.addWidget(self.profit_value)
        
        self.main_layout.addWidget(footer)
        
        # Update the profit display
        self.update_profit_display()
    
    def update_profit_display(self):
        """Update the total profit display in the footer"""
        total_profit = database.get_total_profit()
        self.profit_value.setText(f"${total_profit:.2f}")
    
    def on_tab_changed(self, index):
        """Handle tab change events to update panel info and refresh data"""
        if index == 0:  # Admin panel
            self.panel_label.setText("Admin Panel")
            self.admin_panel.refresh_data()
        elif index == 1:  # Customer panel
            self.panel_label.setText("Customer Panel")
            self.customer_panel.refresh_data()
        
        self.update_profit_display()
    
    def on_sale_completed(self):
        """Handle completed sale event"""
        self.status_label.setText("Sale completed successfully")
        self.update_profit_display()
        
        # Refresh data in both panels
        self.admin_panel.refresh_data()
        self.customer_panel.refresh_data()
