# 🚗 Insurance Saathi  
## AI-Powered Vehicle Damage Detection & Automated Claim Processing System

---

## 🌟 Overview

Insurance Saathi is an end-to-end AI-driven car insurance automation platform that detects vehicle damage from images and automates the insurance claim workflow using deep learning and database-backed logic.

This project simulates a real-world production insurance system with:

- 🔍 AI-based vehicle damage detection (YOLOv8)
- 🧾 Policy validation system
- 🎫 Automated claim & ticket creation
- 📄 Professional PDF claim report generation
- 📊 Admin dashboard with live KPIs
- ☁️ Fully cloud-deployable architecture

---

# ⭐ STAR Format Project Description

---

## 🟢 S — Situation

Manual vehicle insurance claim processing is:

- Time-consuming  
- Human-dependent  
- Error-prone  
- Operationally expensive  

Insurance companies require intelligent automation systems that can reduce claim processing time and improve operational efficiency.

---

## 🟢 T — Task

Build a production-style AI-powered system that:

- Detects vehicle damage from uploaded images  
- Validates insurance policies  
- Automatically generates claims  
- Creates processing tickets  
- Produces professional claim reports  
- Provides an administrative dashboard  
- Is deployable on cloud infrastructure  

---

## 🟢 A — Action

### 1️ Deep Learning Model

- Trained a **YOLOv8 object detection model**
- Used vehicle damage dataset
- Multi-class detection:
  - Dent
  - Scratch
  - Broken glass
  - Paint damage
  - Structural damage
- Optimized for GPU inference (Tesla T4)

---

### 2️ Backend System

- Implemented using **SQLite** for cloud compatibility
- Auto-generates 1000 demo policies
- Database Tables:
  - `Policy_Master`
  - `Claims`
  - `Tickets`

### Workflow:

1. Validate Policy  
2. Upload Damage Image  
3. AI Damage Detection  
4. Claim Creation  
5. Ticket Generation  
6. PDF Claim Report  

---

### 3️ Frontend (Streamlit)

- Minimal & professional UI
- Centered branding
- Real-time AI inference
- Secure confirmation before claim submission
- Admin dashboard with KPIs

---

### 4  PDF Report Generation

Each claim generates a downloadable PDF containing:

- Company Logo  
- Title & subtitle  
- Policy details  
- Damage classification  
- Confidence score  
- Claim ID  
- Uploaded damage image  

---

## 🟢 R — Results

- Built a full-stack AI insurance automation system  
- Integrated deep learning with database workflows  
- Achieved automated claim lifecycle simulation  
- Designed scalable, cloud-ready architecture  
- Demonstrated production-level AI deployment capability  

---

# 🏗️ Tech Stack

| Layer | Technology |
|--------|------------|
| Deep Learning | YOLOv8 (Ultralytics) |
| Backend | SQLite |
| Frontend | Streamlit |
| Image Processing | OpenCV |
| PDF Generation | ReportLab |
| Programming Language | Python 3.11+ |

---


# 🚀 How to Run Locally

## 1️⃣ Clone Repository

```bash
git clone https://github.com/yourusername/Insurance-Saathi-AI-Powered-Vehicle-Damage-Detection-Automated-Claim-Processing-System.git
cd Insurance-Saathi-AI-Powered-Vehicle-Damage-Detection-Automated-Claim-Processing-System


