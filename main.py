import streamlit as st
from datetime import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="แอปบันทึกอายุต้นไม้", page_icon="🌱", layout="centered")

st.title("🌱 แอปบันทึกอายุต้นไม้")
st.write("บันทึกข้อมูลต้นไม้ ติดตามอายุ และเก็บข้อมูลถาวรบน Google Sheets")

# ฟังก์ชันเชื่อมต่อ Google Sheets ผ่าน Secrets ของ Streamlit
@st.cache_resource
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # ดึงค่าจาก Streamlit Secrets
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    # เปิดไฟล์ Google Sheets ตามชื่อ หรือ URL
    sheet = client.open("tree_data").sheet1
    return sheet

try:
    sheet = init_connection()
    # ดึงข้อมูลทั้งหมดมาแปลงเป็น DataFrame
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    
    if df.empty or "name" not in df.columns:
        df = pd.DataFrame(columns=["name", "date_thai", "days"])
except Exception as e:
    st.error(f"ไม่สามารถเชื่อมต่อ Google Sheets ได้: {e}")
    df = pd.DataFrame(columns=["name", "date_thai", "days"])

# ส่วนฟอร์มกรอกข้อมูล
with st.form("plant_form", clear_on_submit=True):
    st.subheader("เพิ่มข้อมูลต้นไม้ใหม่")
    plant_name = st.text_input("ชื่อต้นไม้ (เช่น มะนาว, กุหลาบ)")
    plant_date = st.date_input("วันที่ปลูก", value=datetime.now())
    
    submitted = st.form_submit_button("บันทึกข้อมูล")
    
    if submitted:
        if not plant_name.strip():
            st.warning("⚠️ กรุณากรอกชื่อต้นไม้ก่อนบันทึกครับ")
        else:
            today = datetime.now().date()
            days_old = (today - plant_date).days
            if days_old < 0:
                days_old = 0
                
            thai_year = plant_date.year + 543
            date_thai_str = f"{plant_date.day}/{plant_date.month}/{thai_year}"
            
            # เพิ่มข้อมูลใหม่ลงใน Google Sheets แถวถัดไป
            sheet.append_row([plant_name, date_thai_str, int(days_old)])
            st.success(f"✅ บันทึกต้น '{plant_name}' ลง Google Sheets เรียบร้อยแล้ว!")
            st.rerun()

st.divider()

# ส่วนแสดงรายการต้นไม้
st.subheader("📋 รายการต้นไม้ของคุณ")

if df.empty:
    st.info("ยังไม่มีข้อมูลต้นไม้ เริ่มต้นกรอกข้อมูลด้านบนได้เลยครับ")
else:
    for index, row in df.iterrows():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**🌱 {row['name']}**")
            st.text(f"ปลูกเมื่อ: {row['date_thai']} | อายุ: {int(row['days'])} วัน")
        with col2:
            if st.button("ลบ", key=f"del_{index}"):
                # ลบแถวออกจาก Google Sheets (บวก 2 เพราะ index เริ่มจาก 0 และติดหัวตารางแถวที่ 1)
                sheet.delete_rows(index + 2)
                st.success("ลบรายการเรียบร้อยแล้ว")
                st.rerun()
        st.write("---")
