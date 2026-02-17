"""
Insurance Saathi
AI Powered Vehicle Damage Detection & Claim Automation
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

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors


# =================================================
# PDF FUNCTION (DEFINED FIRST TO AVOID NameError)
# =================================================

def generate_pdf(claim_id, policy_id, damage_class, confidence, image):

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

    # Centered Logo
    logo = RLImage("assets/Insurance_saathi logo.png", width=1.5*inch, height=1.5*inch)
    logo.hAlign = 'CENTER'
    elements.append(logo)
    elements.append(Spacer(1, 0.3 * inch))

    # Title & Subtitle
    elements.append(Paragraph("Insurance Saathi", centered))
    elements.append(Paragraph("AI Powered Car Insurance Automation System", subtitle))
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph(f"<b>Policy ID:</b> {policy_id}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Damage Type:</b> {damage_class}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Confidence:</b> {round(confidence,2)}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Claim ID:</b> {claim_id}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}", styles["Normal"]))
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

init_db()  # Auto-create SQLite DB & policies


# =================================================
# SESSION STATE INITIALIZATION
# =================================================

if "policy_valid" not in st.session_state:
    st.session_state.policy_valid = False

if "policy_id" not in st.session_state:
    st.session_state.policy_id = None

if "damage_class" not in st.session_state:
    st.session_state.damage_class = None

if "confidence" not in st.session_state:
    st.session_state.confidence = None

if "image" not in st.session_state:
    st.session_state.image = None


# =================================================
# SIDEBAR NAVIGATION
# =================================================

page = st.sidebar.selectbox("Navigation", ["Insurance Portal", "Admin Dashboard"])


# =================================================
# LOAD YOLO MODEL
# =================================================

@st.cache_resource
def load_model():
    return YOLO("model/best.pt")

model = load_model()


# =================================================
# INSURANCE PORTAL
# =================================================

if page == "Insurance Portal":

    # ---------------- CENTERED LOGO ----------------

    with open("assets/Insurance_saathi logo.png", "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <div style='text-align: center;'>
            <img src='data:image/png;base64,{encoded}' width='150'/>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h1 style='text-align:center;'>Insurance Saathi</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#00D4FF;'>AI Powered Car Insurance Automation System</p>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ---------------- POLICY VALIDATION ----------------

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


    # ---------------- DAMAGE DETECTION ----------------

    if st.session_state.policy_valid:

        st.markdown("---")
        st.subheader("📸 Upload Damage Image")

        uploaded_file = st.file_uploader("Upload vehicle damage image", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:

            try:
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

                    st.success(f"Damage Detected: {class_name}")
                    st.write(f"Confidence Score: {round(confidence, 2)}")

                    st.session_state.damage_class = class_name
                    st.session_state.confidence = confidence
                    st.session_state.image = image

                else:
                    st.warning("No visible damage detected.")

            except Exception as e:
                st.error("Error processing image.")
                st.exception(e)


    # ---------------- CLAIM DECISION ----------------

    if (
        st.session_state.policy_valid
        and st.session_state.policy_id is not None
        and st.session_state.damage_class is not None
    ):

        st.markdown("---")
        st.subheader("📝 Claim Decision")

        choice = st.radio("Proceed with claim?", ["Select", "Yes", "No"])

        if choice == "Yes":

            if st.button("Submit Claim"):

                claim_id = create_claim(
                    st.session_state.policy_id,
                    st.session_state.damage_class,
                    st.session_state.confidence
                )

                create_ticket(claim_id)

                st.success(f"🎫 Claim Created Successfully! Claim ID: {claim_id}")

                pdf_path = generate_pdf(
                    claim_id,
                    st.session_state.policy_id,
                    st.session_state.damage_class,
                    st.session_state.confidence,
                    st.session_state.image
                )

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📄 Download Claim Report",
                        data=f,
                        file_name=pdf_path,
                        mime="application/pdf"
                    )

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
