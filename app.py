import streamlit as st
import easyocr
from PIL import Image
import pandas as pd
import numpy as np

st.set_page_config(page_title="Bill Scanner", layout="centered")
st.title("📸 Bill Scanner & Editor")

# โหลดสมอง AI (ทำครั้งเดียว)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['th', 'en'])

reader = load_reader()

uploaded_file = st.file_uploader("ถ่ายรูปหรือเลือกรูปบิล...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="รูปที่อัปโหลด", use_container_width=True)
    
    with st.spinner('กำลังสแกนข้อความ...'):
        # แปลงรูปเป็น array เพื่อให้ AI อ่าน
        img_array = np.array(image)
        results = reader.readtext(img_array, detail=0)
        
    st.subheader("📝 ตรวจสอบและแก้ไขข้อมูล")
    # นำข้อความที่สแกนได้มาใส่ในตารางเพื่อให้แก้ไขได้ง่าย
    df = pd.DataFrame(results, columns=["ข้อความที่สแกนพบ"])
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    st.success("สแกนเสร็จแล้ว! คุณสามารถพิมพ์แก้ไขข้อมูลในตารางได้เลย")
