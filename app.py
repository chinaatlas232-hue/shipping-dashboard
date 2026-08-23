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
    st.sidebar.markdown("---")
    # زر أحمر لحذف البيانات برمجياً من السيرفر
    if st.sidebar.button("🗑️ مسح وتصفير البيانات المخزنة", type="primary"):
        try:
            os.remove(SAVED_FILE_PATH)  # حذف الملف من القرص الصلب للسيرفر
            st.cache_data.clear()      # مسح الكاش تماماً
            st.sidebar.success("تم مسح الملف القديم برمجياً وتصفير النظام بنجاح! 🔄")
            st.rerun()                 # إعادة تحميل الصفحة لعرض واجهة البداية
        except Exception as e:
            st.sidebar.error(f"تعذر المسح: {e}")
    st.sidebar.markdown("---")

# --- 2. أداة رفع ملف العميل الجديد ---
uploaded_file = st.sidebar.file_uploader(
    "رفع ملف اكسل العميل الجديد", type=["xlsx", "xls"]
)

# إذا قام المستخدم برفع ملف جديد، يتم حفظه فوراً على الخادم واستبدال الملف القديم
if uploaded_file is not None:
    with open(SAVED_FILE_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("تم رفع وحفظ ملف العميل الجديد بنجاح على الخادم! 🚀")
    st.cache_data.clear()
    st.rerun()

# --- 3. دالة قراءة وتجهيز البيانات المثبتة ---
def load_and_clean_data(path):
    try:
        # قراءة ملف الإكسل بدون عناوين مسبقة لتجنب مشاكل دمج الخلايا
        df = pd.read_excel(path, header=None)
        
        # تنفيذ عملية المسح: الاحتفاظ بأول 6 أسطر فقط وحذف الجدول السفلي الطويل
        cleaned_df = df.iloc[0:6, :]
        return cleaned_df
    except Exception as e:
        return None

# التحقق من وجود الملف الثابت لقراءته وعرضه
if os.path.exists(SAVED_FILE_PATH):
    df = load_and_clean_data(SAVED_FILE_PATH)
    if df is not None:
        st.info("📌 يتم الآن عرض بيانات الملخص المثبتة والمخزنة مسبقاً على الخادم.")
else:
    df = None

# التحقق من سلامة البيانات قبل المتابعة (إذا كان النظام مصفراً أو تم مسحه)
if df is None or df.empty:
    st.title("📦 Logistics Dashboard")
    st.warning("⚠️ النظام فارغ ومصفّر تماماً الآن. يرجى رفع ملف إكسل من الشريط الجانبي لتثبيته في النظام للمرة الأولى.")
    st.stop()

# --- 4. تصميم واجهة لوحة التحكم بعد معالجة البيانات ---
st.title("📦 Logistics Dashboard")
st.markdown("Interactive view of shipments by container, shipping mark, payments and freight")
st.markdown("---")

# عرض ملخص البيانات بعد مسح الجدول السفلي (6 أسطر فقط)
st.subheader("📋 صندوق ملخص الشحنات الحالي (بعد المسح والتنظيف البرمجي)")
st.dataframe(df, use_container_width=True)

# --- 5. إعداد زر تحميل الملف النظيف باستخدام المحرك الافتراضي المدمج لـ Pandas ---
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
