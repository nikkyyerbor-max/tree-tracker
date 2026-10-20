import streamlit as st
from datetime import datetime

# ตั้งค่าหน้าเว็บแอป
st.set_page_config(page_title="แอปบันทึกอายุต้นไม้", page_icon="🌱", layout="centered")

st.title("🌱 แอปบันทึกอายุต้นไม้")
st.write("บันทึกข้อมูลต้นไม้ ติดตามอายุ และใช้งานได้ทั้งบนคอมพิวเตอร์และมือถือ")

# ใช้ st.session_state เพื่อให้ข้อมูลไม่หายเวลากดใช้งาน
if "plants" not in st.session_state:
    st.session_state.plants = []

# ส่วนฟอร์มกรอกข้อมูล
with st.form("plant_form", clear_on_submit=True):
    st.subheader("เพิ่มข้อมูลต้นไม้ใหม่")
    plant_name = st.text_input("ชื่อต้นไม้ (เช่น มะนาว, กุหลาบ)")
    
    # ช่องเลือกวันที่ (มีปฏิทินให้กดเลือกอัตโนมัติ)
    plant_date = st.date_input("วันที่ปลูก", value=datetime.now())
    
    submitted = st.form_submit_button("บันทึกข้อมูล")
    
    if submitted:
        if not plant_name.strip():
            st.warning("⚠️ กรุณากรอกชื่อต้นไม้ก่อนบันทึกครับ")
        else:
            # คำนวณอายุต้นไม้
            today = datetime.now().date()
            days_old = (today - plant_date).days
            if days_old < 0:
                days_old = 0
                
            # แปลงปี ค.ศ. เป็น พ.ศ.
            thai_year = plant_date.year + 543
            date_thai_str = f"{plant_date.day}/{plant_date.month}/{thai_year}"
            
            # เก็บข้อมูลลงในรายการ
            st.session_state.plants.append({
                "name": plant_name,
                "date_thai": date_thai_str,
                "days": days_old
            })
            st.success(f"✅ บันทึกต้น '{plant_name}' เรียบร้อยแล้ว!")

st.divider()

# ส่วนแสดงรายการต้นไม้
st.subheader("📋 รายการต้นไม้ของคุณ")

if not st.session_state.plants:
    st.info("ยังไม่มีข้อมูลต้นไม้ เริ่มต้นกรอกข้อมูลด้านบนได้เลยครับ")
else:
    # แสดงรายการพร้อมปุ่มลบ
    for index, plant in enumerate(st.session_state.plants):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**🌱 {plant['name']}**")
            st.text(f"ปลูกเมื่อ: {plant['date_thai']} | อายุ: {plant['days']} วัน")
        with col2:
            # ปุ่มลบข้อมูลแต่ละรายการ
            if st.button("ลบ", key=f"del_{index}"):
                del st.session_state.plants[index]
                st.rerun()
        st.write("---")
        