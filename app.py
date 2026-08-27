import io
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="شركة أطلس المحيط", page_icon="📦", layout="wide"
)

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
    .block-container { padding-top: 3.5rem !important; padding-bottom: 3rem !important; padding-left: 1rem !important; padding-right: 1rem !important; max-width: 100% !important; }
    [data-testid="stDataFrame"], [data-testid="stTable"], table { width: 100% !important; }
    h1 { background-color: #e2e8f0 !important; color: #0f172a !important; padding: 15px 20px !important; border-radius: 8px !important; margin-bottom: 20px !important; margin-top: 10px !important; }
    [data-testid="stSidebar"] { background-color: #07151a !important; }
    [data-testid="stSidebar"] section div.stRadio label,
    [data-testid="stSidebar"] section div.stRadio p,
    [data-testid="stSidebar"] section div.stRadio span,
    [data-testid="stSidebar"] .element-container label,
    [data-testid="stSidebar"] .element-container span,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #ffffff !important; font-weight: 600 !important; font-size: 18px !important; }
    [data-testid="stSidebar"] [data-testid="stFileUploader"] *, [data-testid="stSidebar"] [data-testid="stButton"] *, [data-testid="stSidebar"] [data-testid="stSelectbox"] * { color: #000000 !important; }
    [data-testid="stSidebar"] button[kind="secondary"] { background-color: #dc2626 !important; color: #ffffff !important; border-color: #dc2626 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = "shipping_data.xlsx"

def clean_numeric(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace("¥", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip(),
        errors="coerce"
    ).fillna(0)

def load_data(uploaded_file):
    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df.to_excel(DATA_FILE, index=False)
            st.sidebar.success("تم حفظ الملف الجديد بنجاح ✔️")
        except Exception as e:
            st.sidebar.error(f"خطأ في قراءة الملف: {e}")

    if df is None and os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE)
        except Exception:
            df = None

    if df is None:
        df = pd.DataFrame(columns=[
            "الشحنة", "الكود", "الوزن", "الحجم", "عدد الطرود", "سعر الكيلو", 
            "اجمالي مبيعات", "الاسم", "رقم الهاتف", "عنوان استلام البظاعة", "نوع الشحنة"
        ])

    df.columns = df.columns.astype(str).str.strip()

    # توحيد اسم عمود الحجم
    vol_col_candidate = next((c for c in df.columns if any(k in c for k in ["الحجم", "حجم", "Volume", "vol"])), None)
    if vol_col_candidate and vol_col_candidate != "الحجم":
        df["الحجم"] = df[vol_col_candidate]
    elif not vol_col_candidate and "الحجم" not in df.columns:
        df["الحجم"] = 0.0

    numeric_cols = [
        "المكتب دفع", "Office Paid", "الزبون دفع", "Client Paid",
        "عدد الطرود", "عدد الكارتون", "الوزن", "الحجم", "حجم", "المجموع", "مبلغ الجمرك", "قيمة الاستحصالات", "عدد الايام"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = clean_numeric(df[col])

    if "مبلغ الجمرك" in df.columns and "قيمة الاستحصالات" in df.columns:
        df["متبقي حقيقي"] = df["مبلغ الجمرك"] - df["قيمة الاستحصالات"]

    return df

st.sidebar.title("🚢 شركة أطلس المحيط")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("📁 رفع ملف Excel جديد", type=["xlsx", "xls"])

if st.sidebar.button("🗑️ مسح بيانات الملف الحالي"):
    if os.path.exists(DATA_FILE):
        try:
            os.remove(DATA_FILE)
            st.sidebar.success("تم مسح بيانات الشيت بنجاح! ✔️")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"خطأ أثناء حذف الملف: {e}")

df = load_data(uploaded_file)
filtered_df = df.copy()

st.sidebar.markdown("### 🔍 الفلاتر الجانبية")
container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات", "الشحنة"] if c in df.columns), None)
selected_container = "الكل"
if container_col and not df.empty:
    containers = ["الكل"] + sorted(df[container_col].dropna().astype(str).unique().tolist())
    selected_container = st.sidebar.selectbox("🚢 اختر رقم الحاوية / الشحنة:", containers)
    if selected_container != "الكل":
        filtered_df = filtered_df[filtered_df[container_col].astype(str) == selected_container]

code_col = next((c for c in ["code", "الكود", "كود"] if c in df.columns), "code")
if code_col in df.columns and not df.empty:
    codes = ["الكل"] + sorted(df[code_col].dropna().astype(str).unique().tolist())
    selected_code = st.sidebar.selectbox("🏷️ اختر الكود (Code):", codes)
    if selected_code != "الكل":
        filtered_df = filtered_df[filtered_df[code_col].astype(str) == selected_code]

st.sidebar.markdown("---")
page_options = {
    "لوحة التحكم (Dashboard)": "dashboard",
    "كشف اجور الكمارك": "customs",
    "الديون على الكفلاء": "sponsors",
    "اعمار الديون (Aging Report)": "aging",
    "كمرك الشحنات والاستحصالات": "collections",
    "الرسوم البيانية": "charts"
}
selected_page_label = st.sidebar.radio("📌 القائمة الرئيسية", list(page_options.keys()))
page = page_options[selected_page_label]

def render_download_buttons(data_to_download):
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            data_to_download.to_excel(writer, index=False, sheet_name='Filtered_Data')
        st.download_button("📊 Download as Excel", buffer.getvalue(), "filtered_details.xlsx", "mime/xlsx")
    with btn_col2:
        st.download_button("📥 Download as CSV", data_to_download.to_csv(index=False).encode('utf-8'), "filtered_details.csv", "text/csv")

if page == "dashboard":
    st.title("📊 لوحة التحكم الرئيسية")
    st.markdown("---")
    
    total_orders = len(filtered_df)
    total_weight = filtered_df["الوزن"].sum() if "الوزن" in filtered_df.columns else 0
    total_volume = filtered_df["الحجم"].sum() if "الحجم" in filtered_df.columns else 0
    ctn_col_name = next((c for c in ["عدد الطرود", "عدد الكارتون"] if c in filtered_df.columns), None)
    total_ctns = filtered_df[ctn_col_name].sum() if ctn_col_name else 0
    
    client_field_candidates = [c for c in ["code", "الكود", "كود", "Shipping mark", "الزبون"] if c in filtered_df.columns]
    total_clients = filtered_df[client_field_candidates[0]].nunique() if client_field_candidates and not filtered_df.empty else 0
    total_containers_count = filtered_df[container_col].nunique() if container_col and container_col in filtered_df.columns and not filtered_df.empty else 0

    row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4)
    with row1_c1:
        st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">📦 عدد الطلبات / الطرود</div><div class="metric-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
    with row1_c2:
        st.markdown(f'<div class="metric-card" style="background-color: #0f766e;"><div class="metric-title">👥 إجمالي عدد العملاء</div><div class="metric-value">{total_clients:,}</div></div>', unsafe_allow_html=True)
    with row1_c3:
        st.markdown(f'<div class="metric-card" style="background-color: #1d4ed8;"><div class="metric-title">🚢 إجمالي الشحنات/الحاويات</div><div class="metric-value">{total_containers_count:,}</div></div>', unsafe_allow_html=True)
    with row1_c4:
        st.markdown(f'<div class="metric-card" style="background-color: #b45309;"><div class="metric-title">📦 إجمالي عدد الطرود</div><div class="metric-value">{total_ctns:,.0f}</div></div>', unsafe_allow_html=True)

    row2_c1, row2_c2, row2_c3, row2_c4 = st.columns(4)
    with row2_c1:
        st.markdown(f'<div class="metric-card" style="background-color: #047857;"><div class="metric-title">⚖️ إجمالي الوزن (kg)</div><div class="metric-value">{total_weight:,.2f}</div></div>', unsafe_allow_html=True)
    with row2_c2:
        st.markdown(f'<div class="metric-card" style="background-color: #7c2d12;"><div class="metric-title">📐 إجمالي الحجم (m³)</div><div class="metric-value">{total_volume:,.3f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    render_download_buttons(filtered_df)
    
    # ترتيب الأعمدة لضمان ظهور عمود "الحجم" بجانب الوزن مباشرة في الجدول
    cols_order = [c for c in ["التسلسل", "الكود", "الاسم", "رقم الهاتف", "عدد الطرود", "الوزن", "الحجم", "عنوان استلام البظاعة", "نوع الشحنة"] if c in filtered_df.columns]
    other_cols = [c for c in filtered_df.columns if c not in cols_order]
    final_display_df = filtered_df[cols_order + other_cols]

    table_height = max(300, min(len(final_display_df) * 35 + 50, 1200))
    st.dataframe(final_display_df, use_container_width=True, height=table_height)
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

else:
    st.title("📌 لوحة التحكم")
    cols_order = [c for c in ["التسلسل", "الكود", "الاسم", "رقم الهاتف", "عدد الطرود", "الوزن", "الحجم", "عنوان استلام البظاعة", "نوع الشحنة"] if c in filtered_df.columns]
    st.dataframe(filtered_df[cols_order + [c for c in filtered_df.columns if c not in cols_order]], use_container_width=True)
