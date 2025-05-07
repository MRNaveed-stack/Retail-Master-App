from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTextEdit, QFileDialog, 
                            QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from datetime import datetime
import os

import database

class BillPreviewDialog(QDialog):
    """
    Dialog for previewing and printing customer bills.
    """
    def __init__(self, sale_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bill Preview")
        self.setMinimumSize(800, 800)  # Larger minimum size
        
        # Make the dialog maximized by default
        self.showMaximized()
        
        # Store sale ID
        self.sale_id = sale_id
        
        # Get the bill data
        self.bill_data = database.generate_bill_data(sale_id)
        if not self.bill_data:
            QMessageBox.critical(self, "Error", "Failed to generate bill data.")
            self.reject()
            return
        
        # Create UI
        self.create_ui()
        
        # Generate bill content
        self.generate_bill_html()
    
    def create_ui(self):
        """Create the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Bill preview area with larger font size for better readability
        self.bill_preview = QTextEdit()
        self.bill_preview.setReadOnly(True)
        
        # Set a larger default font size for the bill preview
        font = QFont("Arial", 12)  # Larger font (12pt instead of default)
        self.bill_preview.setFont(font)
        
        # Make the preview take up most of the screen space
        layout.addWidget(self.bill_preview, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        
        # Print Preview button
        preview_button = QPushButton("Print Preview")
        preview_button.clicked.connect(self.show_print_preview)
        
        # Print button
        print_button = QPushButton("Print")
        print_button.clicked.connect(self.print_bill)
        
        # Save as PDF button
        save_button = QPushButton("Save as PDF")
        save_button.clicked.connect(self.save_as_pdf)
        
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        button_layout.addWidget(preview_button)
        button_layout.addWidget(print_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
    
    def generate_bill_html(self):
        """Generate HTML content for the bill"""
        # Get data from bill_data
        if not self.bill_data:
            self.bill_preview.setHtml("<h2>Error: Could not load bill data</h2>")
            return
            
        bill_date = self.bill_data.get("bill_date", "Unknown Date")
        customer = self.bill_data.get("customer", {"name": "Walk-in Customer", "phone": "", "email": "", "address": ""})
        product = self.bill_data.get("product", {"name": "Unknown", "key_number": 0, "category": "Unknown", "unit_price": 0})
        quantity = self.bill_data.get("quantity", 0)
        total_amount = self.bill_data.get("total_amount", 0)
        
        # Store the customer name prominently for the invoice
        customer_name = customer.get('name', 'Walk-in Customer')
        
        # Generate HTML content
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .header h1 {{ margin-bottom: 5px; }}
                .info-section {{ margin-bottom: 15px; }}
                .info-section h3 {{ margin-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                .total {{ text-align: right; margin-top: 20px; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 30px; font-size: 0.9em; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Retail Master</h1>
                <p>Invoice #{self.sale_id}</p>
                <p>Date: {bill_date}</p>
            </div>
            
            <div class="info-section">
                <h3>Customer Information:</h3>
                <p>Name: {customer['name']}</p>
        """
        
        # Add customer details if available
        if customer['phone']:
            html += f"<p>Phone: {customer['phone']}</p>"
        if customer['email']:
            html += f"<p>Email: {customer['email']}</p>"
        if customer['address']:
            html += f"<p>Address: {customer['address']}</p>"
        
        # Product details
        html += f"""
            </div>
            
            <div class="info-section">
                <h3>Product Details:</h3>
                <table>
                    <tr>
                        <th>Product</th>
                        <th>Category</th>
                        <th>Unit Price</th>
                        <th>Quantity</th>
                        <th>Amount</th>
                    </tr>
                    <tr>
                        <td>{product['name']} (#{product['key_number']})</td>
                        <td>{product['category']}</td>
                        <td>${product['unit_price']:.2f}</td>
                        <td>{quantity}</td>
                        <td>${total_amount:.2f}</td>
                    </tr>
                </table>
            </div>
            
            <div class="total">
                <h3>Total Amount: ${total_amount:.2f}</h3>
            </div>
            
            <div class="footer">
                <p>Thank you for your purchase!</p>
                <p>For any questions or concerns, please contact us.</p>
            </div>
        </body>
        </html>
        """
        
        # Set the HTML content to the preview
        self.bill_preview.setHtml(html)
        self.bill_html = html
    
    def show_print_preview(self):
        """Show print preview dialog"""
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(self.print_document)
        preview.exec_()
    
    def print_bill(self):
        """Print the bill"""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QDialog.Accepted:
            self.print_document(printer)
    
    def print_document(self, printer):
        """Print the document to the specified printer"""
        document = QTextDocument()
        document.setHtml(self.bill_html)
        document.print_(printer)
    
    def save_as_pdf(self):
        """Save the bill as a PDF file"""
        # Get file name from dialog
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Bill as PDF", f"Invoice_{self.sale_id}.pdf", "PDF Files (*.pdf)"
        )
        
        if file_name:
            # Configure printer for PDF output
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_name)
            
            # Create and print document
            document = QTextDocument()
            document.setHtml(self.bill_html)
            document.print_(printer)
            
            # Show success message with file path
            QMessageBox.information(
                self, 
                "PDF Saved", 
                f"Bill has been saved as PDF:\n{file_name}"
            )