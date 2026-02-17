"""
backend.py
SQLite-based backend for Insurance Saathi
Fully cloud deployable
"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "insurance.db"


# -----------------------------
# DATABASE INITIALIZATION
# -----------------------------

def init_db():
    """
    Creates tables if they do not exist
    and populates 1000 policies (only once)
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create Policy table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Policy_Master (
            Policy_ID TEXT PRIMARY KEY,
            Customer_Name TEXT,
            Vehicle_Number TEXT,
            Coverage_Type TEXT,
            Start_Date TEXT,
            Expiry_Date TEXT,
            Insured_Amount REAL,
            Status TEXT
        )
    """)

    # Create Claims table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Claims (
            Claim_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Policy_ID TEXT,
            Damage_Class TEXT,
            Confidence REAL,
            Claim_Status TEXT,
            Created_At TEXT
        )
    """)

    # Create Tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tickets (
            Ticket_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Claim_ID INTEGER,
            Assigned_To TEXT,
            Ticket_Status TEXT,
            Created_At TEXT
        )
    """)

    # Check if policies already exist
    cursor.execute("SELECT COUNT(*) FROM Policy_Master")
    count = cursor.fetchone()[0]

    if count == 0:
        generate_policies(cursor)

    conn.commit()
    conn.close()


# -----------------------------
# GENERATE 1000 POLICIES
# -----------------------------

def generate_policies(cursor):

    for i in range(1000):

        policy_id = f"POL{10000 + i}"
        customer_name = f"Customer_{i+1}"
        vehicle_number = f"MH{random.randint(10,99)}AB{random.randint(1000,9999)}"
        coverage_type = random.choice(["Comprehensive", "Third Party"])

        start_date = datetime.now() - timedelta(days=random.randint(30, 365))
        expiry_date = start_date + timedelta(days=365)

        insured_amount = random.randint(200000, 1500000)
        status = "Active" if expiry_date > datetime.now() else "Expired"

        cursor.execute("""
            INSERT INTO Policy_Master
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            policy_id,
            customer_name,
            vehicle_number,
            coverage_type,
            start_date.strftime("%Y-%m-%d"),
            expiry_date.strftime("%Y-%m-%d"),
            insured_amount,
            status
        ))


# -----------------------------
# VALIDATE POLICY
# -----------------------------

def validate_policy(policy_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM Policy_Master WHERE Policy_ID = ?",
        (policy_id,)
    )

    policy = cursor.fetchone()
    conn.close()

    if not policy:
        return False, "Policy Not Found"

    if policy[7] != "Active":
        return False, "Policy Expired"

    # Convert tuple to object-like dict
    policy_data = {
        "Customer_Name": policy[1],
        "Vehicle_Number": policy[2],
        "Coverage_Type": policy[3],
        "Start_Date": policy[4],
        "Expiry_Date": policy[5],
        "Insured_Amount": policy[6]
    }

    return True, policy_data


# -----------------------------
# CREATE CLAIM
# -----------------------------

def create_claim(policy_id, damage_class, confidence):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    claim_status = "Approved" if confidence > 0.5 else "Under Review"

    cursor.execute("""
        INSERT INTO Claims
        (Policy_ID, Damage_Class, Confidence, Claim_Status, Created_At)
        VALUES (?, ?, ?, ?, ?)
    """, (
        policy_id,
        damage_class,
        confidence,
        claim_status,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    claim_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return claim_id


# -----------------------------
# CREATE TICKET
# -----------------------------

def create_ticket(claim_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Tickets
        (Claim_ID, Assigned_To, Ticket_Status, Created_At)
        VALUES (?, ?, ?, ?)
    """, (
        claim_id,
        "Claims Officer 1",
        "Open",
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    ticket_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return ticket_id
