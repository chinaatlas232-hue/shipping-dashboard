import io
import os
import pandas as pd
import streamlit.components.v1 as components
import streamlit as st

# 1. إعداد الصفحة والتنسيقات
st.set_page_config(
    page_title="شركة أطلس المحيط", page_icon="📦", layout="wide"
)

st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    
    /* تنسيق الشريط العلوي */
    header[data-testid="stHeader"] {
        background-color: #07151a !important;
    }
    header[data-testid="stHeader"] * {
        color: #ffffff !important;
    }
    
    /* === تعديل ترويسة الجدول (Headers) بقوة إضافية لتشمل كافة الهياكل الداخلية === */
    [data-testid="stDataFrame"] th, 
    [data-testid="stTable"] th, 
    table th,
    thead tr th,
    .stDataFrame th,
    div[data-testid="stDataFrame"] table thead tr th,
    div[data-testid="stTable"] table thead tr th,
    div[data-baseweb="data-table"] th,
    div.dvn-scroller th {
        background-color: #0b192c !important;
        background: #0b192c !important;
        color: #ffffff !important;
        font-weight: bold !important;
    }
    
    [data-testid="stDataFrame"] th *, 
    [data-testid="stTable"] th *, 
    table th *,
    thead tr th *,
    div[data-testid="stDataFrame"] th span,
    div[data-testid="stDataFrame"] th div {
        color: #ffffff !important;
        font-weight: bold !important;
    }

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
    
    [data-testid="stDataFrame"] div[data-baseweb="block"] {
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

    [data-testid="stTextInput"] label {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #1f2937 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #07151a !important;
    }
    
    [data-testid="stSidebar"] section div.stRadio label,
    [data-testid="stSidebar"] section div.stRadio p,
    [data-testid="stSidebar"] section div.stRadio span,
    [data-testid="stSidebar"] .element-container label,
    [data-testid="stSidebar"] .element-container span,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 18px !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] *, 
    [data-testid="stSidebar"] [data-testid="stButton"] *, 
    [data-testid="stSidebar"] [data-testid="stSelectbox"] *,
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] * {
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stFileUploader"], 
    [data-testid="stSidebar"] [data-testid="stButton"], 
    [data-testid="stSidebar"] [data-testid="stSelectbox"],
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] button[kind="secondary"] {
        background-color: #dc2626 !important;
        color: #ffffff !important;
        border-color: #dc2626 !important;
    }
    
    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: #b91c1c !important;
        color: #ffffff !important;
        border-color: #b91c1c !important;
    }

    ::-webkit-scrollbar {
        width: 10px !important;
        height: 10px !important;
    }
    ::-webkit-scrollbar-track {
        background: #f1f5f9 !important;
        border-radius: 5px !important;
        margin: 5px !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #f87171 !important;
        border-radius: 4px !important;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #ef4444 !important;
    }

    @media print {
        [data-testid="stSidebar"] {
            display: none !important;
        }
        header {
            display: none !important;
        }
        .stDownloadButton, button {
            display: none !important;
        }
    }
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
            "No", "code", "الكفيل", "Shipping mark", "رقم دخول المخزن",
            "المكتب دفع", "الزبون دفع", "المجموع", "عدد الكارتون",
            "الوزن", "حجم", "رقم الحاوية", "مبلغ الجمرك", "قيمة الاستحصالات", "عدد الايام"
        ])

    df.columns = df.columns.astype(str).str.strip()

    office_col_candidate = next((c for c in df.columns if any(k in c for k in ["المكتب دفع", "Office Paid", "دفع الشركة"])), None)
    client_col_candidate = next((c for c in df.columns if any(k in c for k in ["الزبون دفع", "Client Paid", "دفع الزبون"])), None)

    if office_col_candidate and "Office Paid" not in df.columns:
        df["Office Paid"] = df[office_col_candidate]
    if client_col_candidate and "Client Paid" not in df.columns:
        df["Client Paid"] = df[client_col_candidate]

    if "الزبون دفع" in df.columns and "Client Paid" not in df.columns:
        df["Client Paid"] = df["الزبون دفع"]
    elif "Client Paid" in df.columns and "الزبون دفع" not in df.columns:
        df["الزبون دفع"] = df["Client Paid"]

    if "المكتب دفع" in df.columns and "Office Paid" not in df.columns:
        df["Office Paid"] = df["المكتب دفع"]
    elif "Office Paid" in df.columns and "المكتب دفع" not in df.columns:
        df["المكتب دفع"] = df["Office Paid"]

    numeric_cols = [
        "المكتب دفع", "Office Paid", "الزبون دفع", "Client Paid",
        "عدد الكارتون", "الوزن", "حجم", "المجموع", "مبلغ الجمرك", "قيمة الاستحصالات", "عدد الايام"
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
    else:
        st.sidebar.info("لا توجد بيانات مسجلة مسبقاً.")

df = load_data(uploaded_file)
filtered_df = df.copy()

st.sidebar.markdown("### 🔍 الفلاتر الجانبية")

container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in df.columns), None)
selected_container = "الكل"
if container_col and not df.empty:
    containers = ["الكل"] + sorted(df[container_col].dropna().astype(str).unique().tolist())
    selected_container = st.sidebar.selectbox("🚢 اختر رقم الحاوية:", containers)
    if selected_container != "الكل":
        filtered_df = filtered_df[filtered_df[container_col].astype(str) == selected_container]

code_col = next((c for c in ["code", "الكود", "كود"] if c in df.columns), "code")
selected_code = "الكل"
if code_col in df.columns and not df.empty:
    codes = ["الكل"] + sorted(df[code_col].dropna().astype(str).unique().tolist())
    selected_code = st.sidebar.selectbox("🏷️ اختر الكود (Code):", codes)
    if selected_code != "الكل":
        filtered_df = filtered_df[filtered_df[code_col].astype(str) == selected_code]

sponsor_filter_col = next((c for c in ["الكفيل", "كفيل"] if c in df.columns), None)
selected_sponsor = "الكل"
if sponsor_filter_col and not df.empty:
    sponsors = ["الكل"] + sorted(df[sponsor_filter_col].dropna().astype(str).unique().tolist())
    selected_sponsor = st.sidebar.selectbox("👤 اختر اسم الكفيل:", sponsors)
    if selected_sponsor != "الكل":
        filtered_df = filtered_df[filtered_df[sponsor_filter_col].astype(str) == selected_sponsor]

st.sidebar.markdown("---")

st.sidebar.markdown("### 👁️ التحكم بأعمدة العرض")
all_columns = filtered_df.columns.tolist()
selected_columns = st.sidebar.multiselect(
    "اختر الأعمدة المراد إظهارها:",
    options=all_columns,
    default=all_columns
)

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

st.sidebar.markdown("---")
st.sidebar.info("النظام يعمل بكفاءة ✔️")

def render_download_buttons(data_to_download):
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            data_to_download.to_excel(writer, index=False, sheet_name='Filtered_Data')
        st.download_button(
            label="📊 Download as Excel",
            data=buffer.getvalue(),
            file_name="filtered_details.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    with btn_col2:
        print_html = """
            <div>
                <button onclick="window.parent.print();" style="
                    background-color: #ff4b4b;
                    color: white;
                    padding: 0.45rem 0.75rem;
                    border: none;
                    border-radius: 0.3rem;
                    font-weight: 500;
                    cursor: pointer;
                    width: 100%;
                    font-size: 14px;
                    font-family: inherit;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                ">
                    📄 طباعة / حفظ كـ PDF
                </button>
            </div>
        """
        components.html(print_html, height=45)

def style_container_column(df_to_style):
    target_container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in df_to_style.columns), None)
    sponsor_col_check = "الكفيل" if "الكفيل" in df_to_style.columns else None

    format_dict = {}
    currency_keywords = ["مبلغ", "قيمة", "المجموع", "دفع", "سعر", "الاستحصالات", "المتبقي"]
    for col in df_to_style.columns:
        if pd.api.types.is_numeric_dtype(df_to_style[col]):
            if any(kw in col for kw in currency_keywords):
                format_dict[col] = "¥{:,.2f}"
            else:
                format_dict[col] = "{:,.2f}"

    styler = df_to_style.style.format(format_dict, na_rep="")

    if not target_container_col:
        return styler

    def highlight_cells(row):
        styles = [''] * len(row)
        if target_container_col in df_to_style.columns:
            col_idx = df_to_style.columns.get_loc(target_container_col)
            is_arrived = False
            is_not_arrived = False
            
            if sponsor_col_check and sponsor_col_check in row:
                sponsor_val = str(row[sponsor_col_check]).strip()
                if "لم تصل بعد" in sponsor_val:
                    is_not_arrived = True
                elif sponsor_val and sponsor_val != "nan" and sponsor_val != "غير محدد":
                    is_arrived = True
            
            # تم إضافة !important لضمان إجبار المتصفح على تطبيق الألوان
            if is_not_arrived:
                styles[col_idx] = 'background-color: #fef08a !important; color: #000000 !important; font-weight: bold;'
            elif is_arrived:
                styles[col_idx] = 'background-color: #bbf7d0 !important; color: #000000 !important; font-weight: bold;'
                
        return styles

    return styler.apply(highlight_cells, axis=1)

if page == "dashboard":
    st.title("📊 لوحة التحكم الرئيسية")
    st.markdown("---")
    
    total_orders = len(filtered_df)
    total_weight = filtered_df["الوزن"].sum() if "الوزن" in filtered_df.columns else 0
    total_ctns = filtered_df["عدد الكارتون"].sum() if "عدد الكارتون" in filtered_df.columns else 0
    total_volume = filtered_df["حجم"].sum() if "حجم" in filtered_df.columns else 0
    
    client_field_candidates = [c for c in ["code", "الكود", "كود", "Shipping mark", "الزبون"] if c in filtered_df.columns]
    total_clients = filtered_df[client_field_candidates[0]].nunique() if client_field_candidates and not filtered_df.empty else 0
    total_containers_count = filtered_df[container_col].nunique() if container_col and container_col in filtered_df.columns and not filtered_df.empty else 0

    office_paid_col = next((c for c in ["Office Paid", "المكتب دفع"] if c in filtered_df.columns), None)
    client_paid_col = next((c for c in ["Client Paid", "الزبون دفع"] if c in filtered_df.columns), None)
    
    total_office_paid = filtered_df[office_paid_col].sum() if office_paid_col else 0
    total_client_paid = filtered_df[client_paid_col].sum() if client_paid_col else 0

    row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4)
    with row1_c1:
        st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">📦 عدد الطلبات / الطرود</div><div class="metric-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
    with row1_c2:
        st.markdown(f'<div class="metric-card" style="background-color: #0f766e;"><div class="metric-title">👥 إجمالي عدد العملاء</div><div class="metric-value">{total_clients:,}</div></div>', unsafe_allow_html=True)
    with row1_c3:
        st.markdown(f'<div class="metric-card" style="background-color: #1d4ed8;"><div class="metric-title">🚢 إجمالي عدد الحاويات</div><div class="metric-value">{total_containers_count:,}</div></div>', unsafe_allow_html=True)
    with row1_c4:
        st.markdown(f'<div class="metric-card" style="background-color: #b45309;"><div class="metric-title">📦 إجمالي عدد الكارتون</div><div class="metric-value">{total_ctns:,.2f}</div></div>', unsafe_allow_html=True)

    row2_c1, row2_c2, row2_c3, row2_c4 = st.columns(4)
    with row2_c1:
        st.markdown(f'<div class="metric-card" style="background-color: #047857;"><div class="metric-title">⚖️ إجمالي الوزن (kg)</div><div class="metric-value">{total_weight:,.2f}</div></div>', unsafe_allow_html=True)
    with row2_c2:
        st.markdown(f'<div class="metric-card" style="background-color: #7c2d12;"><div class="metric-title">📐 إجمالي الحجم (m³)</div><div class="metric-value">{total_volume:,.2f}</div></div>', unsafe_allow_html=True)
    with row2_c3:
        st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">💰 مبالغ دفعت من المكتب</div><div class="metric-value">¥{total_office_paid:,.2f}</div></div>', unsafe_allow_html=True)
    with row2_c4:
        st.markdown(f'<div class="metric-card" style="background-color: #9333ea;"><div class="metric-title">👤 مبالغ دفعت من الزبون</div><div class="metric-value">¥{total_client_paid:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    render_download_buttons(filtered_df)
    
    df_to_display = filtered_df[selected_columns] if selected_columns else filtered_df
    styled_filtered_df = style_container_column(df_to_display)
    table_height = max(300, min(len(filtered_df) * 35 + 50, 1200))
    st.dataframe(styled_filtered_df, use_container_width=True, height=table_height)
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "customs":
    st.title("💰 كشف اجور الكمارك")
    st.markdown("---")
    
    search_query = st.text_input("🔍 بحث ذكي (ابحث برقم الكود، اسم الكفيل، أو رقم الحاوية):", "").strip()
    pivot_filtered_df = filtered_df.copy()
    
    if search_query and not pivot_filtered_df.empty:
        search_cols = [c for c in ["code", "الكفيل", "رقم الحاوية", "رقم الحاويات"] if c in pivot_filtered_df.columns]
        if search_cols:
            mask = pivot_filtered_df[search_cols].apply(lambda col: col.astype(str).str.contains(search_query, case=False, na=False))
            pivot_filtered_df = pivot_filtered_df[mask.any(axis=1)]

    total_customs = pivot_filtered_df["مبلغ الجمرك"].sum() if "مبلغ الجمرك" in pivot_filtered_df and not pivot_filtered_df.empty else 0.0
    total_collected = pivot_filtered_df["قيمة الاستحصالات"].sum() if "قيمة الاستحصالات" in pivot_filtered_df and not pivot_filtered_df.empty else 0.0
    total_remaining = pivot_filtered_df["متبقي حقيقي"].sum() if "متبقي حقيقي" in pivot_filtered_df and not pivot_filtered_df.empty else 0.0

    not_arrived_remaining = 0.0
    if "الكفيل" in pivot_filtered_df.columns and not pivot_filtered_df.empty:
        not_arrived_remaining = pivot_filtered_df[pivot_filtered_df["الكفيل"].astype(str).str.contains("لم تصل بعد", na=False)]["متبقي حقيقي"].sum()

    arrived_remaining = total_remaining - not_arrived_remaining

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">أجور الجمرك الكلي</div><div class="metric-value">¥{total_customs:,.2f}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card" style="background-color: #0f766e;"><div class="metric-title">إجمالي المتبقي الحقيقي</div><div class="metric-value">¥{total_remaining:,.2f}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">إجمالي الاستحصالات (المسدد)</div><div class="metric-value">¥{total_collected:,.2f}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card" style="background-color: #dc2626;"><div class="metric-title">متبقي (لم تصل بعد)</div><div class="metric-value">¥{not_arrived_remaining:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 جدول ملخص أجور الكمارك والاستحصالات حسب الكود")
    
    pivot_code_col = next((c for c in ["code", "الكود", "كود"] if c in filtered_df.columns), None)
    
    if pivot_code_col and not pivot_filtered_df.empty:
        base_pivot_df = pivot_filtered_df.copy()

        customs_summary = base_pivot_df.groupby(pivot_code_col, dropna=False).agg({
            "عدد الكارتون": "sum",
            "مبلغ الجمرك": "sum",
            "قيمة الاستحصالات": "sum",
            "متبقي حقيقي": "sum"
        }).reset_index()

        grand_total_row = pd.DataFrame({
            pivot_code_col: ["Grand Total"],
            "عدد الكارتون": [customs_summary["عدد الكارتون"].sum()],
            "مبلغ الجمرك": [customs_summary["مبلغ الجمرك"].sum()],
            "قيمة الاستحصالات": [customs_summary["قيمة الاستحصالات"].sum()],
            "متبقي حقيقي": [customs_summary["متبقي حقيقي"].sum()]
        })

        customs_summary = pd.concat([customs_summary, grand_total_row], ignore_index=True)

        customs_summary = customs_summary.rename(columns={
            pivot_code_col: "Row Labels",
            "عدد الكارتون": "Sum of عدد الكارتون",
            "مبلغ الجمرك": "Sum of مبلغ الجمرك",
            "قيمة الاستحصالات": "Sum of قيمة الاستحصالات",
            "متبقي حقيقي": "Sum of متبقي حقيقي"
        })

        formatted_customs = customs_summary.copy()
        for col in ["Sum of مبلغ الجمرك", "Sum of قيمة الاستحصالات", "Sum of متبقي حقيقي"]:
            if col in formatted_customs.columns:
                formatted_customs[col] = formatted_customs[col].apply(lambda x: f"¥{x:,.2f}" if isinstance(x, (int, float)) else x)

        def style_customs_table(row):
            styles = [''] * len(row)
            if str(row["Row Labels"]) == "Grand Total":
                return ['background-color: #e2e8f0 !important; color: #000000 !important; font-weight: bold;'] * len(row)
            return styles

        styled_customs_table = formatted_customs.style.apply(style_customs_table, axis=1)

        render_download_buttons(customs_summary)
        table_height = max(300, min(len(formatted_customs) * 35 + 50, 1200))
        st.dataframe(styled_customs_table, use_container_width=True, height=table_height)
    else:
        st.warning("الأعمدة المطلوبة لإنشاء الجدول غير متوفرة أو البيانات فارغة.")

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "sponsors":
    st.title("👥 الديون على الكفلاء")
    st.markdown("---")
    
    if "الكفيل" in filtered_df.columns and not filtered_df.empty:
        col_customs = "مبلغ الجمرك" if "مبلغ الجمرك" in filtered_df.columns else filtered_df.columns[0]
        col_collected = "قيمة الاستحصالات" if "قيمة الاستحصالات" in filtered_df.columns else filtered_df.columns[0]
        col_remaining = "متبقي حقيقي" if "متبقي حقيقي" in filtered_df.columns else filtered_df.columns[0]
        col_count = "No" if "No" in filtered_df.columns else filtered_df.columns[0]

        sponsor_summary = filtered_df.groupby("الكفيل").agg(
            total_customs=(col_customs, "sum"),
            total_collected=(col_collected, "sum"),
            total_remaining=(col_remaining, "sum"),
            total_orders=(col_count, "count")
        ).reset_index()

        st.markdown("### 📋 ملخص المبالغ لكل كفيل")
        
        for index, row in sponsor_summary.iterrows():
            sponsor_name = row["الكفيل"]
            s_customs = row["total_customs"]
            s_collected = row["total_collected"]
            s_remaining = row["total_remaining"]
            s_orders = row["total_orders"]
            
            card_bg = "#1e3a8a"
            if "لم تصل بعد" in str(sponsor_name):
                card_bg = "#b45309"
            
            st.markdown(f"""
                <div style="background-color: {card_bg}; padding: 15px; border-radius: 10px; color: white; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="margin: 0 0 10px 0; font-size: 18px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 5px; color: #ffffff !important;">👤 الكفيل: {sponsor_name}</h3>
                    <div style="display: flex; justify-content: space-between; font-size: 15px; text-align: center; color: #ffffff !important;">
                        <div>📦 الطلبات: <b style="color: #ffffff;">{s_orders:,.2f}</b></div>
                        <div>💰 الجمرك: <b style="color: #ffffff;">¥{s_customs:,.2f}</b></div>
                        <div>✅ المسدد: <b style="color: #ffffff;">¥{s_collected:,.2f}</b></div>
                        <div>⏳ المتبقي: <b style="color: #ffffff;">¥{s_remaining:,.2f}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### 📊 جدول تفصيلي بملخص الكفلاء (Pivot Table)")
        
        pivot_code_col = next((c for c in ["code", "الكود", "كود"] if c in filtered_df.columns), None)
        pivot_container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in filtered_df.columns), None)
        pivot_value_col = "متبقي حقيقي" if "متبقي حقيقي" in filtered_df.columns else None

        if pivot_code_col and pivot_container_col and pivot_value_col:
            base_pivot_df = df.copy()
            
            if selected_code != "الكل":
                base_pivot_df = base_pivot_df[base_pivot_df[pivot_code_col].astype(str) == selected_code]
            if selected_sponsor != "الكل" and "الكفيل" in base_pivot_df.columns:
                base_pivot_df = base_pivot_df[base_pivot_df["الكفيل"].astype(str) == selected_sponsor]

            pivot_table_df = base_pivot_df.pivot_table(
                index=pivot_code_col,
                columns=pivot_container_col,
                values=pivot_value_col,
                aggfunc="sum",
                fill_value=0
            )

            pivot_table_df = pivot_table_df.loc[(pivot_table_df > 0).any(axis=1), (pivot_table_df > 0).any(axis=0)]

            pivot_table_df["Grand Total"] = pivot_table_df.sum(axis=1)
            grand_total_row = pivot_table_df.sum(axis=0)
            pivot_table_df.loc["Grand Total"] = grand_total_row

            new_columns = []
            for col in pivot_table_df.columns:
                if col == "Grand Total":
                    new_columns.append(col)
                    continue
                
                sub_df = base_pivot_df[base_pivot_df[pivot_container_col].astype(str) == str(col)]
                is_not_arrived = False
                if not sub_df.empty and "الكفيل" in sub_df.columns:
                    sponsors_in_col = sub_df["الكفيل"].astype(str).unique()
                    if any("لم تصل بعد" in str(s) for s in sponsors_in_col):
                        is_not_arrived = True
                
                bg_color = "#fef08a" if is_not_arrived else "#bbf7d0"
                html_col_name = f'<div style="background-color: {bg_color}; padding: 4px 8px; border-radius: 4px; color: black; font-weight: bold; text-align: center;">{col}</div>'
                new_columns.append(html_col_name)

            pivot_table_df.columns = new_columns

            formatted_pivot = pivot_table_df.map(
                lambda val: f"¥{val:,.2f}" if isinstance(val, (int, float)) and val > 0 else ""
            )
            
            def style_pivot_cells(val):
                if val == "":
                    return 'background-color: #f8fafc !important; color: transparent !important;'
                return 'background-color: #fce7f3 !important; color: #000000 !important; font-weight: bold;'

            styled_matrix = formatted_pivot.style.map(style_pivot_cells)
            matrix_html = styled_matrix.to_html(escape=False).replace('<table id', '<table style="width: 100%;" id')
            st.markdown(f'<div style="width: 100%; overflow-x: auto;">{matrix_html}</div>', unsafe_allow_html=True)
        else:
            st.warning("الأعمدة المطلوبة لإنشاء جدول البايفت غير متوفرة بالكامل.")

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "aging":
    st.title("⏳ تقرير أعمار الديون (Aging Report)")
    st.markdown("---")
    st.markdown("### 📋 جدول تحليلي يوزع المتبقي الحقيقي حسب الكود ورقم الحاوية وأيام التأخير (بدون 0 يوم)")

    aging_df = filtered_df.copy()
    code_field = next((c for c in ["code", "الكود", "كود"] if c in aging_df.columns), None)
    
    if not aging_df.empty and "رقم الحاوية" in aging_df.columns and "عدد الايام" in aging_df.columns and "متبقي حقيقي" in aging_df.columns:
        
        aging_df["عدد الايام"] = pd.to_numeric(aging_df["عدد الايام"], errors="coerce").fillna(0).astype(int)
        aging_df = aging_df[aging_df["عدد الايام"] > 0]
        
        index_cols = [code_field, "رقم الحاوية"] if code_field else ["رقم الحاوية"]
        
        aging_pivot = aging_df.pivot_table(
            index=index_cols,
            columns="عدد الايام",
            values="متبقي حقيقي",
            aggfunc="sum",
            fill_value=0
        )

        aging_pivot = aging_pivot[(aging_pivot > 0).any(axis=1)]

        aging_pivot["Grand Total"] = aging_pivot.sum(axis=1)
        aging_grand_total = aging_pivot.sum(axis=0)
        
        if code_field:
            aging_pivot.loc[("Grand Total", "")] = aging_grand_total
        else:
            aging_pivot.loc["Grand Total"] = aging_grand_total

        formatted_aging = aging_pivot.map(
            lambda val: f"¥{val:,.2f}" if isinstance(val, (int, float)) and val > 0 else ""
        )

        def style_aging_cells(row):
            styles = []
            is_total_row = False
            idx_val = row.name
            if idx_val == "Grand Total" or (isinstance(idx_val, tuple) and idx_val[0] == "Grand Total"):
                is_total_row = True
                
            for val in row:
                if is_total_row:
                    styles.append('background-color: #e2e8f0 !important; color: #0f172a !important; font-weight: bold; text-align: center;')
                elif val == "":
                    styles.append('background-color: #f8fafc !important; color: transparent !important; text-align: center;')
                else:
                    styles.append('background-color: #ffffff !important; color: #000000 !important; font-weight: bold; text-align: center;')
            return styles

        styled_aging_matrix = formatted_aging.style.apply(style_aging_cells, axis=1).set_table_styles([
            {"selector": "th", "props": [("text-align", "center"), ("vertical-align", "middle")]}
        ])
        render_download_buttons(aging_pivot.reset_index())
        
        aging_html = styled_aging_matrix.to_html(escape=False).replace('<table id', '<table style="width: 100%; text-align: center;" id')
        st.markdown(f'<div style="width: 100%; overflow-x: auto; text-align: center;">{aging_html}</div>', unsafe_allow_html=True)
    else:
        st.warning("عذراً، الأعمدة الأساسية المطلوبة غير متوفرة بالكامل في البيانات الحالية.")

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "collections":
    st.title("🛃 نافذة كمرك الشحنات والاستحصالات")
    st.markdown("---")
    st.markdown("### 📋 ملخص الحاويات حسب مبالغ الجمرك والاستحصالات والمتبقي الحقيقي")

    if not filtered_df.empty:
        total_c = filtered_df["مبلغ الجمرك"].sum() if "مبلغ الجمرك" in filtered_df.columns else 0
        total_coll = filtered_df["قيمة الاستحصالات"].sum() if "قيمة الاستحصالات" in filtered_df.columns else 0
        total_rem = filtered_df["متبقي حقيقي" if "متبقي حقيقي" in filtered_df.columns else filtered_df.columns[0]].sum() if "متبقي حقيقي" in filtered_df.columns else 0

        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">إجمالي مبالغ الجمرك</div><div class="metric-value">¥{total_c:,.2f}</div></div>', unsafe_allow_html=True)
        with mc2:
            st.markdown(f'<div class="metric-card" style="background-color: #059669;"><div class="metric-title">إجمالي الاستحصالات</div><div class="metric-value">¥{total_coll:,.2f}</div></div>', unsafe_allow_html=True)
        with mc3:
            st.markdown(f'<div class="metric-card" style="background-color: #d97706;"><div class="metric-title">إجمالي المتبقي الحقيقي</div><div class="metric-value">¥{total_rem:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    render_download_buttons(filtered_df)

    container_field = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in filtered_df.columns), None)
    
    if container_field and not filtered_df.empty:
        agg_df = filtered_df.groupby(container_field, dropna=False).agg(
            {
                "مبلغ الجمرك": "sum",
                "قيمة الاستحصالات": "sum",
                "متبقي حقيقي": "sum"
            }
        ).reset_index()

        grand_totals = pd.DataFrame({
            container_field: ["Grand Total"],
            "مبلغ الجمرك": [agg_df["مبلغ الجمرك"].sum()],
            "قيمة الاستحصالات": [agg_df["قيمة الاستحصالات"].sum()],
            "متبقي حقيقي": [agg_df["متبقي حقيقي"].sum()]
        })
        
        agg_df = pd.concat([agg_df, grand_totals], ignore_index=True)

        agg_df = agg_df.rename(columns={
            container_field: "رقم الحاوية",
            "مبلغ الجمرك": "Sum of مبلغ الجمرك",
            "قيمة الاستحصالات": "Sum of قيمة الاستحصالات",
            "متبقي حقيقي": "Sum of متبقي حقيقي"
        })

        formatted_agg = agg_df.copy()
        for col in ["Sum of مبلغ الجمرك", "Sum of قيمة الاستحصالات", "Sum of متبقي حقيقي"]:
            formatted_agg[col] = formatted_agg[col].apply(lambda x: f"¥{x:,.2f}" if x > 0 else "")

        def style_summary_cells(row):
            styles = [''] * len(row)
            container_val = str(row["رقم الحاوية"])
            
            if container_val == "Grand Total":
                return ['background-color: #f1f5f9 !important; color: #000000 !important; font-weight: bold;'] * len(row)
            
            container_col_name = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in filtered_df.columns), None)
            if container_col_name and "الكفيل" in filtered_df.columns:
                sub_df = filtered_df[filtered_df[container_col_name].astype(str) == container_val]
                is_arrived = False
                is_not_arrived = False
                
                if not sub_df.empty:
                    sponsors_in_col = sub_df["الكفيل"].astype(str).unique()
                    if any("لم تصل بعد" in str(s) for s in sponsors_in_col):
                        is_not_arrived = True
                    elif any(s and s != "nan" and s != "غير محدد" for s in sponsors_in_col):
                        is_arrived = True
                
                col_idx = row.index.get_loc("رقم الحاوية")
                if is_not_arrived:
                    styles[col_idx] = 'background-color: #fef08a !important; color: #000000 !important; font-weight: bold;'
                elif is_arrived:
                    styles[col_idx] = 'background-color: #bbf7d0 !important; color: #000000 !important; font-weight: bold;'
            
            return styles

        styled_summary = formatted_agg.style.apply(style_summary_cells, axis=1)

        summary_height = max(300, min(len(formatted_agg) * 35 + 50, 1200))
        st.dataframe(styled_summary, use_container_width=True, height=summary_height)
    else:
        st.warning("عذراً، عمود رقم الحاوية غير متوفر في البيانات أو البيانات فارغة.")

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "charts":
    st.title("📈 لوحة الرسوم البيانية والتحليلات")
    st.markdown("---")

    if filtered_df.empty:
        st.warning("لا توجد بيانات متاحة لعرض الرسوم البيانية.")
    else:
        if container_col and "مبلغ الجمرك" in filtered_df.columns:
            st.subheader("📦 مقارنة مبالغ الجمرك والاستحصالات حسب الحاويات")
            chart_data = filtered_df.groupby(container_col)[["مبلغ الجمرك", "قيمة الاستحصالات", "متبقي حقيقي"]].sum()
            st.bar_chart(chart_data)
            st.markdown("---")

        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            if container_col and "الوزن" in filtered_df.columns:
                st.subheader("⚖️ إجمالي الوزن حسب الحاوية (kg)")
                weight_data = filtered_df.groupby(container_col)["الوزن"].sum()
                st.bar_chart(weight_data)

        with col_chart2:
            if container_col and "حجم" in filtered_df.columns:
                st.subheader("📐 إجمالي الحجم حسب الحاوية (m³)")
                volume_data = filtered_df.groupby(container_col)["حجم"].sum()
                st.bar_chart(volume_data)

        st.markdown("---")

        if "الكفيل" in filtered_df.columns and "مبلغ الجمرك" in filtered_df.columns:
            st.subheader("👤 إجمالي مبالغ الجمرك والاستحصالات حسب الكفلاء")
            sponsor_chart_data = filtered_df.groupby("الكفيل")[["مبلغ الجمرك", "قيمة الاستحصالات"]].sum()
            st.bar_chart(sponsor_chart_data)

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
