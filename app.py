import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import os

# إعدادات صفحة لوحة التحكم
st.set_page_config(
    page_title="Logistics Dashboard", page_icon="📦", layout="wide"
)

# مسار حفظ الملف الثابت على الخادم لضمان عدم ضياع البيانات عند إغلاق المتصفح
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
        # قراءة ملف الإكسل بدون عناوين مسبقة لتجنب مشاكل دمج الخلايا في الملخص العلوي
        df = pd.read_excel(path, header=None)
        
        # تنفيذ عملية المسح: الاحتفاظ بأول 6 أسطر فقط (صندوق الملخص) وحذف الجدول السفلي الطويل
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

# عرض ملخص البيانات بعد مسح الجدول السفلي
st.subheader("📋 صندوق ملخص الشحنات الحالي (بعد المسح والتنظيف)")
st.dataframe(df, use_container_width=True)

# استخراج الأعمدة الرقمية للرسوم البيانية التفاعلية إذا كانت متوفرة في الملخص
numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

if len(numeric_cols) >= 1 and len(df.columns) > 1:
    st.markdown("---")
    st.subheader("📈 الرسوم البيانية التفاعلية للملخص")
    
    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox("اختر محور البيانات (X):", df.columns, index=0)
    with col2:
        y_axis = st.selectbox("اختر القيمة الرقمية (Y):", numeric_cols, index=0)

    fig = px.bar(
        df,
        x=x_axis,
        y=y_axis,
        template="plotly_dark",
        title=f"مخطط تفاعلي لـ {y_axis} حسب {x_axis}",
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 4. إعداد زر تحميل الملف النظيف من الشريط الجانبي ---
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, header=False, sheet_name='Summary')
processed_excel_data = output.getvalue()

st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 تحميل التقرير النظيف الحالي (Excel)",
    data=processed_excel_data,
    file_name="cleaned_shipment_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
