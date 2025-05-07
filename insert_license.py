import sqlite3
from database import DB_PATH

# License info
license_key = "309e6932ec18f63e"
customer_id = "user123"
expiry_date = "2025-12-31"
activation_date = "2024-04-20"  # use today's date

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS license (
    key TEXT PRIMARY KEY,
    customer_id TEXT,
    expiry_date TEXT,
    activation_date TEXT
)''')

# Insert the license key
cursor.execute("DELETE FROM license")  # clear previous if any
cursor.execute("INSERT INTO license VALUES (?, ?, ?, ?)",
               (license_key, customer_id, expiry_date, activation_date))

# Save and close
conn.commit()
conn.close()

print("✅ License key inserted successfully.")
