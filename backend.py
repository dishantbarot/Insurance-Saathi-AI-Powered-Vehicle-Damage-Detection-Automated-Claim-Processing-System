"""
backend.py

This file contains all database-related business logic functions:
- Database connection
- Policy validation
- Claim creation
- Ticket creation
"""

import pyodbc

# ---------------------------------------------------------
# Database Connection Function
# ---------------------------------------------------------
def get_connection():
    """
    Establishes connection to SQL Server database.
    Returns a connection object.
    """
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=VehicleInsuranceDB;"
        "Trusted_Connection=yes;"
    )


# ---------------------------------------------------------
# Validate Policy
# ---------------------------------------------------------
def validate_policy(policy_id):
    """
    Checks:
    1. If policy exists
    2. If policy is active

    Returns:
    (True, policy_object)  -> if valid
    (False, error_message) -> if invalid
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Policy_Master WHERE Policy_ID = ?", policy_id)
    policy = cursor.fetchone()

    conn.close()

    # If policy does not exist
    if not policy:
        return False, "Policy Not Found"

    # If policy expired
    if policy.Status != "Active":
        return False, "Policy Expired"

    return True, policy


# ---------------------------------------------------------
# Create Claim
# ---------------------------------------------------------
def create_claim(policy_id, damage_class, confidence):
    """
    Inserts a new claim into Claims table.

    Approval logic:
    - If confidence > 0.5 → Approved
    - Else → Under Review

    Returns:
    claim_id (int)
    """

    conn = get_connection()
    cursor = conn.cursor()

    claim_status = "Approved" if confidence > 0.5 else "Under Review"

    cursor.execute("""
        INSERT INTO Claims (Policy_ID, Damage_Class, Confidence, Claim_Status)
        OUTPUT INSERTED.Claim_ID
        VALUES (?, ?, ?, ?)
    """, policy_id, damage_class, confidence, claim_status)

    claim_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return claim_id


# ---------------------------------------------------------
# Create Ticket
# ---------------------------------------------------------
def create_ticket(claim_id):
    """
    Creates a ticket for a claim.
    Assigns to default Claims Officer.

    Returns:
    ticket_id (int)
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Tickets (Claim_ID, Assigned_To, Ticket_Status)
        OUTPUT INSERTED.Ticket_ID
        VALUES (?, ?, ?)
    """, claim_id, "Claims Officer 1", "Open")

    ticket_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return ticket_id
