"""
Insurance Saathi - AI Powered Car Insurance
Streamlit Frontend Application
"""

import streamlit as st
from ultralytics import YOLO
from backend import validate_policy, create_claim, create_ticket
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime
from PIL import Image as PILImage
import numpy as np
import os


# -------------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------------

st.set_page_config(
    page_title="Insurance Saathi",
    page_icon="🚗",
    layout="centered"
)

# -------------------------------------------------------
# CUSTOM CSS (Futuristic + Minimalist)
# -------------------------------------------------------

st.markdown("""
<style>
body {
    background-color: #0E1117;
    color: white;
}
.big-title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
}
.subtitle {
    text-align: center;
    font-size: 18px;
    color: #00D4FF;
}
.section {
    background-color: #161B22;
    padding: 25px;
    border-radius: 12px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# HEADER SECTION
# -------------------------------------------------------

logo = PILImage.open("assets/Insurance_saathi logo.png")
st.image(logo, width=180)

st.markdown("<div class='big-title'>Insurance Saathi</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI Powered Car Insurance Automation System</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------
# LOAD MODEL
# -------------------------------------------------------

@st.cache_resource
def load_model():
    return YOLO("model/best.pt")

model = load_model()

# -------------------------------------------------------
# POLICY VALIDATION SECTION
# -------------------------------------------------------

st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🔎 Policy Verification")

policy_number = st.text_input("Enter Policy Number")

if st.button("Validate Policy"):
    valid, result = validate_policy(policy_number)

    if valid:
        st.success("✅ Policy is Valid")

        st.write("**Customer Name:**", result.Customer_Name)
        st.write("**Vehicle Number:**", result.Vehicle_Number)
        st.write("**Coverage Type:**", result.Coverage_Type)
        st.write("**Expiry Date:**", result.Expiry_Date)
        st.write("**Insured Amount:** ₹", result.Insured_Amount)

        st.session_state["policy_valid"] = True
        st.session_state["policy_id"] = policy_number

    else:
        st.error(result)
        st.session_state["policy_valid"] = False

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------
# DAMAGE DETECTION SECTION
# -------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload vehicle damage image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:

    try:
        image = PILImage.open(uploaded_file).convert("RGB")
        image_np = np.array(image)

        results = model(image_np)
        result = results[0]

        # Check properly
        if result.boxes is not None and len(result.boxes) > 0:

            boxes = result.boxes

            cls_id = int(boxes.cls[0])
            confidence = float(boxes.conf[0])
            class_name = model.names[cls_id]

            st.image(result.plot(), caption="Detected Damage", use_container_width=True)

            st.success(f"Damage Detected: {class_name}")
            st.write(f"Confidence Score: {round(confidence, 2)}")

            st.session_state["damage_class"] = class_name
            st.session_state["confidence"] = confidence

            # -------------------------------------------------------
            # CLAIM DECISION
            # -------------------------------------------------------

            claim_option = st.radio(
                "Do you want to proceed with the claim?",
                ["Yes", "No"]
            )

            if claim_option == "Yes":

                claim_id = create_claim(
                    st.session_state["policy_id"],
                    class_name,
                    confidence
                )

                ticket_id = create_ticket(claim_id)

                st.success(f"🎫 Claim Created Successfully! Claim ID: {claim_id}")

                # -------------------------------------------------------
                # PDF GENERATION
                # -------------------------------------------------------

                pdf_path = f"claim_{claim_id}.pdf"
                doc = SimpleDocTemplate(pdf_path)
                elements = []

                styles = getSampleStyleSheet()

                elements.append(Paragraph("Insurance Saathi - Claim Report", styles["Title"]))
                elements.append(Spacer(1, 0.3 * inch))
                elements.append(Paragraph(f"Policy ID: {st.session_state['policy_id']}", styles["Normal"]))
                elements.append(Paragraph(f"Damage Type: {class_name}", styles["Normal"]))
                elements.append(Paragraph(f"Confidence: {round(confidence,2)}", styles["Normal"]))
                elements.append(Paragraph(f"Claim ID: {claim_id}", styles["Normal"]))
                elements.append(Paragraph(f"Date: {datetime.now()}", styles["Normal"]))

                doc.build(elements)

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📄 Download Claim Report (PDF)",
                        data=f,
                        file_name=pdf_path,
                        mime="application/pdf"
                    )

            else:
                st.info("Thank you for visiting Insurance Saathi 🚗")

        else:
            st.warning("No visible damage detected in the image.")

    except Exception as e:
        st.error("Error processing image.")
        st.exception(e)

    st.markdown("</div>", unsafe_allow_html=True)
