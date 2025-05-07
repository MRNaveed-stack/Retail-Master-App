# generate_license.py

from license_validator import generate_license_key

def main():
    customer_id = input("Enter customer ID: ")
    expiry_date = input("Enter expiry date (YYYY-MM-DD): ")
    key = generate_license_key(customer_id, expiry_date)
    print(f"\nGenerated License Key: {key}")
    print("Give this key + customer ID + expiry date to the user.")

if __name__ == "__main__":
    main()
