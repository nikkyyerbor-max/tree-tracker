import streamlit as st
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="แอปบันทึกอายุต้นไม้", page_icon="🌱", layout="centered")

st.title("🌱 แอปบันทึกอายุต้นไม้")
st.write("บันทึกข้อมูลต้นไม้ ติดตามอายุ และเก็บข้อมูลถาวรบน Google Sheets")

# เชื่อมต่อกับ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# อ่านข้อมูลล่าสุดจาก Google Sheets
try:
    data = conn.read(ttl=0)
    if data is None or data.empty or "name" not in data.columns:
        df = pd.DataFrame(columns=["name", "date_thai", "days"])
    else:
        df = data.dropna(subset=["name"])
except Exception:
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
            
            # เพิ่มแถวใหม่
            new_row = pd.DataFrame([{
                "name": plant_name,
                "date_thai": date_thai_str,
                "days": int(days_old)
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # อัปเดตลง Google Sheets
            conn.update(data=updated_df)
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
                updated_df = df.drop(index).reset_index(drop=True)
                conn.update(data=updated_df)
                st.success("ลบรายการเรียบร้อยแล้ว")
                st.rerun()
        st.write("---")
