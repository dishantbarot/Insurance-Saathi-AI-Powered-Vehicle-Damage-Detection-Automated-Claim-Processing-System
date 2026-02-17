'''
"""
generate_policies.py

This script generates 1000 synthetic vehicle insurance policies
and inserts them into the Policy_Master table.

Run this only once during initial database setup.
"""

import random
import pyodbc
from faker import Faker
from datetime import datetime, timedelta

# Faker generates realistic dummy names
fake = Faker()

# ---------------------------------------------------------
# Establish SQL Server connection
# ---------------------------------------------------------
# Make sure you have ODBC Driver 17 installed.
# If using Driver 18, replace the driver name accordingly.

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"                 # Change if using SQLEXPRESS
    "DATABASE=VehicleInsuranceDB;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

# ---------------------------------------------------------
# Generate 1000 synthetic policies
# ---------------------------------------------------------
for i in range(1000):

    # Unique policy ID (e.g., POL10000, POL10001...)
    policy_id = f"POL{10000 + i}"

    # Generate random realistic customer name
    customer_name = fake.name()

    # Generate realistic Indian-style vehicle number
    vehicle_number = f"MH{random.randint(10,99)}AB{random.randint(1000,9999)}"

    # Randomly assign coverage type
    coverage_type = random.choice(["Comprehensive", "Third Party"])

    # Random policy start date (between 30–365 days ago)
    start_date = datetime.now() - timedelta(days=random.randint(30, 365))

    # Policy valid for 1 year
    expiry_date = start_date + timedelta(days=365)

    # Random insured amount between 2L – 15L
    insured_amount = random.randint(200000, 1500000)

    # Determine status based on expiry date
    status = "Active" if expiry_date > datetime.now() else "Expired"

    # Insert into SQL table
    cursor.execute("""
        INSERT INTO Policy_Master 
        (Policy_ID, Customer_Name, Vehicle_Number, Coverage_Type,
         Start_Date, Expiry_Date, Insured_Amount, Status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, policy_id, customer_name, vehicle_number, coverage_type,
         start_date, expiry_date, insured_amount, status)

# Commit all inserts
conn.commit()

# Close connection
conn.close()

print("✅ 1000 Policies Inserted Successfully")
'''