import streamlit as st
from PIL import Image

st.title("لوحة معالجة صور الشحنات")

# 1. إضافة أداة لرفع الصورة من الواجهة
uploaded_file = st.file_uploader("قم برفع صورة الشحنات هنا", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 2. فتح الصورة المرفوعة مباشرة
    img = Image.open(uploaded_file)
    
    # 3. الحصول على أبعاد الصورة
    width, height = img.size
    
    # 4. تحديد منطقة القص (الاحتفاظ بأول 30% من الارتفاع)
    crop_height = int(height * 0.30)
    cropped_img = img.crop((0, 0, width, crop_height))
    
    # 5. عرض النتيجة للمستخدم على الشاشة
    st.subheader("الصورة الناتجة بعد مسح الصندوق:")
    st.image(cropped_img, use_container_width=True)
    
    # 6. زر اختياري لتحميل الصورة المقصوصة
    # نحتاج لحفظها مؤقتاً في الذاكرة لتسهيل تحميلها
    import io
    buf = io.BytesIO()
    cropped_img.save(buf, format="JPEG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="تحميل الصورة المعدلة",
        data=byte_im,
        file_name="cleared_image.jpg",
        mime="image/jpeg"
    )
else:
    st.info("بانتظار رفع صورة لبدء عملية القص والمسح.")
