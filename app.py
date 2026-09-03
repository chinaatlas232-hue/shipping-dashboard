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
        padding: 10px 8px !important;
        border: 1px solid #cbd5e1 !important;
        font-size: 14px !important;
    }
    .custom-html-table td {
        text-align: center !important;
        padding: 8px !important;
        border: 1px solid #cbd5e1 !important;
        font-size: 13px !important;
        color: #1e293b !important;
    }
    .custom-html-table tr:nth-child(even) {
        background-color: #f8fafc !important;
    }

    .metric-card {
        padding: 16px; border-radius: 12px; color: white;
        text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .metric-title { font-size: 14px; margin-bottom: 6px; opacity: 0.95; font-weight: 600; }
    .metric-value { font-size: 20px; font-weight: bold; }
    
    .block-container { 
        padding-top: 2rem !important; 
        padding-bottom: 3rem !important; 
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
    [data-testid="stSidebar"] .stMarkdown p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        text-align: right !important;
    }

    ::-webkit-scrollbar {
        width: 10px !important;
        height: 10px !important;
    }
    ::-webkit-scrollbar-track {
        background: #f1f5f9 !important;
        border-radius: 5px !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #f87171 !important;
        border-radius: 4px !important;
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
        pass

    if df is None or df.empty:
        df = pd.DataFrame(columns=[
            "No", "code", "الكفيل", "Shipping mark", "رقم دخول المخزن",
            "المكتب دفع", "الزبون دفع", "المجموع", "عدد الكارتون",
            "الوزن", "حجم", "رقم الحاوية", "مبلغ الجمرك", "قيمة الاستحصالات", "عدد الايام", "نوع البضاعة"
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
        "عدد الكارتون", "الوزن", "حجم", "المجموع", "مبلغ الجمرك", "قيمة الاستحصالات", "عدد الايام"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = clean_numeric(df[col])

    if "مبلغ الجمرك" in df.columns and "قيمة الاستحصالات" in df.columns:
        df["متبقي حقيقي"] = df["مبلغ الجمرك"] - df["قيمة الاستحصالات"]

    return df

df = load_data()
all_columns = df.columns.tolist()

# ضبط الـ Session State للاختيارات لكي تثبت تماماً ولا تتصفر أبداً
if "user_selected_columns" not in st.session_state:
    st.session_state["user_selected_columns"] = all_columns

# ----------------- القائمة الجانبية (Sidebar) -----------------
st.sidebar.title("🚢 شركة أطلس المحيط")
st.sidebar.markdown("---")

if st.sidebar.button("🔄 تحديث البيانات من جوجل شيت", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 👁️ التحكم بأعمدة العرض الثابتة")

# عنصر اختيار الأعمدة المرتبط حصرياً بذاكرة الجلسة الثابتة
selected_columns = st.sidebar.multiselect(
    "اختر الأعمدة المراد إظهارها:",
    options=all_columns,
    default=st.session_state["user_selected_columns"],
    key="fixed_multiselect_columns_key"
)

# حفظ التحديثات المباشرة دون ضياع
st.session_state["user_selected_columns"] = selected_columns

st.sidebar.markdown("---")

page_options = {
    "لوحة التحكم (Dashboard)": "dashboard",
    "كشف اجور الكمارك": "customs",
    "الديون على الكفلاء": "sponsors",
    "اعمار الديون (Aging Report)": "aging",
    "كمرك الشحنات والاستحصالات": "collections",
    "الرسوم البيانية": "charts"
}

selected_page_label = st.sidebar.radio("📌 القائمة الرئيسية", list(page_options.keys()), key="selected_page_label_key")
page = page_options[selected_page_label]

st.sidebar.markdown("---")
st.sidebar.info("متصل بملف Google Sheets بنجاح ✔️")


# ----------------- نظام التصفية والبحث المخصص الحر -----------------
st.markdown("### 🔍 نظام التصفية والبحث المخصص للجدول")

with st.expander("📂 اضغط هنا لفتح خيارات التصفية المتقدمة حسب رغبتك", expanded=True):
    fc1, fc2, fc3 = st.columns(3)
    
    with fc1:
        search_text = st.text_input("بحث نصي عام (في كل الأعمدة):", "", key="general_search_input").strip()
        
    container_col_name = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in df.columns), None)
    with fc2:
        if container_col_name:
            all_containers = sorted(df[container_col_name].dropna().astype(str).unique().tolist())
            selected_containers_filter = st.multiselect("تصفية برقم الحاوية:", options=all_containers, default=[], key="filter_containers")
        else:
            selected_containers_filter = []

    code_col_name = next((c for c in ["code", "الكود", "كود"] if c in df.columns), None)
    with fc3:
        if code_col_name:
            all_codes = sorted(df[code_col_name].dropna().astype(str).unique().tolist())
            selected_codes_filter = st.multiselect("تصفية بالكود (Code):", options=all_codes, default=[], key="filter_codes")
        else:
            selected_codes_filter = []

    fc4, fc5, fc6 = st.columns(3)
    sponsor_col_name = next((c for c in ["الكفيل", "كفيل"] if c in df.columns), None)
    with fc4:
        if sponsor_col_name:
            all_sponsors = sorted(df[sponsor_col_name].dropna().astype(str).unique().tolist())
            selected_sponsors_filter = st.multiselect("تصفية باسم الكفيل:", options=all_sponsors, default=[], key="filter_sponsors")
        else:
            selected_sponsors_filter = []

    goods_col_name = next((c for c in ["نوع البضاعة", "البضاعة"] if c in df.columns), None)
    with fc5:
        if goods_col_name:
            all_goods = sorted(df[goods_col_name].dropna().astype(str).unique().tolist())
            selected_goods_filter = st.multiselect("تصفية بنوع البضاعة:", options=all_goods, default=[], key="filter_goods")
        else:
            selected_goods_filter = []

    with fc6:
        st.markdown("<div style='margin-top: 27px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ مسح وإلغاء كل الفلاتر", use_container_width=True):
            st.rerun()

st.markdown("---")

# تطبيق الفلاتر على البيانات
filtered_df = df.copy()

if search_text:
    mask = filtered_df.astype(str).apply(lambda col: col.str.contains(search_text, case=False, na=False)).any(axis=1)
    filtered_df = filtered_df[mask]

if container_col_name and selected_containers_filter:
    filtered_df = filtered_df[filtered_df[container_col_name].astype(str).isin(selected_containers_filter)]

if code_col_name and selected_codes_filter:
    filtered_df = filtered_df[filtered_df[code_col_name].astype(str).isin(selected_codes_filter)]

if sponsor_col_name and selected_sponsors_filter:
    filtered_df = filtered_df[filtered_df[sponsor_col_name].astype(str).isin(selected_sponsors_filter)]

if goods_col_name and selected_goods_filter:
    filtered_df = filtered_df[filtered_df[goods_col_name].astype(str).isin(selected_goods_filter)]


# دوال التصدير والعرض
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
        print_html = """
            <div class="no-print" style="width: 100%;">
                <button onclick="window.parent.print();" style="
                    background-color: #ff4b4b; color: white; padding: 0.45rem 0.75rem;
                    border: none; border-radius: 0.3rem; font-weight: 500; cursor: pointer;
                    width: 100%; height: 38px; font-size: 14px; font-family: inherit;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                ">
                    📄 طباعة / حفظ كـ PDF
                </button>
            </div>
        """
        components.html(print_html, height=45)
    st.markdown('</div>', unsafe_allow_html=True)

def display_custom_html_table(df_to_render, is_sponsors_pivot=False, is_aging_report=False):
    if df_to_render.empty:
        st.info("لا توجد بيانات مطابقة لخيارات الفلترة الحالية.")
        return
        
    currency_keywords = ["مبلغ", "قيمة", "المجموع", "دفع", "سعر", "الاستحصالات", "المتبقي"]

    html = '<div style="width: 100%;"><table class="custom-html-table"><thead><tr>'
    for col in df_to_render.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'

    for _, row in df_to_render.iterrows():
        html += '<tr>'
        for col in df_to_render.columns:
            val = row[col]
            col_str = str(col)
            cell_style = ""
            
            is_grand_total_row = (str(row.get("رقم الحاوية", "")) == "Grand Total") or (str(row.get("code", "")) == "Grand Total") or (col_str == "Grand Total")
            
            if (is_sponsors_pivot or is_aging_report) and not is_grand_total_row and col_str != "رقم الحاوية" and col_str != "code":
                try:
                    num_val = float(str(val).replace("¥", "").replace(",", "").strip())
                    if num_val > 0.0:
                        cell_style = ' style="background-color: #fbcfe8; color: #000000; font-weight: bold;"'
                except:
                    pass

            if not is_sponsors_pivot and not is_aging_report and "متبقي حقيقي" in col_str:
                try:
                    num_val = float(str(val).replace("¥", "").replace(",", "").strip())
                    if num_val == 0.0:
                        cell_style = ' style="background-color: #bbf7d0; color: #000000; font-weight: bold;"'
                    elif num_val > 0.0:
                        cell_style = ' style="background-color: #fbcfe8; color: #000000; font-weight: bold;"'
                except:
                    pass

            formatted_val = val
            if pd.isna(val) or str(val).strip() == "" or str(val).lower() == "nan":
                formatted_val = "0.00"
            elif pd.api.types.is_numeric_dtype(type(val)) or isinstance(val, (int, float)):
                if any(kw in col_str for kw in currency_keywords):
                    formatted_val = f"¥{val:,.2f}"
                else:
                    formatted_val = f"{val:,.2f}" if isinstance(val, float) else f"{val:,}"
            else:
                try:
                    num_try = float(str(val).replace(",", "").strip())
                    formatted_val = f"{num_try:,.2f}"
                except:
                    pass

            html += f'<td{cell_style}>{formatted_val}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    
    st.markdown(html, unsafe_allow_html=True)

# عرض الأقسام والصفحات
if page == "dashboard":
    st.title("📊 لوحة التحكم الرئيسية")
    st.markdown("---")

    total_orders = len(filtered_df)
    total_weight = filtered_df["الوزن"].sum() if "الوزن" in filtered_df.columns else 0
    total_ctns = filtered_df["عدد الكارتون"].sum() if "عدد الكارتون" in filtered_df.columns else 0
    total_volume = filtered_df["حجم"].sum() if "حجم" in filtered_df.columns else 0
    
    client_field_candidates = [c for c in ["code", "الكود", "كود", "Shipping mark", "الزبون"] if c in filtered_df.columns]
    total_clients = filtered_df[client_field_candidates[0]].nunique() if client_field_candidates and not filtered_df.empty else 0
    total_containers_count = filtered_df[container_col_name].nunique() if container_col_name and container_col_name in filtered_df.columns and not filtered_df.empty else 0

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
    
    # الاعتماد على القائمة المختارة عبر الـ multiselect الثابت
    df_to_display = filtered_df[selected_columns] if selected_columns else filtered_df
    display_custom_html_table(df_to_display)

elif page == "customs":
    st.title("💰 كشف اجور الكمارك")
    st.markdown("---")
    
    total_customs = filtered_df["مبلغ الجمرك"].sum() if "مبلغ الجمرك" in filtered_df and not filtered_df.empty else 0.0
    total_collected = filtered_df["قيمة الاستحصالات"].sum() if "قيمة الاستحصالات" in filtered_df and not filtered_df.empty else 0.0
    total_remaining = filtered_df["متبقي حقيقي"].sum() if "متبقي حقيقي" in filtered_df and not filtered_df.empty else 0.0

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">أجور الجمرك الكلي</div><div class="metric-value">¥{total_customs:,.2f}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card" style="background-color: #0f766e;"><div class="metric-title">إجمالي المتبقي الحقيقي</div><div class="metric-value">¥{total_remaining:,.2f}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">إجمالي الاستحصالات (المسدد)</div><div class="metric-value">¥{total_collected:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    pivot_code_col = next((c for c in ["code", "الكود", "كود"] if c in filtered_df.columns), None)
    if pivot_code_col and not filtered_df.empty:
        customs_summary = filtered_df.groupby(pivot_code_col, dropna=False).agg({
            "عدد الكارتون": "sum", "مبلغ الجمرك": "sum", "قيمة الاستحصالات": "sum", "متبقي حقيقي": "sum"
        }).reset_index()

        grand_total_row = pd.DataFrame({
            pivot_code_col: ["Grand Total"],
            "عدد الكارتون": [customs_summary["عدد الكارتون"].sum()],
            "مبلغ الجمرك": [customs_summary["مبلغ الجمرك"].sum()],
            "قيمة الاستحصالات": [customs_summary["قيمة الاستحصالات"].sum()],
            "متبقي حقيقي": [customs_summary["متبقي حقيقي"].sum()]
        })
        customs_summary = pd.concat([customs_summary, grand_total_row], ignore_index=True)
        render_download_buttons(customs_summary)
        display_custom_html_table(customs_summary)

elif page == "sponsors":
    st.title("👥 الديون على الكفلاء")
    st.markdown("---")
    if "الكفيل" in filtered_df.columns and not filtered_df.empty:
        sponsor_summary = filtered_df.groupby("الكفيل").agg(
            total_customs=("مبلغ الجمرك", "sum"),
            total_collected=("قيمة الاستحصالات", "sum"),
            total_remaining=("متبقي حقيقي", "sum"),
            total_orders=("No", "count")
        ).reset_index()

        for _, row in sponsor_summary.iterrows():
            st.markdown(f"""
                <div style="background-color: #1e3a8a; padding: 12.2px; border-radius: 8px; color: white; margin-bottom: 10px;">
                    <h4 style="margin:0 0 5px 0; color:white;">👤 الكفيل: {row["الكفيل"]}</h4>
                    <div style="display: flex; justify-content: space-between;">
                        <span>الطلبات: <b>{row["total_orders"]}</b></span>
                        <span>الجمرك: <b>¥{row["total_customs"]:,.2f}</b></span>
                        <span>المسدد: <b>¥{row["total_collected"]:,.2f}</b></span>
                        <span>المتبقي: <b>¥{row["total_remaining"]:,.2f}</b></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

elif page == "aging":
    st.title("⏳ تقرير أعمار الديون (Aging Report)")
    st.markdown("---")
    if not filtered_df.empty:
        display_custom_html_table(filtered_df[selected_columns] if selected_columns else filtered_df)

elif page == "collections":
    st.title("🛃 كمرك الشحنات والاستحصالات")
    st.markdown("---")
    render_download_buttons(filtered_df)
    display_custom_html_table(filtered_df[selected_columns] if selected_columns else filtered_df)

elif page == "charts":
    st.title("📈 لوحة الرسوم البيانية")
    st.markdown("---")
    if not filtered_df.empty and container_col_name and "مبلغ الجمرك" in filtered_df.columns:
        st.bar_chart(filtered_df.groupby(container_col_name)[["مبلغ الجمرك", "قيمة الاستحصالات"]].sum())
