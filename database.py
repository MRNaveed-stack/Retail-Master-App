import os
import sqlite3
from datetime import datetime
import base64

# Database file path
DB_PATH = "mattress_shop.db"

def get_connection():
    """
    Create and return a connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def check_and_update_schema():
    """
    Check if the database schema is up to date and migrate if needed.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if the 'categories' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
    if not cursor.fetchone():
        # Create categories table
        print("Migrating database: Adding categories table")
        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
            ''')
            
            # Insert default category
            cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", 
                          ("General", "Default category for all products"))
            conn.commit()
            print("Categories table created")
        except Exception as e:
            print(f"Migration error (categories): {e}")
            conn.rollback()
    
    # Check if category_id column exists in products table
    cursor.execute("PRAGMA table_info(products)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "category_id" not in columns:
        print("Migrating database: Adding category_id column to products table")
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN category_id INTEGER DEFAULT 1 REFERENCES categories(id)")
            conn.commit()
            print("Added category_id column")
        except Exception as e:
            print(f"Migration error (category_id): {e}")
            conn.rollback()
    
    # Check if image_data column exists in products table
    if "image_data" not in columns:
        print("Migrating database: Adding image_data column to products table")
        try:
            cursor.execute("ALTER TABLE products ADD COLUMN image_data TEXT")
            conn.commit()
            print("Added image_data column")
        except Exception as e:
            print(f"Migration error (image_data): {e}")
            conn.rollback()
    
    # Check if the customers table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
    if not cursor.fetchone():
        print("Migrating database: Adding customers table")
        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TEXT
            )
            ''')
            conn.commit()
            print("Customers table created")
        except Exception as e:
            print(f"Migration error (customers): {e}")
            conn.rollback()
    
    # Check if customer_id column exists in sales table
    cursor.execute("PRAGMA table_info(sales)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "customer_id" not in columns:
        print("Migrating database: Adding customer_id column to sales table")
        try:
            cursor.execute("ALTER TABLE sales ADD COLUMN customer_id INTEGER REFERENCES customers(id)")
            conn.commit()
            print("Added customer_id column to sales table")
        except Exception as e:
            print(f"Migration error (customer_id): {e}")
            conn.rollback()
    
    conn.close()

def create_database():
    """
    Create the database and necessary tables if they don't exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    )
    ''')
    
    # Insert default category if it doesn't exist
    cursor.execute("SELECT id FROM categories WHERE name = 'General'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", 
                      ("General", "Default category for all products"))
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        key_number INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        purchase_price REAL NOT NULL,
        sale_price REAL NOT NULL,
        total_added INTEGER NOT NULL,
        sold INTEGER DEFAULT 0,
        image_path TEXT,
        image_data TEXT,
        category_id INTEGER DEFAULT 1,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    ''')
    
    # Create customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        address TEXT,
        created_at TEXT
    )
    ''')
    
    # Create sales table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_number INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        sale_price REAL NOT NULL,
        sale_date TEXT NOT NULL,
        profit REAL NOT NULL,
        customer_id INTEGER,
        FOREIGN KEY (key_number) REFERENCES products (key_number),
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    # Check if we need to migrate existing data
    check_and_update_schema()

def get_all_categories():
    """
    Retrieve all product categories.
    
    Returns:
        list: List of category dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, description FROM categories ORDER BY name")
    
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return categories

def get_category_by_id(category_id):
    """
    Retrieve a category by its ID.
    
    Args:
        category_id (int): The category ID
        
    Returns:
        dict: Category information or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, description FROM categories WHERE id = ?", (category_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def add_category(name, description=""):
    """
    Add a new category.
    
    Args:
        name (str): Category name
        description (str): Category description
        
    Returns:
        int: New category ID or None if error
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO categories (name, description) VALUES (?, ?)",
            (name, description)
        )
        conn.commit()
        new_id = cursor.lastrowid
        return new_id
    except sqlite3.IntegrityError:
        # Category name already exists
        return None
    finally:
        conn.close()

def update_category(category_id, name, description):
    """
    Update an existing category.
    
    Args:
        category_id (int): The category ID to update
        name (str): New category name
        description (str): New category description
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE categories SET name = ?, description = ? WHERE id = ?",
            (name, description, category_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.IntegrityError:
        # Category name already exists
        return False
    finally:
        conn.close()

def delete_category(category_id):
    """
    Delete a category, moving all products to the default category.
    
    Args:
        category_id (int): The category ID to delete
        
    Returns:
        bool: True if successful
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Don't allow deleting the default category (ID 1)
        if category_id == 1:
            return False
            
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Move all products in this category to the default category
        cursor.execute(
            "UPDATE products SET category_id = 1 WHERE category_id = ?",
            (category_id,)
        )
        
        # Delete the category
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error deleting category: {e}")
        return False
    finally:
        conn.close()

def add_product(key_number, name, purchase_price, sale_price, total_added, category_id=1, image_path=None, image_data=None):
    """
    Add a new product to the database.
    
    Args:
        key_number (int): Unique identifier for the product
        name (str): Name of the product
        purchase_price (float): Price paid to wholesaler
        sale_price (float): Price to be charged to customers
        total_added (int): Total quantity initially added
        category_id (int): Category ID the product belongs to
        image_path (str, optional): Path to the image file
        image_data (str, optional): Base64 encoded image data
        
    Returns:
        bool: True if successful, False if key_number already exists
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO products (key_number, name, purchase_price, sale_price, total_added, category_id, image_path, image_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (key_number, name, purchase_price, sale_price, total_added, category_id, image_path, image_data)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Key number already exists
        return False
    finally:
        conn.close()

def update_product(key_number, name=None, purchase_price=None, sale_price=None, category_id=None):
    """
    Update an existing product's details.
    
    Args:
        key_number (int): The key number of the product to update
        name (str, optional): New product name
        purchase_price (float, optional): New purchase price
        sale_price (float, optional): New sale price
        category_id (int, optional): New category ID
        
    Returns:
        bool: True if successful, False if product not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build update query dynamically based on provided parameters
    query_parts = []
    params = []
    
    if name is not None:
        query_parts.append("name = ?")
        params.append(name)
    
    if purchase_price is not None:
        query_parts.append("purchase_price = ?")
        params.append(purchase_price)
    
    if sale_price is not None:
        query_parts.append("sale_price = ?")
        params.append(sale_price)
    
    if category_id is not None:
        query_parts.append("category_id = ?")
        params.append(category_id)
    
    if not query_parts:
        return False  # Nothing to update
    
    # Complete the query
    query = f"UPDATE products SET {', '.join(query_parts)} WHERE key_number = ?"
    params.append(key_number)
    
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating product: {e}")
        return False
    finally:
        conn.close()

def get_all_products():
    """
    Retrieve all products from the database.
    
    Returns:
        list: List of product dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT p.key_number, p.name, p.purchase_price, p.sale_price, p.total_added, p.sold, 
           (p.total_added - p.sold) as remaining, p.image_path, p.image_data, p.category_id,
           c.name as category_name
    FROM products p
    JOIN categories c ON p.category_id = c.id
    ORDER BY p.key_number
    """)
    
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return products

def get_products_by_category(category_id):
    """
    Retrieve all products in a specific category.
    
    Args:
        category_id (int): The category ID to filter by
        
    Returns:
        list: List of product dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT p.key_number, p.name, p.purchase_price, p.sale_price, p.total_added, p.sold, 
           (p.total_added - p.sold) as remaining, p.image_path, p.image_data, p.category_id,
           c.name as category_name
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE p.category_id = ?
    ORDER BY p.key_number
    """, (category_id,))
    
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return products

def get_product_by_key(key_number):
    """
    Retrieve a product by its key number.
    
    Args:
        key_number (int): The key number to search for
        
    Returns:
        dict: Product information or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT p.key_number, p.name, p.purchase_price, p.sale_price, p.total_added, p.sold, 
           (p.total_added - p.sold) as remaining, p.image_path, p.image_data, p.category_id,
           c.name as category_name
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE p.key_number = ?
    """, (key_number,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def search_products(search_term):
    """
    Search for products by key number or name.
    
    Args:
        search_term (str): The search term
        
    Returns:
        list: Matching products
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Try to convert search term to integer for key number search
    try:
        key_number = int(search_term)
        key_search = f"p.key_number = {key_number}"
    except ValueError:
        key_search = "0"  # No match possible for key if not an integer
    
    cursor.execute(f"""
    SELECT p.key_number, p.name, p.purchase_price, p.sale_price, p.total_added, p.sold, 
           (p.total_added - p.sold) as remaining, p.image_path, p.image_data, p.category_id,
           c.name as category_name
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE {key_search} OR p.name LIKE ?
    ORDER BY p.key_number
    """, (f"%{search_term}%",))
    
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return products

def update_product_image(key_number, image_path=None, image_data=None):
    """
    Update the image for a product.
    
    Args:
        key_number (int): The key number of the product
        image_path (str, optional): Path to the product image
        image_data (str, optional): Base64 encoded image data
        
    Returns:
        bool: True if successful, False if product not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE products SET image_path = ?, image_data = ? WHERE key_number = ?",
            (image_path, image_data, key_number)
        )
        conn.commit()
        # Check if any row was updated
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating product image: {e}")
        return False
    finally:
        conn.close()

def add_customer(name, phone=None, email=None, address=None):
    """
    Add a new customer to the database.
    
    Args:
        name (str): Customer name
        phone (str, optional): Customer phone number
        email (str, optional): Customer email address
        address (str, optional): Customer address
        
    Returns:
        int: New customer ID or None if error
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Make sure the customers table exists
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            created_at TEXT
        )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Error ensuring customers table exists: {e}")
    
    try:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Adding customer: {name}, {phone}, {email}, {address}, {created_at}")
        cursor.execute(
            "INSERT INTO customers (name, phone, email, address, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, phone, email, address, created_at)
        )
        conn.commit()
        new_id = cursor.lastrowid
        print(f"Added customer with ID: {new_id}")
        return new_id
    except Exception as e:
        print(f"Error adding customer: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_customer_by_id(customer_id):
    """
    Retrieve a customer by their ID.
    
    Args:
        customer_id (int): The customer ID
        
    Returns:
        dict: Customer information or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, phone, email, address, created_at FROM customers WHERE id = ?", (customer_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def get_all_customers():
    """
    Retrieve all customers from the database.
    
    Returns:
        list: List of customer dictionaries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, phone, email, address, created_at FROM customers ORDER BY name")
    
    customers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return customers

def search_customers(search_term):
    """
    Search for customers by name or phone number.
    
    Args:
        search_term (str): The search term
        
    Returns:
        list: Matching customers
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, name, phone, email, address, created_at 
    FROM customers
    WHERE name LIKE ? OR phone LIKE ?
    ORDER BY name
    """, (f"%{search_term}%", f"%{search_term}%"))
    
    customers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return customers

def record_sale(key_number, quantity, sale_price, customer_id=None):
    """
    Record a sale in the database and update inventory.
    
    Args:
        key_number (int): Product key number
        quantity (int): Quantity sold
        sale_price (float): Price per unit
        customer_id (int, optional): Customer ID for this sale
        
    Returns:
        int: Sale ID if successful, None otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Start a transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Get product details
        cursor.execute("SELECT purchase_price, (total_added - sold) as remaining FROM products WHERE key_number = ?", 
                      (key_number,))
        product = cursor.fetchone()
        
        if not product or product["remaining"] < quantity:
            conn.rollback()
            return None
        
        # Calculate profit
        purchase_price = product["purchase_price"]
        profit = (sale_price - purchase_price) * quantity
        sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Record the sale
        if customer_id:
            cursor.execute(
                "INSERT INTO sales (key_number, quantity, sale_price, sale_date, profit, customer_id) VALUES (?, ?, ?, ?, ?, ?)",
                (key_number, quantity, sale_price, sale_date, profit, customer_id)
            )
        else:
            cursor.execute(
                "INSERT INTO sales (key_number, quantity, sale_price, sale_date, profit) VALUES (?, ?, ?, ?, ?)",
                (key_number, quantity, sale_price, sale_date, profit)
            )
        
        sale_id = cursor.lastrowid
        
        # Update the inventory
        cursor.execute(
            "UPDATE products SET sold = sold + ? WHERE key_number = ?",
            (quantity, key_number)
        )
        
        conn.commit()
        return sale_id
    except Exception as e:
        conn.rollback()
        print(f"Error recording sale: {e}")
        return None
    finally:
        conn.close()

def get_sales_history():
    """
    Retrieve all sales history.
    
    Returns:
        list: List of sales records
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT s.id, s.key_number, p.name, p.category_id, c.name as category_name,
           s.quantity, s.sale_price, s.sale_date, s.profit, p.purchase_price,
           s.customer_id, IFNULL(cust.name, 'Walk-in Customer') as customer_name,
           IFNULL(cust.phone, '') as customer_phone
    FROM sales s
    JOIN products p ON s.key_number = p.key_number
    JOIN categories c ON p.category_id = c.id
    LEFT JOIN customers cust ON s.customer_id = cust.id
    ORDER BY s.sale_date DESC
    """)
    
    sales = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return sales

def get_sales_by_customer(customer_id):
    """
    Retrieve sales history for a specific customer.
    
    Args:
        customer_id (int): The customer ID
        
    Returns:
        list: List of sales records for the customer
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT s.id, s.key_number, p.name, p.category_id, c.name as category_name,
           s.quantity, s.sale_price, s.sale_date, s.profit, p.purchase_price,
           s.customer_id, cust.name as customer_name, cust.phone as customer_phone
    FROM sales s
    JOIN products p ON s.key_number = p.key_number
    JOIN categories c ON p.category_id = c.id
    JOIN customers cust ON s.customer_id = cust.id
    WHERE s.customer_id = ?
    ORDER BY s.sale_date DESC
    """, (customer_id,))
    
    sales = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return sales

def get_sale_details(sale_id):
    """
    Get detailed information about a specific sale, including customer info.
    
    Args:
        sale_id (int): The sale ID
        
    Returns:
        dict: Sale details or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT s.id, s.key_number, p.name as product_name, p.category_id, 
           c.name as category_name, s.quantity, s.sale_price, 
           (s.quantity * s.sale_price) as total_amount,
           s.sale_date, s.profit, p.purchase_price,
           s.customer_id, IFNULL(cust.name, 'Walk-in Customer') as customer_name,
           IFNULL(cust.phone, '') as customer_phone,
           IFNULL(cust.email, '') as customer_email,
           IFNULL(cust.address, '') as customer_address
    FROM sales s
    JOIN products p ON s.key_number = p.key_number
    JOIN categories c ON p.category_id = c.id
    LEFT JOIN customers cust ON s.customer_id = cust.id
    WHERE s.id = ?
    """, (sale_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def generate_bill_data(sale_id):
    """
    Generate data for a bill based on a sale ID.
    
    Args:
        sale_id (int): The sale ID
        
    Returns:
        dict: Bill data including sale, product, and customer information
    """
    sale_details = get_sale_details(sale_id)
    if not sale_details:
        return None
    
    # Format date for printing
    sale_date = datetime.strptime(sale_details["sale_date"], "%Y-%m-%d %H:%M:%S")
    formatted_date = sale_date.strftime("%d-%m-%Y %I:%M %p")
    
    bill_data = {
        "sale_id": sale_id,
        "bill_date": formatted_date,
        "customer": {
            "name": sale_details["customer_name"],
            "phone": sale_details["customer_phone"],
            "email": sale_details["customer_email"],
            "address": sale_details["customer_address"]
        },
        "product": {
            "name": sale_details["product_name"],
            "key_number": sale_details["key_number"],
            "category": sale_details["category_name"],
            "unit_price": sale_details["sale_price"]
        },
        "quantity": sale_details["quantity"],
        "total_amount": sale_details["total_amount"]
    }
    
    return bill_data

def get_sales_by_category(category_id):
    """
    Retrieve sales history for a specific category.
    
    Args:
        category_id (int): The category ID
        
    Returns:
        list: List of sales records for the category
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT s.id, s.key_number, p.name, p.category_id, c.name as category_name,
           s.quantity, s.sale_price, s.sale_date, s.profit, p.purchase_price,
           s.customer_id, IFNULL(cust.name, 'Walk-in Customer') as customer_name,
           IFNULL(cust.phone, '') as customer_phone
    FROM sales s
    JOIN products p ON s.key_number = p.key_number
    JOIN categories c ON p.category_id = c.id
    LEFT JOIN customers cust ON s.customer_id = cust.id
    WHERE p.category_id = ?
    ORDER BY s.sale_date DESC
    """, (category_id,))
    
    sales = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return sales

def get_total_profit():
    """
    Calculate the total profit from all sales.
    
    Returns:
        float: Total profit
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(profit) as total_profit FROM sales")
    result = cursor.fetchone()
    conn.close()
    
    return result["total_profit"] if result and result["total_profit"] else 0.0

def get_total_profit_by_category(category_id):
    """
    Calculate the total profit from sales in a specific category.
    
    Args:
        category_id (int): The category ID
        
    Returns:
        float: Total profit for the category
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT SUM(s.profit) as total_profit
    FROM sales s
    JOIN products p ON s.key_number = p.key_number
    WHERE p.category_id = ?
    """, (category_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result["total_profit"] if result and result["total_profit"] else 0.0

def delete_product(key_number):
    """
    Delete a product from the database.
    
    Args:
        key_number (int): The key number of the product to delete
        
    Returns:
        bool: True if successful, False if product not found or has sales
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if there are sales for this product
        cursor.execute("SELECT COUNT(*) FROM sales WHERE key_number = ?", (key_number,))
        sales_count = cursor.fetchone()[0]
        
        if sales_count > 0:
            # Product has sales records, can't delete
            return False
        
        # Delete the product
        cursor.execute("DELETE FROM products WHERE key_number = ?", (key_number,))
        conn.commit()
        
        # Check if any row was deleted
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error deleting product: {e}")
        return False
    finally:
        conn.close()

def delete_sale(sale_id):
    """
    Delete a sale record and update inventory accordingly.
    
    Args:
        sale_id (int): The ID of the sale to delete
        
    Returns:
        bool: True if successful, False if sale not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Start a transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Get sale details before deleting
        cursor.execute(
            "SELECT key_number, quantity FROM sales WHERE id = ?", 
            (sale_id,)
        )
        sale = cursor.fetchone()
        
        if not sale:
            conn.rollback()
            return False
        
        product_key, quantity = sale["key_number"], sale["quantity"]
        
        # Delete the sale
        cursor.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
        
        if cursor.rowcount > 0:
            # Update product inventory (reduce sold quantity)
            cursor.execute(
                "UPDATE products SET sold = sold - ? WHERE key_number = ?",
                (quantity, product_key)
            )
            
            conn.commit()
            return True
        else:
            conn.rollback()
            return False
    except Exception as e:
        conn.rollback()
        print(f"Error deleting sale: {e}")
        return False
    finally:
        conn.close()

def clear_sales_history():
    """
    Clear all sales history and reset product sold counts.
    
    Returns:
        int: Number of sales records deleted
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Start a transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Count sales records before deletion
        cursor.execute("SELECT COUNT(*) FROM sales")
        sales_count = cursor.fetchone()[0]
        
        # Delete all sales
        cursor.execute("DELETE FROM sales")
        
        # Reset sold counts for all products
        cursor.execute("UPDATE products SET sold = 0")
        
        conn.commit()
        return sales_count
    except Exception as e:
        conn.rollback()
        print(f"Error clearing sales history: {e}")
        return 0
    finally:
        conn.close()
