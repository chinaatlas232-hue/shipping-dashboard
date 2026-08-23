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

# --- 1. إدارة ملفات العملاء وتثبيتها في الشريط الجانبي ---
st.sidebar.subheader("📁 إدارة ملفات العملاء")
uploaded_file = st.sidebar.file_uploader(
    "رفع ملف اكسل العميل الجديد", type=["xlsx", "xls"]
)

# إذا قام المستخدم برفع ملف جديد، يتم حفظه فوراً على الخادم واستبدال الملف القديم
if uploaded_file is not None:
    with open(SAVED_FILE_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("تم رفع وحفظ ملف العميل الجديد بنجاح على الخادم! 🚀")
    # إعادة تشغيل التطبيق فوراً لتحديث البيانات المعروضة تلقائياً
    st.rerun()

# --- 2. دالة قراءة وتجهيز البيانات المثبتة ---
def load_and_clean_data(path):
    try:
        # قراءة ملف الإكسل بدون عناوين مسبقة لتجنب مشاكل دمج الخلايا
        df = pd.read_excel(path, header=None)
        
        # تنفيذ عملية المسح الحقيقية: الاحتفاظ بأول 6 أسطر فقط وحذف الجدول السفلي الطويل
        cleaned_df = df.iloc[0:6, :]
        return cleaned_df
    except Exception as e:
        return None

# التحقق من وجود الملف الثابت لقراءته وعرضه
if os.path.exists(SAVED_FILE_PATH):
    df = load_and_clean_data(SAVED_FILE_PATH)
    st.info("📌 يتم الآن عرض بيانات الملخص المثبتة والمخزنة مسبقاً على الخادم.")
else:
    df = None

# التحقق من سلامة البيانات قبل المتابعة
if df is None or df.empty:
    st.title("📦 Logistics Dashboard")
    st.warning("⚠️ لا توجد بيانات مثبتة حالياً. يرجى رفع ملف إكسل من الشريط الجانبي لتثبيته في النظام للمرة الأولى.")
    st.stop()

# --- 3. تصميم واجهة لوحة التحكم بعد معالجة البيانات ---
st.title("📦 Logistics Dashboard")
st.markdown("Interactive view of shipments by container, shipping mark, payments and freight")
st.markdown("---")

# عرض ملخص البيانات بعد مسح الجدول السفلي (6 أسطر فقط)
st.subheader("📋 صندوق ملخص الشحنات الحالي (بعد المسح والتنظيف)")
st.dataframe(df, use_container_width=True)

# --- 4. إعداد زر تحميل الملف النظيف باستخدام المحرك الافتراضي المدمج لـ Pandas ---
output = io.BytesIO()
# قمنا بإزالة 'xlsxwriter' واستبداله بالمحرك الافتراضي المدمج ليتوافق مع السيرفر تلقائياً
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
