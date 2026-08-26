import io
import os
import pandas as pd
import streamlit as st

# 1. إعداد الصفحة والتنسيقات
st.set_page_config(page_title="شركة أطلس المحيط", page_icon="", layout="wide")

st.markdown(
    """
<style>
.main { background-color: #0e1117; }
.metric-card {
    padding: 16px; border-radius: 12px; color: white;
    text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
}
.metric-title { font-size: 14px; margin-bottom: 6px; opacity: 0.95; font-weight: 600; }
.metric-value { font-size: 20px; font-weight: bold; }
.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 3rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
}
[data-testid="stDataFrame"], [data-testid="stTable"], table {
    width: 100% !important;
}
h1 {
    background-color: #e2e8f0 !important;
    color: #0f172a !important;
    padding: 15px 20px !important;
    border-radius: 8px !important;
    margin-bottom: 20px !important;
    margin-top: 10px !important;
}
[data-testid="stSidebar"] {
    background-color: #07151a !important;
}
[data-testid="stSidebar"] section div.stRadio label,
[data-testid="stSidebar"] section div.stRadio p,
[data-testid="stSidebar"] section div.stRadio span,
[data-testid="stSidebar"] .element-container label,
[data-testid="stSidebar"] .element-container span,
[data-testid="stSidebar"] .stMarkdown p {
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 18px !important;
}
</style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = "shipping_data.xlsx"
WMS_FILE = "wms_daily_data.xlsx"

def load_data(uploaded_file, file_path):
    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df.to_excel(file_path, index=False)
            st.sidebar.success("تم حفظ الملف الجديد بنجاح")
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة الملف: {e}")
            
    if df is None and os.path.exists(file_path):
        try:
            df = pd.read_excel(file_path)
        except Exception:
            df = None
            
    return df

# تحميل ملف التتبع الأساسي
st.sidebar.title("شركة أطلس المحيط 🚢")
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📁 رفع ملف التتبع Excel", type=["xlsx", "xls"], key="tracking_uploader")

if st.sidebar.button("مسح بيانات ملف التتبع الحالي"):
    if os.path.exists(DATA_FILE):
        try:
            os.remove(DATA_FILE)
            st.sidebar.success("تم مسح بيانات الشيت بنجاح")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"خطأ أثناء حذف الملف: {e}")
    else:
        st.sidebar.info("لا توجد بيانات مسجلة مسبقاً.")

df = load_data(uploaded_file, DATA_FILE)

if df is None:
    df = pd.DataFrame(columns=[
        "رقم دخول المخزن", "Shipping mark", "الكفيل", "No", "code",
        "المكتب دفع", "الزبون دفع", "المجموع", "عدد الكارتون",
        "الوزن", "حجم", "رقم الحاوية", "مبلغ الجمرك", "قيمة الاستحصالات", "عدد الايام"
    ])

# تنظيف أسماء الأعمدة لإزالة المسافات الزائدة
df.columns = df.columns.astype(str).str.strip()

# دالة ذكية لتحويل الأعمدة الرقمية وتجنب الأخطاء
def safe_to_numeric(series):
    if series is None:
        return 0
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.strip(),
        errors="coerce"
    ).fillna(0)

# البحث عن أعمدة الدفع بالأسماء العربية أو الإنجليزية المتاحة بدقة
office_col = None
client_col = None

for col in df.columns:
    if "المكتب" in col or "Office" in col:
        office_col = col
    if "الزبون" in col or "Client" in col:
        client_col = col

if office_col:
    df["Office Paid"] = safe_to_numeric(df[office_col])
else:
    df["Office Paid"] = 0

if client_col:
    df["Client Paid"] = safe_to_numeric(df[client_col])
else:
    df["Client Paid"] = 0

# تنظيف باقي الأعمدة الرقمية الأساسية
numeric_cols = ["عدد الكارتون", "الوزن", "حجم", "المجموع", "مبلغ الجمرك", "قيمة الاستحصالات", "عدد الايام"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = safe_to_numeric(df[col])

if "مبلغ الجمرك" in df.columns and "قيمة الاستحصالات" in df.columns:
    df["متبقي حقيقي"] = df["مبلغ الجمرك"] - df["قيمة الاستحصالات"]

filtered_df = df.copy()

# الفلاتر الجانبية
st.sidebar.markdown("---")
st.sidebar.markdown("🔍 **الفلاتر الجانبية**")

container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in df.columns), None)
selected_container = "الكل"
if container_col and not df.empty:
    containers = ["الكل"] + sorted(df[container_col].dropna().astype(str).unique().tolist())
    selected_container = st.sidebar.selectbox("اختر رقم الحاوية:", containers)
    if selected_container != "الكل":
        filtered_df = filtered_df[filtered_df[container_col].astype(str) == selected_container]

code_col = next((c for c in ["code", "الكود", "كود"] if c in df.columns), "code")
selected_code = "الكل"
if code_col in df.columns and not df.empty:
    codes = ["الكل"] + sorted(df[code_col].dropna().astype(str).unique().tolist())
    selected_code = st.sidebar.selectbox("اختر الكود (Code):", codes)
    if selected_code != "الكل":
        filtered_df = filtered_df[filtered_df[code_col].astype(str) == selected_code]

sponsor_filter_col = next((c for c in ["الكفيل", "كفيل"] if c in df.columns), None)
selected_sponsor = "الكل"
if sponsor_filter_col and not df.empty:
    sponsors = ["الكل"] + sorted(df[sponsor_filter_col].dropna().astype(str).unique().tolist())
    selected_sponsor = st.sidebar.selectbox("اختر اسم الكفيل:", sponsors)
    if selected_sponsor != "الكل":
        filtered_df = filtered_df[filtered_df[sponsor_filter_col].astype(str) == selected_sponsor]

st.sidebar.markdown("---")

# القائمة الرئيسية
page_options = {
    "لوحة التحكم (Dashboard)": "dashboard",
    "حركة المخازن (WMS)": "wms_movement",
    "كشف أجور الكمارك": "customs",
    "الديون على الكفلاء": "sponsors",
    "اعمار الديون (Aging Report)": "aging",
    "كمرك الشحنات والاستحصالات": "collections",
    "الرسوم البيانية": "charts"
}

selected_page_label = st.sidebar.radio("القائمة الرئيسية 📌", list(page_options.keys()))
page = page_options[selected_page_label]

st.sidebar.markdown("---")
st.sidebar.info("النظام يعمل بكفاءة ✓")

def render_download_buttons(data_to_download):
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            data_to_download.to_excel(writer, index=False, sheet_name='Filtered_Data')
        st.download_button(
            label="📥 Download as Excel",
            data=buffer.getvalue(),
            file_name="filtered_details.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with btn_col2:
        st.download_button(
            label="📥 Download as CSV",
            data=data_to_download.to_csv(index=False).encode('utf-8'),
            file_name="filtered_details.csv",
            mime="text/csv"
        )

# صفحة لوحة التحكم
if page == "dashboard":
    st.title("📊 لوحة التحكم الرئيسية")
    st.markdown("---")
    
    total_orders = len(filtered_df)
    total_weight = filtered_df["الوزن"].sum() if "الوزن" in filtered_df.columns else 0
    total_ctns = filtered_df["عدد الكارتون"].sum() if "عدد الكارتون" in filtered_df.columns else 0
    total_volume = filtered_df["حجم"].sum() if "حجم" in filtered_df.columns else 0
    
    client_field_candidates = [c for c in ["الزبون", "الكود", "code", "Shipping mark"] if c in filtered_df.columns]
    total_clients = filtered_df[client_field_candidates[0]].nunique() if client_field_candidates and not filtered_df.empty else 0
    total_containers_count = filtered_df[container_col].nunique() if container_col and container_col in filtered_df.columns and not filtered_df.empty else 0
    
    total_office_paid = filtered_df["Office Paid"].sum() if "Office Paid" in filtered_df.columns else 0
    total_client_paid = filtered_df["Client Paid"].sum() if "Client Paid" in filtered_df.columns else 0
    
    row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4)
    with row1_c1:
        st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">عدد الطلبات / الطرود</div><div class="metric-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
    with row1_c2:
        st.markdown(f'<div class="metric-card" style="background-color: #0f766e;"><div class="metric-title">إجمالي عدد العملاء</div><div class="metric-value">{total_clients:,}</div></div>', unsafe_allow_html=True)
    with row1_c3:
        st.markdown(f'<div class="metric-card" style="background-color: #1d4ed8;"><div class="metric-title">إجمالي عدد الحاويات</div><div class="metric-value">{total_containers_count:,}</div></div>', unsafe_allow_html=True)
    with row1_c4:
        st.markdown(f'<div class="metric-card" style="background-color: #b45309;"><div class="metric-title">إجمالي عدد الكارتون</div><div class="metric-value">{total_ctns:,.0f}</div></div>', unsafe_allow_html=True)
        
    row2_c1, row2_c2, row2_c3, row2_c4 = st.columns(4)
    with row2_c1:
        st.markdown(f'<div class="metric-card" style="background-color: #047857;"><div class="metric-title">إجمالي الوزن (kg)</div><div class="metric-value">{total_weight:,.2f}</div></div>', unsafe_allow_html=True)
    with row2_c2:
        st.markdown(f'<div class="metric-card" style="background-color: #7c2d12;"><div class="metric-title">إجمالي الحجم (m3)</div><div class="metric-value">{total_volume:,.3f}</div></div>', unsafe_allow_html=True)
    with row2_c3:
        st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">مبالغ دفعت من المكتب</div><div class="metric-value">{total_office_paid:,.2f}</div></div>', unsafe_allow_html=True)
    with row2_c4:
        st.markdown(f'<div class="metric-card" style="background-color: #9333ea;"><div class="metric-title">مبالغ دفعت من الزبون</div><div class="metric-value">{total_client_paid:,.2f}</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    render_download_buttons(filtered_df)
    st.dataframe(filtered_df, use_container_width=True)

# بقية الصفحات تعمل بشكل متكامل بناءً على نفس المتغيرات
elif page == "wms_movement":
    st.title("📦 إدارة حركة المخازن والتقرير اليومي (WMS)")
    st.markdown("---")
    daily_file = st.file_uploader("رفع ملف حركة المخازن اليومي (Excel)", type=["xlsx", "xls"], key="wms_uploader")
    wms_df = load_data(daily_file, WMS_FILE)
    if wms_df is not None and not wms_df.empty:
        st.success("تم تحميل تقرير حركة المخازن بنجاح!")
        st.dataframe(wms_df, use_container_width=True)
    else:
        st.info("يرجى رفع ملف حركة المخازن اليومي.")

elif page == "customs":
    st.title("كشف اجور الكمارك")
    st.markdown("---")
    st.dataframe(filtered_df, use_container_width=True)

elif page == "sponsors":
    st.title("الديون على الكفلاء")
    st.markdown("---")
    st.dataframe(filtered_df, use_container_width=True)

elif page == "aging":
    st.title("تقرير أعمار الديون (Aging Report)")
    st.markdown("---")
    st.dataframe(filtered_df, use_container_width=True)

elif page == "collections":
    st.title("نافذة كمرك الشحنات والاستحصالات")
    st.markdown("---")
    st.dataframe(filtered_df, use_container_width=True)

elif page == "charts":
    st.title("لوحة الرسوم البيانية والتحليلات")
    st.markdown("---")
    if not filtered_df.empty and container_col:
        st.bar_chart(filtered_df.groupby(container_col)[["مبلغ الجمرك", "قيمة الاستحصالات"]].sum())
    else:
        st.warning("لا توجد بيانات كافية للرسوم البيانية.")
