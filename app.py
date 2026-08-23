import streamlit as st
import pandas as pd
import io
import os

# إعدادات صفحة لوحة التحكم
st.set_page_config(
    page_title="Logistics Dashboard", page_icon="📦", layout="wide"
)

# مسار حفظ الملف الثابت على الخادم
SAVED_FILE_PATH = "permanent_shipping_data.xlsx"

st.sidebar.subheader("📁 إدارة ملفات العملاء")

# --- 1. زر المسح البرمجي والتصفير الشامل ---
if os.path.exists(SAVED_FILE_PATH):
    if st.sidebar.button("🗑️ مسح وتصفير البيانات المخزنة", type="primary"):
        try:
            os.remove(SAVED_FILE_PATH)  # حذف الملف من السيرفر
            st.cache_data.clear()      # مسح الكاش
            st.sidebar.success("تم مسح الملف وتصفير النظام بنجاح! 🔄")
            st.rerun()                 
        except Exception as e:
            st.sidebar.error(f"تعذر المسح: {e}")
    st.sidebar.markdown("---")

# --- 2. أداة رفع ملف العميل الجديد ---
uploaded_file = st.sidebar.file_uploader(
    "رفع ملف اكسل العميل الجديد", type=["xlsx", "xls"]
)

if uploaded_file is not None:
    with open(SAVED_FILE_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.cache_data.clear()
    st.rerun()  

# --- 3. دالة قراءة وتجهيز البيانات المثبتة مباشرة ---
def load_and_clean_data(path):
    try:
        # قراءة ملف الإكسل كما هو بدون أي شروط مسبقة
        df = pd.read_excel(path, header=None)
        
        # الاحتفاظ بأول 15 سطراً لضمان شمول صندوق ملخص الشحنات والأكواد كاملة
        cleaned_df = df.iloc[0:15, :]
        return cleaned_df
    except Exception as e:
        return None

# التحقق من وجود الملف الثابت لقراءته
df = None
if os.path.exists(SAVED_FILE_PATH):
    df = load_and_clean_data(SAVED_FILE_PATH)
    if df is not None:
        st.info("📌 يتم الآن عرض بيانات الملخص المثبتة والمخزنة مسبقاً على الخادم.")

# إذا كان النظام مصفراً
if df is None or df.empty:
    st.title("📦 Logistics Dashboard")
    st.warning("⚠️ النظام فارغ ومصفّر تماماً الآن. يرجى رفع ملف إكسل من الشريط الجانبي لتثبيته في النظام للمرة الأولى.")
    st.stop()

# --- 4. تصميم واجهة لوحة التحكم وعرض الجدول ---
st.title("📦 Logistics Dashboard")
st.markdown("Interactive view of shipments by container, shipping mark, payments and freight")
st.markdown("---")

# عرض ملخص البيانات النظيفة والأكواد بشكل مباشر ومضمون
st.subheader("📋 صندوق ملخص الشحنات والأكواد المكتشفة")
st.dataframe(df, use_container_width=True)

# --- 5. إعداد زر تحميل الملف النظيف ---
try:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, header=False, sheet_name='Summary')
    processed_excel_data = output.getvalue()

    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 تحميل التقرير النظيف الحالي (Excel)",
        data=processed_excel_data,
        file_name="cleaned_shipment_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
except Exception as e:
    st.sidebar.error(f"خطأ في تجهيز زر التحميل: {e}")
