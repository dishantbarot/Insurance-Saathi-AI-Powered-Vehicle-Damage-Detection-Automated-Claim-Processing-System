"""
Insurance Saathi
AI Powered Car Insurance Automation System
Streamlit Application
"""

# -------------------------
# IMPORT LIBRARIES
# -------------------------

import streamlit as st
import numpy as np
from ultralytics import YOLO
from backend import validate_policy, create_claim, create_ticket
from PIL import Image as PILImage
from datetime import datetime

# PDF generation imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors


# -------------------------
# PAGE CONFIGURATION
# -------------------------

st.set_page_config(
    page_title="Insurance Saathi",
    page_icon="🚗",
    layout="centered"
)


# -------------------------
# HEADER SECTION (Centered Logo + Title)
# -------------------------

col1, col2, col3 = st.columns([1,2,1])

with col2:
    logo = PILImage.open("assets/Insurance_saathi logo.png")
    st.image(logo, width=150)

st.markdown(
    "<h1 style='text-align: center;'>Insurance Saathi</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center; color:#00D4FF;'>AI Powered Car Insurance Automation System</p>",
    unsafe_allow_html=True
)

st.markdown("---")


# -------------------------
# LOAD YOLO MODEL (cached)
# -------------------------

@st.cache_resource
def load_model():
    return YOLO("model/best.pt")

model = load_model()


# -------------------------
# POLICY VERIFICATION
# -------------------------

st.subheader("🔎 Policy Verification")

policy_number = st.text_input("Enter Policy Number")

if st.button("Validate Policy"):

    valid, result = validate_policy(policy_number)

    if valid:
        st.success("✅ Policy is Valid")

        # Display policy details
        st.write("**Customer Name:**", result.Customer_Name)
        st.write("**Vehicle Number:**", result.Vehicle_Number)
        st.write("**Coverage Type:**", result.Coverage_Type)
        st.write("**Expiry Date:**", result.Expiry_Date)
        st.write("**Insured Amount:** ₹", result.Insured_Amount)

        # Store in session
        st.session_state["policy_valid"] = True
        st.session_state["policy_id"] = policy_number

    else:
        st.error(result)
        st.session_state["policy_valid"] = False


# -------------------------
# DAMAGE DETECTION SECTION
# -------------------------

if st.session_state.get("policy_valid", False):

    st.markdown("---")
    st.subheader("📸 Upload Damage Image")

    uploaded_file = st.file_uploader(
        "Upload vehicle damage image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is not None:

        try:
            # Convert uploaded file to PIL image
            image = PILImage.open(uploaded_file).convert("RGB")

            # Convert to numpy array for YOLO
            image_np = np.array(image)

            # Run YOLO inference
            results = model(image_np)
            result = results[0]

            # Check if detections exist
            if result.boxes is not None and len(result.boxes) > 0:

                boxes = result.boxes
                cls_id = int(boxes.cls[0])
                confidence = float(boxes.conf[0])
                class_name = model.names[cls_id]

                # Show detection result
                st.image(result.plot(), caption="Detected Damage", use_container_width=True)

                st.success(f"Damage Detected: {class_name}")
                st.write(f"Confidence Score: {round(confidence, 2)}")

                # Store detection result
                st.session_state["damage_class"] = class_name
                st.session_state["confidence"] = confidence
                st.session_state["image"] = image

            else:
                st.warning("No visible damage detected.")

        except Exception as e:
            st.error("Error processing image.")
            st.exception(e)


# -------------------------
# CLAIM DECISION SECTION
# -------------------------

if "damage_class" in st.session_state:

    st.markdown("---")
    st.subheader("📝 Claim Decision")

    claim_choice = st.radio(
        "Do you want to proceed with the claim?",
        ["Select", "Yes", "No"]
    )

    if claim_choice == "Yes":

        if st.button("Submit Claim"):

            # Create claim record
            claim_id = create_claim(
                st.session_state["policy_id"],
                st.session_state["damage_class"],
                st.session_state["confidence"]
            )

            # Create ticket record
            ticket_id = create_ticket(claim_id)

            st.success(f"🎫 Claim Created Successfully! Claim ID: {claim_id}")

            # Generate PDF
            generate_pdf(
                claim_id,
                st.session_state["policy_id"],
                st.session_state["damage_class"],
                st.session_state["confidence"],
                st.session_state["image"]
            )

    elif claim_choice == "No":
        st.info("Thank you for using Insurance Saathi 🚗")


# -------------------------
# PDF GENERATION FUNCTION
# -------------------------

def generate_pdf(claim_id, policy_id, damage_class, confidence, image):

    pdf_path = f"claim_{claim_id}.pdf"
    doc = SimpleDocTemplate(pdf_path)
    elements = []

    styles = getSampleStyleSheet()

    # Centered title style
    centered = ParagraphStyle(
        name="Centered",
        parent=styles["Heading1"],
        alignment=1,
        textColor=colors.HexColor("#0A84FF")
    )

    subtitle_style = ParagraphStyle(
        name="Subtitle",
        parent=styles["Normal"],
        alignment=1,
        textColor=colors.grey
    )

    # Add Logo
    logo = RLImage("assets/Insurance_saathi logo.png", width=1.5*inch, height=1.5*inch)
    logo.hAlign = 'CENTER'
    elements.append(logo)
    elements.append(Spacer(1, 0.3 * inch))

    # Title + Subtitle
    elements.append(Paragraph("Insurance Saathi", centered))
    elements.append(Paragraph("AI Powered Car Insurance Automation System", subtitle_style))
    elements.append(Spacer(1, 0.5 * inch))

    # Policy Details
    elements.append(Paragraph(f"<b>Policy ID:</b> {policy_id}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Damage Type:</b> {damage_class}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Confidence:</b> {round(confidence,2)}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Claim ID:</b> {claim_id}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))

    # Save image temporarily
    temp_img_path = f"damage_{claim_id}.jpg"
    image.save(temp_img_path)

    damage_img = RLImage(temp_img_path, width=4*inch, height=3*inch)
    damage_img.hAlign = 'CENTER'
    elements.append(damage_img)

    doc.build(elements)

    with open(pdf_path, "rb") as f:
        st.download_button(
            "📄 Download Claim Report",
            data=f,
            file_name=pdf_path,
            mime="application/pdf"
        )
