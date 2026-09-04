import io
import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# 1. إعداد الصفحة والتنسيقات
st.set_page_config(
    page_title="شركة أطلس المحيط", page_icon="📦", layout="wide"
)

st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    
    /* تنسيق جدول HTML المخصص */
    .custom-html-table {
        width: 100% !important;
        border-collapse: collapse !important;
        direction: rtl !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #ffffff;
        color: #000000;
        margin-bottom: 20px;
    }
    .custom-html-table th {
        background-color: #0b2239 !important;
        color: #ffffff !important;
        text-align: center !important;
        font-weight: bold !important;
        padding: 8px 4px !important;
        border: 1px solid #cbd5e1 !important;
        font-size: 12px !important;
    }
    .custom-html-table td {
        text-align: center !important;
        padding: 6px 4px !important;
        border: 1px solid #cbd5e1 !important;
        font-size: 11px !important;
        color: #1e293b !important;
    }

    .metric-card {
        padding: 16px; border-radius: 12px; color: white;
        text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .metric-title { font-size: 14px; margin-bottom: 6px; opacity: 0.95; font-weight: 600; direction: rtl; unicode-bidi: embed; }
    .metric-value { font-size: 20px; font-weight: bold; }
    
    .block-container { 
        padding-top: 2rem !important; 
        padding-bottom: 2rem !important; 
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
        max-width: 100% !important; 
        direction: rtl !important;
    }

    h1 {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        padding: 15px 20px !important;
        border-radius: 8px !important;
        margin-bottom: 20px !important;
        margin-top: 10px !important;
        text-align: right !important;
    }

    [data-testid="stSidebar"] {
        background-color: #07151a !important;
        direction: rtl !important;
        padding-top: 1rem !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        text-align: right !important;
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
        font-size: 16px !important;
        text-align: right !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] *, 
    [data-testid="stSidebar"] [data-testid="stButton"] *, 
    [data-testid="stSidebar"] [data-testid="stSelectbox"] *,
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] * {
        color: #000000 !important;
        text-align: right !important;
    }

    [data-testid="stSidebar"] button[kind="secondary"] {
        background-color: #dc2626 !important;
        color: #ffffff !important;
        border-color: #dc2626 !important;
        width: 100% !important;
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

    /* تعديلات الطباعة العامة */
    @media print {
        @page {
            size: A4 landscape;
            margin: 5mm !important;
        }
        
        html, body {
            height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            background-color: #ffffff !important;
            -webkit-print-color-adjust: exact !important;
        }

        [data-testid="stSidebar"],
        header,
        .no-print,
        div[data-testid="stTextInput"],
        iframe {
            display: none !important;
            height: 0 !important;
            max-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .main, .block-container {
            background-color: #ffffff !important;
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            width: 100% !important;
            display: block !important;
            position: relative !important;
        }

        .metric-card {
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            box-shadow: none !important;
            border: 1px solid #cbd5e1 !important;
            margin-bottom: 10px !important;
        }

        h1 {
            margin-top: 0 !important;
            margin-bottom: 10px !important;
            padding: 8px 12px !important;
            font-size: 14px !important;
            background-color: #1e293b !important;
            color: #ffffff !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            page-break-after: avoid !important;
            break-after: avoid !important;
        }

        .custom-html-table {
            width: 100% !important;
            font-size: 9px !important;
            border-collapse: collapse !important;
            margin: 0 !important;
        }

        thead {
            display: table-header-group !important;
        }

        tr {
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }

        .custom-html-table th {
            background-color: #0b2239 !important;
            color: #ffffff !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            padding: 4px !important;
        }

        .custom-html-table td {
            padding: 3px 2px !important;
            font-size: 9px !important;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }
    }
    </style>
""",
    unsafe_allow_html=True,
)

def clean_numeric(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace("¥", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip(),
        errors="coerce"
    ).fillna(0)

@st.cache_data(ttl=60)
def load_data():
    df = None
    try:
        sheet_id = "1amOmnZgzn2bhWTgje_9W2sUK6V-OygWk"
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df = pd.read_csv(sheet_url)
    except Exception as e:
        st.sidebar.error(f"خطأ في الاتصال بملف Google Sheets: {e}")

    if df is None or df.empty:
        df = pd.DataFrame(columns=[
            "No", "code", "الكفيل", "Shipping mark", "رقم دخول المخزن",
            "المكتب دفع", "الزبون دفع", "المجموع", "عدد الكارتون",
            "الوزن", "حجم", "رقم الحاوية", "مبلغ الجمرك", "قيمة الاستحصالات", "عدد الايام", "سعر البيع"
        ])

    df.columns = df.columns.astype(str).str.strip()

    for col in df.columns:
        if any(kw in str(col).lower() for kw in ["تاريخ", "date"]):
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d").fillna(df[col])

    office_col_candidate = next((c for c in df.columns if any(k in str(c) for k in ["المكتب دفع", "Office Paid", "دفع الشركة"])), None)
    client_col_candidate = next((c for c in df.columns if any(k in str(c) for k in ["الزبون دفع", "Client Paid", "دفع الزبون"])), None)

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
        "عدد الكارتون", "الوزن", "حجم", "المجموع", "مبلغ الجمرك", "قيمة الاستحصالات", "عدد الايام", "سعر البيع"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = clean_numeric(df[col])

    if "مبلغ الجمرك" in df.columns and "قيمة الاستحصالات" in df.columns:
        df["متبقي حقيقي"] = df["مبلغ الجمرك"] - df["قيمة الاستحصالات"]

    return df

st.sidebar.title("🚢 شركة أطلس المحيط")
st.sidebar.markdown("---")

if st.sidebar.button("🔄 تحديث البيانات من جوجل شيت"):
    st.cache_data.clear()
    st.rerun()

if "df_updated" in st.session_state:
    df = st.session_state["df_updated"]
else:
    df = load_data()

filtered_df = df.copy()

st.sidebar.markdown("### 🔍 الفلاتر الجانبية")

container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in df.columns), None)
selected_container = "الكل"
if container_col and not df.empty:
    containers = ["الكل"] + sorted(df[container_col].dropna().astype(str).unique().tolist())
    selected_container = st.sidebar.selectbox("🚢 اختر رقم الحاوية:", containers, key="selected_container_key")
    if selected_container != "الكل":
        filtered_df = filtered_df[filtered_df[container_col].astype(str) == selected_container]

code_col = next((c for c in ["code", "الكود", "كود"] if c in df.columns), "code")
selected_code = "الكل"
if code_col in df.columns and not df.empty:
    codes = ["الكل"] + sorted(df[code_col].dropna().astype(str).unique().tolist())
    selected_code = st.sidebar.selectbox("🏷️ اختر الكود (Code):", codes, key="selected_code_key")
    if selected_code != "الكل":
        filtered_df = filtered_df[filtered_df[code_col].astype(str) == selected_code]

sponsor_filter_col = next((c for c in ["الكفيل", "كفيل"] if c in df.columns), None)
selected_sponsor = "الكل"
if sponsor_filter_col and not df.empty:
    sponsors = ["الكل"] + sorted(df[sponsor_filter_col].dropna().astype(str).unique().tolist())
    selected_sponsor = st.sidebar.selectbox("👤 اختر اسم الكفيل:", sponsors, key="selected_sponsor_key")
    if selected_sponsor != "الكل":
        filtered_df = filtered_df[filtered_df[sponsor_filter_col].astype(str) == selected_sponsor]

st.sidebar.markdown("---")

default_columns_to_show = [
    "No", "code", "Shipping mark", "عدد الكارتون", "الوزن", "حجم", 
    "رقم الحاوية", "الكفيل", "المجموع", "الزبون دفع", "المكتب دفع", "نقل داخلي", 
    "سعر البيع", "مبلغ الجمرك", "قيمة الاستحصالات", "متبقي حقيقي", 
    "تاريخ التوزيع", "عدد الايام"
]

page_options = {
    "لوحة التحكم (Dashboard)": "dashboard",
    "كشف اجور الكمارك": "customs",
    "الديون على الكفلاء": "sponsors",
    "اعمار الديون (Aging Report)": "aging",
    "كمرك الشحنات والاستحصالات": "collections",
    "توزيع البضاعة داخل الحاويات": "distribution",
    "الرسوم البيانية": "charts",
    "إدخال وتعديل البيانات": "data_entry"
}

selected_page_label = st.sidebar.radio("📌 القائمة الرئيسية", list(page_options.keys()), key="selected_page_label_key")
page = page_options[selected_page_label]

st.sidebar.markdown("---")
st.sidebar.info("متصل بملف Google Sheets بنجاح ✔️")

def render_download_buttons(data_to_download):
    st.markdown('<div class="no-print" style="margin-bottom: 10px;">', unsafe_allow_html=True)
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            data_to_download.to_excel(writer, index=False, sheet_name='Filtered_Data')
        st.download_button(
            label="📊 Download as Excel",
            data=buffer.getvalue(),
            file_name="filtered_details.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with btn_col2:
        components.html("""
            <div style="display: flex; justify-content: center; align-items: center; height: 100%; margin: 0;">
                <button onclick="window.parent.print();" style="
                    width: 100%;
                    background-color: #ffffff;
                    color: #262730;
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    padding: 0.5rem 0.75rem;
                    border-radius: 0.5rem;
                    font-weight: 400;
                    font-size: 14px;
                    cursor: pointer;
                    text-align: center;
                    display: inline-flex;
                    justify-content: center;
                    align-items: center;
                    gap: 5px;
                    height: 42px;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    box-shadow: rgba(0, 0, 0, 0.02) 0px 1px 3px 0px;
                ">
                    🖨️ طباعة الصفحة الحالية
                </button>
            </div>
        """, height=50)
    st.markdown('</div>', unsafe_allow_html=True)

def display_custom_html_table(df_to_render, is_sponsors_pivot=False, is_aging_report=False):
    if df_to_render.empty:
        st.info("لا توجد بيانات للعرض.")
        return
        
    df_with_seq = df_to_render.copy()
    
    has_grand_total = any(str(val).strip() in ["Grand Total", "GrandTotal"] for val in df_with_seq.iloc[:, 0].values) if not df_with_seq.empty else False

    if not is_sponsors_pivot and not has_grand_total:
        seq_list = []
        for _, row in df_with_seq.iterrows():
            is_total = any(str(val).strip() in ["Grand Total", "GrandTotal"] for val in row.values)
            if is_total:
                seq_list.append("")
            else:
                seq_list.append(len(seq_list) + 1)
        df_with_seq.insert(0, "التسلسل", seq_list)

    html = '<div style="width: 100%;"><table class="custom-html-table"><thead><tr>'
    for col in df_with_seq.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'

    for _, row in df_with_seq.iterrows():
        sponsor_val = str(row.get("الكفيل", "")) if "الكفيل" in df_with_seq.columns else ""
        is_not_arrived = "لم تصل بعد" in sponsor_val

        is_row_total = any(str(val).strip() in ["Grand Total", "GrandTotal"] for val in row.values)

        html += '<tr>'
        for col in df_with_seq.columns:
            val = row[col]
            col_str = str(col)
            val_str = str(val).strip()
            cell_style = ""
            
            if is_row_total:
                cell_style = ' style="background-color: #4b5563 !important; color: #ffffff !important; font-weight: bold;"'
            else:
                numeric_val = None
                try:
                    clean_val_str = val_str.replace("¥", "").replace("$", "").replace(",", "")
                    numeric_val = float(clean_val_str)
                except (ValueError, TypeError):
                    pass

                if is_sponsors_pivot:
                    cell_style = ' style="background-color: #fce7f3 !important; color: #831843 !important; font-weight: bold;"'
                    if col_str in df_with_seq.columns[:2]:
                        cell_style = ' style="background-color: #fed7aa !important; color: #7c2d12 !important; font-weight: bold;"'
                else:
                    if numeric_val is not None and numeric_val > 0.0 and col_str != "التسلسل":
                        cell_style = ' style="background-color: #fbcfe8 !important; color: #831843 !important; font-weight: bold;"'
                    else:
                        if is_not_arrived:
                            cell_style = ' style="background-color: #fef08a !important; color: #713f12 !important;"'
                            if col_str in ["رقم الحاوية", "الكفيل"]:
                                cell_style = ' style="background-color: #fef08a !important; color: #713f12 !important; font-weight: bold;"'
                        else:
                            if col_str in ["رقم الحاوية", "الكفيل"]:
                                cell_style = ' style="background-color: #bbf7d0 !important; color: #065f46 !important; font-weight: bold;"'

            formatted_val = val
            if col_str == "التسلسل":
                formatted_val = val if val != "" else "-"
            elif pd.isna(val) or val_str == "" or val_str.lower() == "nan":
                formatted_val = "0.00" if is_sponsors_pivot else "-"
            elif numeric_val is not None:
                is_currency_col = any(kw in col_str for kw in ["مبلغ", "قيمة", "المجموع", "دفع", "سعر", "الاستحصالات", "متبقي", "المتبقي"])
                if is_currency_col or is_sponsors_pivot:
                    if "¥" in col_str or "يوان" in col_str or "¥" in val_str or (is_sponsors_pivot and "الزبون دفع" in col_str):
                        formatted_val = f"¥{numeric_val:,.2f}"
                    elif is_sponsors_pivot and any(k in col_str for k in ["سعر البيع", "مبلغ الجمرك", "متبقي حقيقي"]):
                        formatted_val = f"$ {numeric_val:,.2f}"
                    elif is_sponsors_pivot:
                        formatted_val = f"{numeric_val:,.2f}" if isinstance(numeric_val, float) and not numeric_val.is_integer() else f"{int(numeric_val):,}"
                    else:
                        formatted_val = f"${numeric_val:,.2f}"
                else:
                    formatted_val = f"{numeric_val:,.2f}" if isinstance(numeric_val, float) and not numeric_val.is_integer() else f"{int(numeric_val):,}" if numeric_val.is_integer() else f"{numeric_val:,.2f}"
            else:
                formatted_val = str(val)

            html += f'<td{cell_style}>{formatted_val}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    
    st.markdown(html, unsafe_allow_html=True)

if page == "dashboard":
    st.title("📊 لوحة التحكم الرئيسية")
    st.markdown("---")
    
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    search_query = st.text_input("🔍 بحث ذكي (ابحث برقم الكود، اسم الكفيل، أو رقم الحاوية):", "").strip()
    st.markdown('</div>', unsafe_allow_html=True)

    if "display_mode" not in st.session_state:
        st.session_state.display_mode = "all"

    st.markdown('<div class="no-print" style="margin-bottom: 15px;">', unsafe_allow_html=True)
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        if st.button("📄 طباعة شامل (عرض الكل)", use_container_width=True):
            st.session_state.display_mode = "all"
    with b_col2:
        if st.button("🚢 الشحن البحري (RQ)", use_container_width=True):
            st.session_state.display_mode = "marine"
    with b_col3:
        if st.button("✈️ الشحن الجوي (RA)", use_container_width=True):
            st.session_state.display_mode = "air"
    st.markdown('</div>', unsafe_allow_html=True)

    dash_filtered_df = filtered_df.copy()
    if search_query and not dash_filtered_df.empty:
        search_cols = [c for c in ["code", "الكفيل", "رقم الحاوية", "رقم الحاويات", "Shipping mark"] if c in dash_filtered_df.columns]
        if search_cols:
            mask = dash_filtered_df[search_cols].apply(lambda col: col.astype(str).str.contains(search_query, case=False, na=False))
            dash_filtered_df = dash_filtered_df[mask.any(axis=1)]

    if container_col and container_col in dash_filtered_df.columns:
        marine_df = dash_filtered_df[dash_filtered_df[container_col].astype(str).str.upper().str.startswith("RQ")]
        air_df = dash_filtered_df[dash_filtered_df[container_col].astype(str).str.upper().str.startswith("RA")]
    else:
        marine_df = pd.DataFrame(columns=dash_filtered_df.columns)
        air_df = pd.DataFrame(columns=dash_filtered_df.columns)

    if st.session_state.display_mode == "marine":
        active_view_df = marine_df
    elif st.session_state.display_mode == "air":
        active_view_df = air_df
    else:
        active_view_df = dash_filtered_df

    total_orders = len(active_view_df)
    total_weight = active_view_df["الوزن"].sum() if "الوزن" in active_view_df.columns else 0
    total_ctns = active_view_df["عدد الكارتون"].sum() if "عدد الكارتون" in active_view_df.columns else 0
    total_volume = active_view_df["حجم"].sum() if "حجم" in active_view_df.columns else 0
    
    client_field_candidates = [c for c in ["code", "الكود", "كود", "Shipping mark", "الزبون"] if c in active_view_df.columns]
    total_clients = active_view_df[client_field_candidates[0]].nunique() if client_field_candidates and not active_view_df.empty else 0
    total_containers_count = active_view_df[container_col].nunique() if container_col and container_col in active_view_df.columns and not active_view_df.empty else 0

    office_paid_col = next((c for c in ["Office Paid", "المكتب دفع"] if c in active_view_df.columns), None)
    client_paid_col = next((c for c in ["Client Paid", "الزبون دفع"] if c in active_view_df.columns), None)
    
    total_office_paid = active_view_df[office_paid_col].sum() if office_paid_col else 0
    total_client_paid = active_view_df[client_paid_col].sum() if client_paid_col else 0

    row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4)
    with row1_c1:
        st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">📦 عدد الطلبات</div><div class="metric-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
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
        st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">💰 مبالغ دفعت من المكتب</div><div class="metric-value">${total_office_paid:,.2f}</div></div>', unsafe_allow_html=True)
    with row2_c4:
        st.markdown(f'<div class="metric-card" style="background-color: #9333ea;"><div class="metric-title">👤 مبالغ دفعت من الزبون</div><div class="metric-value">${total_client_paid:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    render_download_buttons(active_view_df)
    
    active_cols = [c for c in default_columns_to_show if c in dash_filtered_df.columns]

    if st.session_state.display_mode in ["all", "marine"]:
        st.markdown("### 🚢 جدول الشحن البحري (RQ)")
        marine_display = marine_df[active_cols] if active_cols else marine_df
        display_custom_html_table(marine_display)
        if st.session_state.display_mode == "all":
            st.markdown("---")

    if st.session_state.display_mode in ["all", "air"]:
        st.markdown("### ✈️ جدول الشحن الجوي (RA)")
        air_display = air_df[active_cols] if active_cols else air_df
        display_custom_html_table(air_display)

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "customs":
    st.title("💰 كشف اجور الكمارك")
    st.markdown("---")
    
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
    search_query = st.text_input("🔍 بحث ذكي (ابحث برقم الكود، اسم الكفيل، أو رقم الحاوية):", "").strip()
    st.markdown('</div>', unsafe_allow_html=True)

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

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">أجور الجمرك الكلي</div><div class="metric-value">${total_customs:,.2f}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card" style="background-color: #0f766e;"><div class="metric-title">إجمالي المتبقي الحقيقي</div><div class="metric-value">${total_remaining:,.2f}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">إجمالي الاستحصالات (المسدد)</div><div class="metric-value">${total_collected:,.2f}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card" style="background-color: #dc2626;"><div class="metric-title">متبقي (لم تصل بعد)</div><div class="metric-value">${not_arrived_remaining:,.2f}</div></div>', unsafe_allow_html=True)

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

        render_download_buttons(customs_summary)
        display_custom_html_table(customs_summary)
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
                <div class="metric-card" style="background-color: {card_bg}; padding: 15px; border-radius: 10px; color: white; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="margin: 0 0 10px 0; font-size: 18px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 5px; color: #ffffff !important; text-align: right;">👤 الكفيل: {sponsor_name}</h3>
                    <div style="display: flex; justify-content: space-between; font-size: 15px; text-align: center; color: #ffffff !important;">
                        <div>📦 الطلبات: <b style="color: #ffffff;">{s_orders:,.2f}</b></div>
                        <div>💰 الجمرك: <b style="color: #ffffff;">${s_customs:,.2f}</b></div>
                        <div>✅ المسدد: <b style="color: #ffffff;">${s_collected:,.2f}</b></div>
                        <div>⏳ المتبقي: <b style="color: #ffffff;">${s_remaining:,.2f}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### 📊 جدول تفصيلي بملخص الكفلاء المطابق لتنسيق العرض المطلوب (Pivot Table)")
        
        pivot_container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in filtered_df.columns), None)
        pivot_mark_col = "Shipping mark" if "Shipping mark" in filtered_df.columns else None

        if pivot_container_col and pivot_mark_col:
            base_pivot_df = df.copy()
            
            if selected_container != "الكل":
                base_pivot_df = base_pivot_df[base_pivot_df[pivot_container_col].astype(str) == selected_container]
            if selected_sponsor != "الكل" and "الكفيل" in base_pivot_df.columns:
                base_pivot_df = base_pivot_df[base_pivot_df["الكفيل"].astype(str) == selected_sponsor]

            required_pivot_cols = [
                pivot_container_col, pivot_mark_col, 
                "الزبون دفع" if "الزبون دفع" in base_pivot_df.columns else "Client Paid",
                "المكتب دفع" if "المكتب دفع" in base_pivot_df.columns else "Office Paid",
                "المجموع", "عدد الكارتون", "سعر البيع", "مبلغ الجمرك", "قيمة الاستحصالات", "متبقي حقيقي"
            ]
            
            available_pivot_cols = [c for c in required_pivot_cols if c in base_pivot_df.columns]
            pivot_table_df = base_pivot_df[available_pivot_cols].copy()

            if not pivot_table_df.empty:
                numeric_cols_to_sum = [c for c in pivot_table_df.columns if c not in [pivot_container_col, pivot_mark_col]]
                
                totals_dict = {pivot_container_col: "Grand Total", pivot_mark_col: ""}
                for col in numeric_cols_to_sum:
                    pivot_table_df[col] = pd.to_numeric(pivot_table_df[col], errors="coerce").fillna(0)
                    totals_dict[col] = pivot_table_df[col].sum()

                grand_total_df = pd.DataFrame([totals_dict])
                pivot_table_df = pd.concat([pivot_table_df, grand_total_df], ignore_index=True)

                column_rename_map = {
                    pivot_container_col: "رقم الحاوية",
                    pivot_mark_col: "Shipping mark",
                    "الزبون دفع": "الزبون دفع",
                    "Client Paid": "الزبون دفع",
                    "المكتب دفع": "المكتب دفع",
                    "Office Paid": "المكتب دفع",
                    "المجموع": "المجموع",
                    "عدد الكارتون": "Sum of عدد الكارتون",
                    "سعر البيع": "Sum of سعر البيع",
                    "مبلغ الجمرك": "Sum of مبلغ الجمرك",
                    "قيمة الاستحصالات": "Sum of قيمة الاستحصالات",
                    "متبقي حقيقي": "متبقي حقيقي"
                }
                pivot_table_df = pivot_table_df.rename(columns=column_rename_map)

                render_download_buttons(pivot_table_df)
                display_custom_html_table(pivot_table_df, is_sponsors_pivot=True)
            else:
                st.warning("لا توجد بيانات كافية لإنشاء الجدول.")
        else:
            st.warning("الأعمدة المطلوبة لإنشاء الجدول المحوري غير متوفرة بالكامل.")

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "aging":
    st.title("⏳ تقرير أعمار الديون (Aging Report)")
    st.markdown("---")
    st.markdown("### 📋 جدول تحليلي يوزع المتبقي الحقيقي حسب الكود ورقم الحاوية وأيام التأخير (بدون 0 يوم)")

    aging_df = filtered_df.copy()
    code_field = next((c for c in ["code", "الكود", "كود"] if c in aging_df.columns), None)
    
    if not aging_df.empty and "رقم الحاوية" in aging_df.columns and "عدد الايام" in aging_df.columns and "متبقي حقيقي" in aging_df.columns and code_field:
        
        aging_df["عدد الايام"] = pd.to_numeric(aging_df["عدد الايام"], errors="coerce").fillna(0).astype(int)
        aging_df = aging_df[aging_df["عدد الايام"] > 0]
        
        if aging_df.empty:
            st.info("لا توجد بيانات متاحة لأيام التأخير بعد التصفية الحالية.")
        else:
            agg_aging_df = aging_df.groupby(["رقم الحاوية", code_field, "عدد الايام"])["متبقي حقيقي"].sum().reset_index()
            
            aging_pivot = agg_aging_df.pivot_table(
                index=["رقم الحاوية", code_field],
                columns="عدد الايام",
                values="متبقي حقيقي",
                aggfunc="sum",
                fill_value=0.0
            )

            aging_pivot = aging_pivot.loc[(aging_pivot > 0).any(axis=1), (aging_pivot > 0).any(axis=0)]

            if aging_pivot.empty:
                st.info("لا توجد مبالغ متبقية أكبر من الصفر للعرض بناءً على الفلاتر المحددة.")
            else:
                sorted_cols = sorted(aging_pivot.columns, reverse=False)
                aging_pivot = aging_pivot[sorted_cols]

                aging_pivot["Grand Total"] = aging_pivot.sum(axis=1)
                
                aging_grand_total = aging_pivot.sum(axis=0)
                aging_pivot = aging_pivot.reset_index()
                
                grand_total_row_dict = {
                    "رقم الحاوية": "Grand Total",
                    code_field: ""
                }
                for c in aging_pivot.columns:
                    if c not in ["رقم الحاوية", code_field]:
                        grand_total_row_dict[c] = aging_grand_total[c]
                
                aging_pivot = pd.concat([aging_pivot, pd.DataFrame([grand_total_row_dict])], ignore_index=True)
                aging_pivot.columns = [str(c) for c in aging_pivot.columns]
                
                render_download_buttons(aging_pivot)
                display_custom_html_table(aging_pivot, is_aging_report=True)
    else:
        st.warning("عذراً، الأعمدة الأساسية المطلوبة (رقم الحاوية، الكود، عدد الأيام، متبقي حقيقي) غير متوفرة بالكامل في البيانات الحالية.")

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "collections":
    st.title("🛃 نافذة كمرك الشحنات والاستحصالات")
    st.markdown("---")
    st.markdown("### 📋 ملخص الحاويات حسب مبالغ الجمرك والاستحصالات والمتبقي الحقيقي")

    if not filtered_df.empty:
        total_c = filtered_df["مبلغ الجمرك"].sum() if "مبلغ الجمرك" in filtered_df.columns else 0
        total_coll = filtered_df["قيمة الاستحصالات"].sum() if "قيمة الاستحصالات" in filtered_df.columns else 0
        total_rem = filtered_df["متبقي حقيقي"] .sum() if "متبقي حقيقي" in filtered_df.columns else 0

        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">إجمالي مبالغ الجمرك</div><div class="metric-value">${total_c:,.2f}</div></div>', unsafe_allow_html=True)
        with mc2:
            st.markdown(f'<div class="metric-card" style="background-color: #059669;"><div class="metric-title">إجمالي الاستحصالات</div><div class="metric-value">${total_coll:,.2f}</div></div>', unsafe_allow_html=True)
        with mc3:
            st.markdown(f'<div class="metric-card" style="background-color: #d97706;"><div class="metric-title">إجمالي المتبقي الحقيقي</div><div class="metric-value">${total_rem:,.2f}</div></div>', unsafe_allow_html=True)

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

        display_custom_html_table(agg_df)
    else:
        st.warning("عذراً، عمود رقم الحاوية غير متوفر في البيانات أو البيانات فارغة.")

    st.markdown("<div style='margin-block: 50px;'></div>", unsafe_allow_html=True)

elif page == "distribution":
    st.title("📦 توزيع البضاعة داخل الحاويات")
    st.markdown("---")
    st.markdown("### 📋 تفاصيل وتوزيع البضائع والكراتين داخل الحاويات")

    dist_df = filtered_df.copy()
    if not dist_df.empty:
        total_boxes = dist_df["عدد الكارتون"].sum() if "عدد الكارتون" in dist_df.columns else 0
        total_wt = dist_df["الوزن"].sum() if "الوزن" in dist_df.columns else 0
        total_vol = dist_df["حجم"].sum() if "حجم" in dist_df.columns else 0

        dc1, dc2, dc3 = st.columns(3)
        with dc1:
            st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">إجمالي عدد الكارتون</div><div class="metric-value">{total_boxes:,.2f}</div></div>', unsafe_allow_html=True)
        with dc2:
            st.markdown(f'<div class="metric-card" style="background-color: #059669;"><div class="metric-title">إجمالي الوزن (kg)</div><div class="metric-value">{total_wt:,.2f}</div></div>', unsafe_allow_html=True)
        with dc3:
            st.markdown(f'<div class="metric-card" style="background-color: #d97706;"><div class="metric-title">إجمالي الحجم (m³)</div><div class="metric-value">{total_vol:,.2f}</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        render_download_buttons(dist_df)

        dist_columns = [c for c in ["No", "code", "الكفيل", "Shipping mark", "رقم دخول المخزن", "عدد الكارتون", "الوزن", "حجم", "رقم الحاوية"] if c in dist_df.columns]
        display_df = dist_df[dist_columns] if dist_columns else dist_df
        display_custom_html_table(display_df)
    else:
        st.warning("لا توجد بيانات متاحة لعرض توزيع البضاعة.")

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

elif page == "data_entry":
    st.title("📝 إدخال وتعديل البيانات محلياً")
    st.markdown("---")
    st.markdown("يمكنك تعديل البيانات مباشرة في الجدول أدناه، أو إضافة سجل جديد:")

    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="data_editor_grid")

    if st.button("💾 حفظ التغييرات وتحديث العرض"):
        st.session_state["df_updated"] = edited_df
        st.success("تم تحديث البيانات بنجاح في الجلسة الحالية!")
        st.rer()
