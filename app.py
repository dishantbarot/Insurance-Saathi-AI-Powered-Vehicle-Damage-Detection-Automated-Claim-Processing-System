"""
Insurance Saathi
AI Powered Vehicle Damage Detection & Claim Automation
Production Enhanced Version
"""

# =================================================
# IMPORTS
# =================================================

import streamlit as st
import numpy as np
import sqlite3
import base64
from ultralytics import YOLO
from backend import (
    init_db,
    validate_policy,
    create_claim,
    create_ticket,
    DB_NAME
)
from PIL import Image as PILImage
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors


# =================================================
# PDF FUNCTION
# =================================================

def generate_pdf(claim_id, policy_id, damage_class, confidence,
                 damage_percent, approval_score, claim_status, image):

    pdf_path = f"claim_{claim_id}.pdf"
    doc = SimpleDocTemplate(pdf_path)
    elements = []
    styles = getSampleStyleSheet()

    centered = ParagraphStyle(
        name="Centered",
        parent=styles["Heading1"],
        alignment=1,
        textColor=colors.HexColor("#0A84FF")
    )

    subtitle = ParagraphStyle(
        name="Subtitle",
        parent=styles["Normal"],
        alignment=1,
        textColor=colors.grey
    )

    logo = RLImage("assets/Insurance_saathi logo.png", width=1.5*inch, height=1.5*inch)
    logo.hAlign = 'CENTER'
    elements.append(logo)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Insurance Saathi", centered))
    elements.append(Paragraph("AI Powered Car Insurance Automation System", subtitle))
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(f"<b>Policy ID:</b> {policy_id}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Damage Type:</b> {damage_class}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Model Confidence:</b> {round(confidence*100,2)}%", styles["Normal"]))
    elements.append(Paragraph(f"<b>Damage Coverage:</b> {round(damage_percent,2)}%", styles["Normal"]))
    elements.append(Paragraph(f"<b>Approval Score:</b> {round(approval_score,2)}%", styles["Normal"]))
    elements.append(Paragraph(f"<b>Status:</b> {claim_status}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Claim ID:</b> {claim_id}", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))

    temp_img = f"damage_{claim_id}.jpg"
    image.save(temp_img)

    damage_img = RLImage(temp_img, width=4*inch, height=3*inch)
    damage_img.hAlign = 'CENTER'
    elements.append(damage_img)

    doc.build(elements)

    return pdf_path


# =================================================
# INITIAL SETUP
# =================================================

st.set_page_config(page_title="Insurance Saathi", page_icon="🚗", layout="centered")
init_db()

# Session state
for key in ["policy_valid", "policy_id", "damage_class",
            "confidence", "damage_percent",
            "approval_score", "claim_status", "image"]:
    if key not in st.session_state:
        st.session_state[key] = None

# Sidebar
page = st.sidebar.selectbox("Navigation", ["Insurance Portal", "Admin Dashboard"])

# Load Model
@st.cache_resource
def load_model():
    return YOLO("model/best.pt")

model = load_model()


# =================================================
# INSURANCE PORTAL
# =================================================

if page == "Insurance Portal":

    # Centered Logo
    with open("assets/Insurance_saathi logo.png", "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"<div style='text-align:center;'><img src='data:image/png;base64,{encoded}' width='150'></div>",
        unsafe_allow_html=True
    )

    st.markdown("<h1 style='text-align:center;'>Insurance Saathi</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#00D4FF;'>AI Powered Car Insurance Automation System</p>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # POLICY VALIDATION
    st.subheader("🔎 Policy Verification")
    policy_number = st.text_input("Enter Policy Number")

    if st.button("Validate Policy"):

        valid, result = validate_policy(policy_number)

        if valid:
            st.success("✅ Policy is Valid")

            st.write("**Customer Name:**", result["Customer_Name"])
            st.write("**Vehicle Number:**", result["Vehicle_Number"])
            st.write("**Coverage Type:**", result["Coverage_Type"])
            st.write("**Expiry Date:**", result["Expiry_Date"])
            st.write("**Insured Amount:** ₹", result["Insured_Amount"])

            st.session_state.policy_valid = True
            st.session_state.policy_id = policy_number

        else:
            st.error(result)
            st.session_state.policy_valid = False
            st.session_state.policy_id = None

    # DAMAGE DETECTION
    if st.session_state.policy_valid:

        st.markdown("---")
        st.subheader("📸 Upload Damage Image")

        uploaded_file = st.file_uploader("Upload vehicle damage image", type=["jpg","jpeg","png"])

        if uploaded_file is not None:

            image = PILImage.open(uploaded_file).convert("RGB")
            image_np = np.array(image)

            results = model(image_np)
            result = results[0]

            if result.boxes is not None and len(result.boxes) > 0:

                boxes = result.boxes
                cls_id = int(boxes.cls[0])
                confidence = float(boxes.conf[0])
                class_name = model.names[cls_id]

                st.image(result.plot(), width="stretch")

                # DAMAGE %
                img_h, img_w = image_np.shape[:2]
                total_area = img_h * img_w
                damage_area = 0

                for box in boxes.xyxy:
                    x1, y1, x2, y2 = box
                    damage_area += (x2 - x1) * (y2 - y1)

                damage_percent = float((damage_area / total_area) * 100)

                # CLAIM APPROVAL SCORE
                approval_score = (
                    confidence * 100 * 0.6 +
                    damage_percent * 0.4
                )

                # STATUS LOGIC
                if approval_score >= 70:
                    claim_status = "Approved"
                    badge_color = "green"
                elif approval_score >= 50:
                    claim_status = "Under Review"
                    badge_color = "orange"
                else:
                    claim_status = "Rejected"
                    badge_color = "red"

                # Store session
                st.session_state.damage_class = class_name
                st.session_state.confidence = confidence
                st.session_state.damage_percent = damage_percent
                st.session_state.approval_score = approval_score
                st.session_state.claim_status = claim_status
                st.session_state.image = image

                # DISPLAY
                st.success(f"Damage Detected: {class_name}")
                st.progress(int(confidence*100))
                st.write(f"Model Confidence: {round(confidence*100,2)}%")

                st.progress(int(damage_percent))
                st.write(f"Damage Coverage: {round(damage_percent,2)}%")

                st.progress(int(min(approval_score,100)))
                st.write(f"Claim Approval Score: {round(approval_score,2)}%")

                st.markdown(
                    f"<h3 style='color:{badge_color};'>Status: {claim_status}</h3>",
                    unsafe_allow_html=True
                )

    # CLAIM SUBMISSION
    if (
        st.session_state.policy_valid
        and st.session_state.damage_class is not None
    ):

        st.markdown("---")
        choice = st.radio("Proceed with claim?", ["Select", "Yes", "No"])

        if choice == "Yes":

            if st.button("Submit Claim"):

                claim_id = create_claim(
                    st.session_state.policy_id,
                    st.session_state.damage_class,
                    st.session_state.confidence
                )

                create_ticket(claim_id)

                st.success(f"🎫 Claim Created! ID: {claim_id}")

                pdf_path = generate_pdf(
                    claim_id,
                    st.session_state.policy_id,
                    st.session_state.damage_class,
                    st.session_state.confidence,
                    st.session_state.damage_percent,
                    st.session_state.approval_score,
                    st.session_state.claim_status,
                    st.session_state.image
                )

                with open(pdf_path, "rb") as f:
                    st.download_button("📄 Download Claim Report",
                                       data=f,
                                       file_name=pdf_path,
                                       mime="application/pdf")

        elif choice == "No":
            st.info("Thank you for using Insurance Saathi 🚗")


# =================================================
# ADMIN DASHBOARD
# =================================================

if page == "Admin Dashboard":

    st.title("📊 Admin Dashboard")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM Policy_Master")
    total_policies = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Claims")
    total_claims = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Tickets")
    total_tickets = cursor.fetchone()[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Policies", total_policies)
    col2.metric("Total Claims", total_claims)
    col3.metric("Total Tickets", total_tickets)

    st.markdown("---")

    st.subheader("Claims Table")
    cursor.execute("SELECT * FROM Claims ORDER BY Claim_ID DESC")
    st.dataframe(cursor.fetchall())

    st.subheader("Tickets Table")
    cursor.execute("SELECT * FROM Tickets ORDER BY Ticket_ID DESC")
    st.dataframe(cursor.fetchall())

    conn.close()
