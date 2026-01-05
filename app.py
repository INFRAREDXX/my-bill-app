import streamlit as st
import easyocr
import pandas as pd
import re
from PIL import Image
import numpy as np

# ตั้งค่าหน้าแอป
st.set_page_config(page_title="Bill Scanner", layout="centered")
st.title("🧾 Bill Scanner & Editor")
st.write("ถ่ายรูปบิล แล้วตรวจสอบข้อมูลก่อนบันทึก")

# โหลดสมอง AI (EasyOCR)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['th', 'en'])

reader = load_reader()

# ส่วนอัปโหลดรูป
uploaded_file = st.file_uploader("ถ่ายรูปหรือเลือกรูปบิล", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="รูปที่อัปโหลด", use_container_width=True)
    
    with st.spinner('กำลังอ่านข้อมูล...'):
        img_array = np.array(image)
        result = reader.readtext(img_array, detail=0)
        
        # --- ส่วน Logic เดิมของคุณ (ใส่ไว้เพื่อดึงค่าเริ่มต้น) ---
        shop_name, date, time, amount = "ไม่พบ", "ไม่พบ", "ไม่พบ", "ไม่พบ"
        for i, text in enumerate(result):
            clean_text = text.replace(" ", "").upper()
            if len(shop_name) > 10 or shop_name == "ไม่พบ": # หาชื่อร้านคร่าวๆ
                if len(text) > 3 and not any(c.isdigit() for c in text): shop_name = text
            if ('/' in text) or any(m in clean_text for m in ['DEC', 'JAN']):
                date = text if ':' not in text else text.split()[0]
            time_match = re.search(r'\d{1,2}:\d{2}', text)
            if time_match: time = time_match.group()
            if any(k in clean_text for k in ['รวม', 'AMT', 'THB']):
                for n in [1, 2]:
                    if i+n < len(result):
                        val = result[i+n].replace(",", "")
                        if re.match(r'^\d+\.\d{2}$', val): amount = result[i+n]; break

    # --- ส่วนที่เพิ่มมา: ให้คุณแก้ไขข้อมูลได้ถ้ามันมั่ว! ---
    st.subheader("📝 ตรวจสอบและแก้ไขข้อมูล")
    
    col1, col2 = st.columns(2)
    with col1:
        edit_shop = st.text_input("ชื่อร้าน", value=shop_name)
        edit_date = st.text_input("วันที่", value=date)
    with col2:
        edit_time = st.text_input("เวลา", value=time)
        edit_amount = st.text_input("ยอดเงิน", value=amount)

    # ปุ่มบันทึก
    if st.button("💾 บันทึกข้อมูลลงตาราง"):
        new_data = {
            "ชื่อร้าน": [edit_shop],
            "วันที่": [edit_date],
            "เวลา": [edit_time],
            "ยอดเงิน": [edit_amount]
        }
        df_new = pd.DataFrame(new_data)
        
        # แสดงตารางสรุป
        st.success("บันทึกข้อมูลเรียบร้อย!")
        st.table(df_new)
        
        # ปุ่มดาวน์โหลด Excel
        df_new.to_excel("bill_summary.xlsx", index=False)
        with open("bill_summary.xlsx", "rb") as f:
            st.download_button("📥 ดาวน์โหลดไฟล์ Excel", f, "bill_summary.xlsx")