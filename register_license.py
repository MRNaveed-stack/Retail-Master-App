import sqlite3
from license_validator import generate_license_key
from database import DB_PATH

# Define your values
customer_id = "user123"
expiry_date = "2025-12-31"
license_key = generate_license_key(customer_id, expiry_date)

# Store in database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS license
                 (key TEXT PRIMARY KEY, customer_id TEXT, 
                  expiry_date TEXT, activation_date TEXT)''')

cursor.execute("DELETE FROM license")  # Optional: clear old license
cursor.execute("INSERT INTO license (key, customer_id, expiry_date, activation_date) VALUES (?, ?, ?, DATE('now'))",
               (license_key, customer_id, expiry_date))

conn.commit()
conn.close()

print("License registered successfully.")
print(DB_PATH)
