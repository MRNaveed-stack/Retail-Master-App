class Product:
    """
    Represents a mattress product in the inventory.
    """
    def __init__(self, key_number, name, purchase_price, total_added, sold=0, 
                 sale_price=None, image_path=None, image_data=None, 
                 category_id=1, category_name="General"):
        self.key_number = key_number
        self.name = name
        self.purchase_price = purchase_price
        self.sale_price = sale_price or (purchase_price * 1.2)  # Default markup
        self.total_added = total_added
        self.sold = sold
        self.image_path = image_path
        self.image_data = image_data
        self.category_id = category_id
        self.category_name = category_name
        
    @property
    def remaining(self):
        """Calculate remaining stock"""
        return self.total_added - self.sold
    
    def __str__(self):
        return f"Product {self.key_number}: {self.name} - {self.remaining} remaining"


class Customer:
    """
    Represents a customer who purchases products.
    """
    def __init__(self, id=None, name="", phone=None, email=None, address=None, created_at=None):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.created_at = created_at
    
    def __str__(self):
        if self.phone:
            return f"{self.name} ({self.phone})"
        return self.name


class Sale:
    """
    Represents a sale transaction.
    """
    def __init__(self, key_number, product_name, quantity, sale_price, sale_date, 
                 purchase_price=None, sale_id=None, category_id=None, category_name=None,
                 customer_id=None, customer_name=None, customer_phone=None):
        self.sale_id = sale_id
        self.key_number = key_number
        self.product_name = product_name
        self.quantity = quantity
        self.sale_price = sale_price
        self.sale_date = sale_date
        self.purchase_price = purchase_price
        self.category_id = category_id
        self.category_name = category_name
        self.customer_id = customer_id
        self.customer_name = customer_name or "Walk-in Customer"
        self.customer_phone = customer_phone or ""
        
    @property
    def total_amount(self):
        """Calculate total sale amount"""
        return self.sale_price * self.quantity
    
    @property
    def profit(self):
        """Calculate profit if purchase price is available"""
        if self.purchase_price is not None:
            return (self.sale_price - self.purchase_price) * self.quantity
        return None
    
    def __str__(self):
        return f"Sale on {self.sale_date}: {self.quantity} x {self.product_name} - ${self.total_amount:.2f}"
        
    def customer_info(self):
        """Return formatted customer information"""
        if self.customer_id and self.customer_name != "Walk-in Customer":
            if self.customer_phone:
                return f"{self.customer_name} ({self.customer_phone})"
            return self.customer_name
        return "Walk-in Customer"


class Category:
    """
    Represents a product category.
    """
    def __init__(self, id, name, description=""):
        self.id = id
        self.name = name
        self.description = description
    
    def __str__(self):
        return f"Category {self.id}: {self.name}"
