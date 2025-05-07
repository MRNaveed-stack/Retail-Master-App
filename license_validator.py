import sqlite3
import datetime
from PyQt5.QtWidgets import QApplication, QInputDialog, QMessageBox
from database import DB_PATH  # adjust if your DB_PATH import is different
import hashlib

def generate_license_key(customer_id, expiry_date):
    """Generate a unique license key for a customer."""
    seed = f"{customer_id}-{expiry_date}-SmartRetailApp"
    return hashlib.sha256(seed.encode()).hexdigest()[:16]

def validate_license():
    """Check the stored license against expected key and expiry."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS license (
                key TEXT PRIMARY KEY,
                customer_id TEXT,
                expiry_date TEXT,
                activation_date TEXT
            )
        ''')
        cursor.execute("SELECT key, customer_id, expiry_date FROM license LIMIT 1")
        row = cursor.fetchone()
        if not row:
            return False

        stored_key, customer_id, expiry_date = row
        # expiry check
        if datetime.datetime.now() > datetime.datetime.strptime(expiry_date, "%Y-%m-%d"):
            return False

        expected = generate_license_key(customer_id, expiry_date)
        return stored_key == expected

    finally:
        conn.close()

def register_license():
    """GUI flow to register a new license (ID, date, key)."""
    from PyQt5.QtWidgets import QInputDialog, QMessageBox

    # 1) Customer ID
    cid, ok = QInputDialog.getText(None, "Register License", "Enter Customer ID:")
    if not ok or not cid:
        return False

    # 2) Expiry Date
    exp, ok = QInputDialog.getText(None, "Register License",
                                  "Enter Expiry Date (YYYY-MM-DD):")
    if not ok or not exp:
        return False

    # 3) License Key
    key, ok = QInputDialog.getText(None, "Register License", "Enter License Key:")
    if not ok or not key:
        return False

    # 4) Validate it
    if key.strip() != generate_license_key(cid, exp):
        QMessageBox.critical(None, "Invalid License",
                             "That key does not match this ID and date.")
        return False

    # 5) Store in DB
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM license")
        cursor.execute(
            "INSERT INTO license VALUES (?, ?, ?, ?)",
            (key.strip(), cid, exp, datetime.datetime.now().strftime("%Y-%m-%d"))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        QMessageBox.critical(None, "Error Saving License", str(e))
        return False

    QMessageBox.information(None, "Success", "License registered successfully.")
    return True
