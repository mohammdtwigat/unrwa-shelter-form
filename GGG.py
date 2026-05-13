import streamlit as st
import pandas as pd
from datetime import datetime
import os
import textwrap
from PIL import Image

import gspread
from google.oauth2.service_account import Credentials

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

try:
    from streamlit_js_eval import get_geolocation
except Exception:
    get_geolocation = None


# =====================================================
# SETTINGS
# =====================================================

st.set_page_config(
    page_title="UNRWA Shelter Assessment Form",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

EXCEL_FILE = "shelter_assessment_responses.xlsx"
GOOGLE_SHEET_NAME = "Shelter_Assessment_Responses"
LOGO_FILE = "unrwa_logo.png"


# =====================================================
# GOOGLE SHEETS
# =====================================================

def connect_google_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_file(
        "credentials.json",
        scopes=scopes
    )

    client = gspread.authorize(credentials)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    return sheet


def save_to_google_sheet(data):
    sheet = connect_google_sheet()

    headers = list(data.keys())
    existing_headers = sheet.row_values(1)

    if not existing_headers:
        sheet.append_row(headers)

    row = [str(data.get(h, "")) for h in headers]
    sheet.append_row(row)


# =====================================================
# PDF REPORT
# =====================================================

def create_pdf_report(data):
    os.makedirs("reports", exist_ok=True)

    plot_id = str(data.get("Plot ID", "Unknown")).replace(" ", "_").replace("/", "_")
    pdf_name = f"Shelter_Report_{plot_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join("reports", pdf_name)

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "UNRWA SHELTER TECHNICAL ASSESSMENT REPORT")
    y -= 0.8 * cm

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, "Field Engineering Assessment Report")
    y -= 1 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Assessment Details")
    y -= 0.7 * cm

    c.setFont("Helvetica", 9)

    for key, value in data.items():
        text = f"{key}: {value}"
        lines = textwrap.wrap(text, width=95)

        for line in lines:
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm
                c.setFont("Helvetica", 9)

            c.drawString(2 * cm, y, line)
            y -= 0.45 * cm

        y -= 0.1 * cm

    if y < 3 * cm:
        c.showPage()
        y = height - 2 * cm

    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, y, "FIELD ENGINEER SIGNATURE:")
    c.drawString(8 * cm, y, str(data.get("Field Engineer Signature", "")))

    y -= 0.7 * cm
    c.drawString(2 * cm, y, "DATE:")
    c.drawString(4 * cm, y, str(data.get("Signature Date", "")))

    c.save()
    return pdf_path


# =====================================================
# SAVE EXCEL
# =====================================================

def save_to_excel(data):
    new_df = pd.DataFrame([data])

    if os.path.exists(EXCEL_FILE):
        old_df = pd.read_excel(EXCEL_FILE)
        final_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        final_df = new_df

    final_df.to_excel(EXCEL_FILE, index=False)


# =====================================================
# CSS STYLE - BLUE & WHITE FIXED LABELS
# =====================================================

st.markdown("""
<style>

:root {
    --main-blue: #0057B8;
    --light-blue: #EAF4FF;
    --dark-blue: #003F8A;
    --text-dark: #0F172A;
}

/* Main background */
.stApp {
    background: #F4F8FC !important;
    color: #0F172A !important;
}

/* Main container */
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

/* Hide extra top space */
header[data-testid="stHeader"] {
    background-color: transparent;
}

/* Header */
.header-box {
    background: linear-gradient(90deg, #0057B8, #0072CE);
    padding: 28px;
    border-radius: 18px;
    color: white !important;
    margin-bottom: 25px;
    box-shadow: 0 5px 18px rgba(0, 87, 184, 0.28);
}

.header-title {
    font-size: 38px;
    font-weight: 900;
    color: white !important;
    margin-bottom: 8px;
    letter-spacing: 1px;
}

.header-subtitle {
    font-size: 18px;
    color: white !important;
    opacity: 0.96;
}

/* Section Card */
.section-card {
    background: #FFFFFF !important;
    border: 1px solid #CFE1F5;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 22px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.05);
}

/* Section Title */
.section-title {
    background: linear-gradient(90deg, #0057B8, #0072CE);
    color: white !important;
    padding: 12px 18px;
    border-radius: 10px;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 20px;
}

/* IMPORTANT: Fix labels visibility */
label,
.stTextInput label,
.stTextArea label,
.stNumberInput label,
.stSelectbox label,
.stRadio label,
.stMultiSelect label,
.stDateInput label,
.stTimeInput label,
.stFileUploader label {
    color: #003F8A !important;
    font-weight: 800 !important;
    font-size: 15px !important;
}

/* Help text and small text */
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] span {
    color: #0F172A !important;
}

/* Inputs */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border-radius: 10px !important;
    border: 1px solid #B9D3EF !important;
}

/* Date and time input */
.stDateInput input,
.stTimeInput input {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border-radius: 10px !important;
    border: 1px solid #B9D3EF !important;
}

/* Placeholder */
input::placeholder,
textarea::placeholder {
    color: #64748B !important;
    opacity: 1 !important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1px solid #B9D3EF !important;
    border-radius: 10px !important;
}

/* Multiselect */
div[data-baseweb="tag"] {
    background-color: #EAF4FF !important;
    color: #003F8A !important;
}

/* Radio and checkbox text */
.stRadio label p,
.stCheckbox label p {
    color: #0F172A !important;
    font-weight: 500 !important;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(90deg, #0057B8, #0072CE) !important;
    color: white !important;
    border-radius: 12px !important;
    height: 50px !important;
    border: none !important;
    font-size: 16px !important;
    font-weight: 800 !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #003F8A !important;
    color: white !important;
}

/* Success and warning */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
}

/* Footer */
.footer {
    background: linear-gradient(90deg, #0057B8, #0072CE);
    color: white !important;
    text-align: center;
    padding: 18px;
    border-radius: 15px;
    margin-top: 25px;
    font-size: 14px;
}

.footer * {
    color: white !important;
}

/* Remove strange black separator if appears */
hr {
    border: none !important;
    border-top: 1px solid #CFE1F5 !important;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# HEADER
# =====================================================

col_logo, col_title = st.columns([1, 5])

with col_logo:
    if os.path.exists(LOGO_FILE):
        st.image(Image.open(LOGO_FILE), width=170)
    else:
        st.info("ضع شعار الأونروا باسم unrwa_logo.png بجانب ملف GGG.py")

with col_title:
    st.markdown("""
    <div class="header-box">
        <div class="header-title">UNRWA SHELTER ASSESSMENT FORM</div>
        <div class="header-subtitle">Field Data Collection for Emergency Shelter Assessment</div>
        <div class="header-subtitle">   نموذج كشف هندسي ميداني</div>
         <div class="header-subtitle">   اعداد المهندس محمد الطويقات</div>

    </div>
    """, unsafe_allow_html=True)


# =====================================================
# AUTO GPS
# =====================================================

auto_gps_coordinates = ""
auto_latitude = ""
auto_longitude = ""

if get_geolocation:
    location = get_geolocation()

    if location:
        auto_latitude = location["coords"]["latitude"]
        auto_longitude = location["coords"]["longitude"]
        auto_gps_coordinates = f"{auto_latitude}, {auto_longitude}"


# =====================================================
# FORM
# =====================================================

with st.form("assessment_form"):

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 PROJECT INFORMATION</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        hof_name = st.text_input("Name of HoF", placeholder="Enter Head of Family Name")
        unrwa_no = st.text_input("UNRWA Family Registration Number", placeholder="Enter Registration Number")
        phone1 = st.text_input("Phone 1", placeholder="07XXXXXXXX")
        phone2 = st.text_input("Phone 2", placeholder="Optional")
        plot_id_main = st.text_input("Plot ID", placeholder="Example: C 17.18")

    with col2:
        project_name = st.text_input("PROJECT NAME")
        project_code = st.text_input("PROJECT CODE")
        house_id = st.text_input("HOUSE ID")
        plot_id = st.text_input("PLOT ID")
        assessment_date = st.date_input("DATE")
        assessment_time = st.time_input("TIME")
        field_engineer = st.text_input("FIELD ENGINEER")
        team_members = st.text_area("TEAM MEMBERS")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">1. GENERAL INFORMATION</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        owner_name = st.text_input("Owner Name")
        national_id = st.text_input("National ID")
        phone_number = st.text_input("Phone Number")
        alternative_phone = st.text_input("Alternative Phone")
        address = st.text_area("Address")

        gps_coordinates = st.text_input(
            "GPS Coordinates",
            value=auto_gps_coordinates,
            placeholder="Auto GPS or enter manually"
        )

        if auto_gps_coordinates:
            st.success(f"GPS captured: {auto_gps_coordinates}")

    with col2:
        type_of_housing = st.selectbox(
            "Type of Housing",
            ["", "Concrete House", "Apartment", "Temporary Shelter", "Informal Shelter", "Other"]
        )
        number_of_floors = st.number_input("Number of Floors", min_value=0, step=1)
        current_occupancy = st.selectbox("Current Occupancy", ["", "Occupied", "Partially Occupied", "Vacant"])
        number_of_families = st.number_input("Number of Families", min_value=0, step=1)
        number_of_residents = st.number_input("Number of Residents", min_value=0, step=1)
        children = st.number_input("Children", min_value=0, step=1)
        elderly = st.number_input("Elderly", min_value=0, step=1)
        pwd_cases = st.selectbox("PWD Cases", ["", "Yes", "No"])
        pwd_details = st.text_area("Details of PWD Cases")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">2. EXISTING HOUSE INFORMATION</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        building_age = st.text_input("Approximate Building Age")
        structural_system = st.selectbox(
            "Structural System",
            ["", "Reinforced Concrete", "Load Bearing Walls", "Steel", "Mixed", "Other"]
        )
        roof_type = st.selectbox(
            "Roof Type",
            ["", "Concrete Slab", "Metal Sheet", "Wood", "Asbestos", "Other"]
        )

    with col2:
        total_existing_area = st.text_input("Total Existing Area")
        additional_structures = st.text_area("Additional Structures")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">3. ARCHITECTURAL ASSESSMENT</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        spaces_available = st.text_area("Spaces Available")
        bedrooms = st.number_input("Number of Bedrooms", min_value=0, step=1)
        bathrooms = st.number_input("Number of Bathrooms", min_value=0, step=1)
        ventilation = st.selectbox("Ventilation Condition", ["", "Good", "Fair", "Poor"])
        lighting = st.selectbox("Lighting Condition", ["", "Good", "Fair", "Poor"])

    with col2:
        accessibility = st.selectbox("Accessibility", ["", "Good", "Fair", "Poor", "Not Accessible"])
        cleanliness = st.selectbox("General Cleanliness", ["", "Good", "Fair", "Poor"])
        overcrowding = st.selectbox("Overcrowding", ["", "Yes", "No"])
        architectural_notes = st.text_area("Architectural Notes")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">4. STRUCTURAL ASSESSMENT</div>', unsafe_allow_html=True)

    condition_options = ["", "Good", "Fair", "Poor", "Critical"]

    col1, col2 = st.columns(2)

    with col1:
        foundations = st.selectbox("Foundations", condition_options)
        columns = st.selectbox("Columns", condition_options)
        beams = st.selectbox("Beams", condition_options)
        slabs_roof = st.selectbox("Slabs / Roof", condition_options)

    with col2:
        walls = st.selectbox("Walls", condition_options)
        stairs = st.selectbox("Stairs", condition_options)
        floor_condition = st.selectbox("Floor Condition", condition_options)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">5. SERVICES ASSESSMENT</div>', unsafe_allow_html=True)

    service_options = ["", "Good", "Fair", "Poor", "Not Available"]

    col1, col2 = st.columns(2)

    with col1:
        electrical = st.selectbox("Electrical System", service_options)
        water_supply = st.selectbox("Water Supply", service_options)

    with col2:
        sewage = st.selectbox("Sewage System", service_options)
        rainwater = st.selectbox("Rainwater Drainage", service_options)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">6. SAFETY ASSESSMENT</div>', unsafe_allow_html=True)

    safety_options = ["", "Yes", "No"]

    col1, col2 = st.columns(2)

    with col1:
        immediate_safety_risk = st.selectbox("Immediate Safety Risk", safety_options)
        evacuation_required = st.selectbox("Evacuation Required", safety_options)

    with col2:
        children_at_risk = st.selectbox("Children at Risk", safety_options)
        structural_collapse_risk = st.selectbox("Structural Collapse Risk", safety_options)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">7. DAMAGE CLASSIFICATION</div>', unsafe_allow_html=True)

    damage_classification = st.radio(
        "Select Damage Classification",
        [
            "D1 – Minor Damage",
            "D2 – Moderate Damage",
            "D3 – Severe Damage",
            "D4 – Unsafe Structure"
        ],
        horizontal=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">8. ENGINEERING RECOMMENDATION</div>', unsafe_allow_html=True)

    engineering_recommendation = st.multiselect(
        "Engineering Recommendation",
        [
            "Minor Repair",
            "Rehabilitation",
            "Partial Reconstruction",
            "Full Reconstruction",
            "Temporary Support Required",
            "Demolition Recommended"
        ]
    )

    priority_level = st.selectbox("Priority Level", ["", "Low", "Medium", "High", "Emergency"])

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">9. REQUIRED INTERVENTIONS</div>', unsafe_allow_html=True)

    required_interventions = st.multiselect(
        "Required Interventions",
        [
            "Structural Repair",
            "Roof Replacement",
            "Additional Room",
            "Toilet",
            "Accessibility Ramp",
            "Electrical Upgrade",
            "Plumbing Upgrade",
            "Waterproofing",
            "Full Redesign"
        ]
    )

    intervention_notes = st.text_area("Notes")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">11. FIELD ENGINEER FINAL NOTES</div>', unsafe_allow_html=True)

    final_notes = st.text_area("FIELD ENGINEER FINAL NOTES")

    uploaded_photos = st.file_uploader(
        "Upload Site Photos",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    field_engineer_signature = st.text_input(
        "FIELD ENGINEER SIGNATURE",
        value="ENG. MOHAMMED ALTWIQAT"
    )

    signature_date = st.date_input("SIGNATURE DATE")

    st.markdown('</div>', unsafe_allow_html=True)

    submit = st.form_submit_button("🚀 Submit Assessment")


# =====================================================
# AFTER SUBMIT
# =====================================================

if submit:

    data = {
        "Timestamp": datetime.now(),

        "Name of HoF": hof_name,
        "UNRWA Family Registration Number": unrwa_no,
        "Phone 1": phone1,
        "Phone 2": phone2,
        "Main Plot ID": plot_id_main,

        "Project Name": project_name,
        "Project Code": project_code,
        "House ID": house_id,
        "Plot ID": plot_id,
        "Date": assessment_date,
        "Time": assessment_time,
        "Field Engineer": field_engineer,
        "Team Members": team_members,

        "Owner Name": owner_name,
        "National ID": national_id,
        "Phone Number": phone_number,
        "Alternative Phone": alternative_phone,
        "Address": address,
        "GPS Coordinates": gps_coordinates,
        "Auto Latitude": auto_latitude,
        "Auto Longitude": auto_longitude,
        "Type of Housing": type_of_housing,
        "Number of Floors": number_of_floors,
        "Current Occupancy": current_occupancy,
        "Number of Families": number_of_families,
        "Number of Residents": number_of_residents,
        "Children": children,
        "Elderly": elderly,
        "PWD Cases": pwd_cases,
        "Details of PWD Cases": pwd_details,

        "Approximate Building Age": building_age,
        "Structural System": structural_system,
        "Roof Type": roof_type,
        "Total Existing Area": total_existing_area,
        "Additional Structures": additional_structures,

        "Spaces Available": spaces_available,
        "Number of Bedrooms": bedrooms,
        "Number of Bathrooms": bathrooms,
        "Ventilation Condition": ventilation,
        "Lighting Condition": lighting,
        "Accessibility": accessibility,
        "General Cleanliness": cleanliness,
        "Overcrowding": overcrowding,
        "Architectural Notes": architectural_notes,

        "Foundations": foundations,
        "Columns": columns,
        "Beams": beams,
        "Slabs / Roof": slabs_roof,
        "Walls": walls,
        "Stairs": stairs,
        "Floor Condition": floor_condition,

        "Electrical System": electrical,
        "Water Supply": water_supply,
        "Sewage System": sewage,
        "Rainwater Drainage": rainwater,

        "Immediate Safety Risk": immediate_safety_risk,
        "Evacuation Required": evacuation_required,
        "Children at Risk": children_at_risk,
        "Structural Collapse Risk": structural_collapse_risk,

        "Damage Classification": damage_classification,

        "Engineering Recommendation": ", ".join(engineering_recommendation),
        "Priority Level": priority_level,

        "Required Interventions": ", ".join(required_interventions),
        "Intervention Notes": intervention_notes,

        "Field Engineer Final Notes": final_notes,
        "Field Engineer Signature": field_engineer_signature,
        "Signature Date": signature_date,

        "Uploaded Photos Count": len(uploaded_photos) if uploaded_photos else 0
    }

    save_to_excel(data)
    st.success("✅ Data saved locally to Excel.")

    try:
        save_to_google_sheet(data)
        st.success("✅ Data saved successfully to Google Sheets.")
    except Exception as e:
        st.error(f"Google Sheets Error: {e}")

    try:
        pdf_path = create_pdf_report(data)
        st.success("✅ PDF report generated successfully.")

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_file,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"PDF Error: {e}")

    with open(EXCEL_FILE, "rb") as excel_file:
        st.download_button(
            label="📥 Download Excel File",
            data=excel_file,
            file_name=EXCEL_FILE,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


st.markdown("""
<div class="footer">
    © 2026 UNRWA - Field Engineering Unit | Shelter Technical Assessment Form
</div>
""", unsafe_allow_html=True)