import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# إعدادات صفحة لوحة التحكم
st.set_page_config(
    page_title="Logistics Dashboard", page_icon="📦", layout="wide"
)

# --- 1. نظام حماية بكلمة مرور ---
PASSWORD = "1234"  # يمكنك تغيير كلمة المرور هنا إلى ما تريده

password_input = st.sidebar.text_input(
    "🔒 أدخل كلمة المرور للوصول للوحة:", type="password"
)

if password_input != PASSWORD:
    st.title("🔒 Logistics Dashboard — Protected")
    st.warning(
        "⚠️ يرجى إدخال كلمة المرور الصحيحة في الشريط الجانبي لعرض بيانات الشحنات."
    )
    st.stop()  # إيقاف عرض الصفحة بالكامل حتى يتم إدخال الباسورد الصحيح

# --- 2. زر رفع ملف العميل الجديد ---
st.sidebar.markdown("---")
st.sidebar.subheader("📁 إدارة ملفات العملاء")
uploaded_file = st.sidebar.file_uploader(
    "رفع ملف اكسل العميل الجديد", type=["xlsx", "xls"]
)

DATA_FILE = "data.xlsx"  # الملف الافتراضي في النظام

if uploaded_file is not None:
    file_to_use = uploaded_file
    st.sidebar.success("تم رفع ملف العميل الجديد بنجاح! 🚀")
else:
    file_to_use = DATA_FILE


# --- 3. دالة قراءة البيانات ---
@st.cache_data
def load_data(path):
    try:
        df = pd.read_excel(path)
        return df
    except Exception as e:
        return None


df = load_data(file_to_use)

if df is None or df.empty:
    st.error(
        "⚠️ لم يتم العثور على بيانات أو أن الملف فارغ. يرجى التأكد من رفع ملف صحيح."
    )
    st.stop()

# --- 4. تصميم واجهة لوحة التحكم ---
st.title("📦 Logistics Dashboard")
st.markdown("Interactive view of shipments by container, shipping mark, payments and freight")
st.markdown("---")

# عرض ملخص سريع للبيانات
st.subheader("📋 جدول بيانات الشحنات")
st.dataframe(df, use_container_width=True)

# استخراج الأعمدة الرقمية للرسوم البيانية التفاعلية
numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

if len(numeric_cols) >= 1 and len(df.columns) > 1:
    st.markdown("---")
    st.subheader("📈 الرسوم البيانية التفاعلية")
    
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

# زر لتحميل البيانات كملف CSV من الشريط الجانبي
csv = df.to_csv(index=False).encode("utf-8")
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 تحميل التقرير الحالي (CSV)",
    data=csv,
    file_name="shipment_report.csv",
    mime="text/csv",
)
