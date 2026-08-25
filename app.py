import io
import pandas as pd
import streamlit as st

# إعداد الصفحة وتكوينها
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="🚢", layout="wide"
)

# تفعيل التصميم المخصص لدعم اللغة العربية وتناسق الألواح
st.markdown(
    """
    <style>
    body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }
    .stDataFrame {
        text-align: right;
    }
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# بيانات تجريبية افتراضية للمنصة
@st.cache_data
def load_default_data():
    data = {
        "No.": [34, 176, 293, 585, 604],
        "code": ["B7", "B7", "B7", "B7", "B7"],
        "Shipping mark": [
            "B7-B13",
            "B7-C19",
            "B7-B26",
            "B7-C37",
            "B7-C28 (B)",
        ],
        "رقم دخول المخزن": [
            "RS26032397217",
            "RA260429100757",
            "RS260430101131",
            "RS260529088",
            "RS2606121092",
        ],
        "نوع البضاعة": [
            "Ladies dress",
            "HANGER",
            "LADY SET",
            "SET",
            "White shirt",
        ],
        "عدد الكارتون": [8, 13, 6, 9, 1],
        "الوزن": [273, 210, 426, 598, 38],
        "حجم": [1.265, 0.705, 1.476, 2.378, 0.143],
    }
    return pd.DataFrame(data)


# الشريط الجانبي (Sidebar)
st.sidebar.markdown("### 🚢 إدارة اللوجستيات")
st.sidebar.markdown("📁 رفع ملف Excel جديد")
uploaded_file = st.sidebar.file_uploader(
    "", type=["xlsx", "xls"], label_visibility="collapsed"
)
st.sidebar.caption("200MB per file • XLSX, XLS")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 الفلاتر الجانبية")
container_filter = st.sidebar.selectbox("🚢 اختر رقم الحاوية:", ["الكل"])
code_filter = st.sidebar.selectbox("🏷️ اختر الكود (Code):", ["B7"])

st.sidebar.markdown("---")
st.sidebar.markdown("📌 القائمة الرئيسية")
nav_option = st.sidebar.radio(
    "",
    [
        "📊 لوحة التحكم (Dashboard)",
        "🚢 الشحنات والحاويات",
        "📦 الطلبات",
        "💰 كشف الكمارك المستحصلة",
        "📈 واجهة التقارير",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("<br><hr>", unsafe_allow_html=True)
st.sidebar.markdown("النظام يعمل بكفاءة ✔️")

# تحميل البيانات
if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        df = load_default_data()
else:
    df = load_default_data()

# تطبيق الفلاتر
filtered_df = df.copy()
if code_filter and "code" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["code"] == code_filter]

# المحتوى الرئيسي
if "لوحة التحكم" in nav_option:
    st.markdown("## 📊 لوحة التحكم الرئيسية")

    # البطاقات الإحصائية مع الترتيب السليم للأرقام والنصوص العربية
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric(label="إجمالي الطلبات", value="28")
    with col2:
        st.metric(label="إجمالي الكارتون", value="126")
    with col3:
        st.metric(label="إجمالي الوزن", value="6,540.50 kg")
    with col4:
        st.metric(label="إجمالي الحجم", value="30.202 m³")
    with col5:
        st.metric(label="دفع الشركة", value="$579,715.00")
    with col6:
        st.metric(label="دفع الزبون", value="$116,680.00")

    st.markdown("<br>", unsafe_allow_html=True)

    # أزرار التصدير
    exp_col1, exp_col2, _ = st.columns([1, 1, 4])
    with exp_col1:
        st.button("📊 Download as Excel")
    with exp_col2:
        st.button("📥 Download as CSV")

    st.markdown("---")

    # الجدول الرئيسي
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

else:
    st.markdown(f"## {nav_option}")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
