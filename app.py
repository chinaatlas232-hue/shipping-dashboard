import io
import os
import pandas as pd
import streamlit as st

# 1. إعداد الصفحة والتنسيقات (عرض الشاشة بالكامل وبدون قيود)
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
    
    .block-container { 
        padding-top: 3.5rem !important; 
        padding-bottom: 3rem !important; 
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
        max-width: 100% !important; 
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

    [data-testid="stDataFrame"] {
        margin-bottom: 35px !important;
        width: 100% !important;
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
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"] *, 
    [data-testid="stSidebar"] [data-testid="stButton"] *, 
    [data-testid="stSidebar"] [data-testid="stSelectbox"] * {
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stFileUploader"], 
    [data-testid="stSidebar"] [data-testid="stButton"], 
    [data-testid="stSidebar"] [data-testid="stSelectbox"] {
        color: #ffffff !important;
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
page = st.sidebar.radio(
    "📌 القائمة الرئيسية",
    [
        "📊 لوحة التحكم (Dashboard)",
        "💰 كشف اجور الكمارك",
        "👥 الديون على الكفلاء",
        "🛃 كمرك الشحنات والاستحصالات",
        "⏳ اعمار الديون للعملاء",
        "📈 الرسوم البيانية"
    ]
)
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
        st.download_button(
            label="📥 Download as CSV",
            data=data_to_download.to_csv(index=False).encode('utf-8'),
            file_name="filtered_details.csv",
            mime="text/csv"
        )

def render_dashboard_metrics(data_df):
    total_orders = len(data_df)
    total_cartons = data_df["عدد الكارتون"].sum() if "عدد الكارتون" in data_df.columns else 0
    total_weight = data_df["الوزن"].sum() if "الوزن" in data_df.columns else 0
    total_volume = data_df["حجم"].sum() if "حجم" in data_df.columns else 0

    target_customer_col = next((c for c in [code_col, "code", "الكفيل", "الزبون"] if c in data_df.columns), None)
    total_customers = data_df[target_customer_col].nunique() if target_customer_col and not data_df.empty else 0

    office_paid_col = next((c for c in ["المكتب دفع", "Office Paid"] if c in data_df.columns), None)
    client_paid_col = next((c for c in ["الزبون دفع", "Client Paid"] if c in data_df.columns), None)

    office_paid = data_df[office_paid_col].sum() if office_paid_col and not data_df.empty else 0.0
    client_paid = data_df[client_paid_col].sum() if client_paid_col and not data_df.empty else 0.0

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    with c1:
        st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">إجمالي الطلبات</div><div class="metric-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card" style="background-color: #475569;"><div class="metric-title">عدد الزبائن</div><div class="metric-value">{total_customers:,}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card" style="background-color: #0284c7;"><div class="metric-title">إجمالي الكارتون</div><div class="metric-value">{total_cartons:,.0f}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card" style="background-color: #0d9488;"><div class="metric-title">إجمالي الوزن</div><div class="metric-value">{total_weight:,.2f} kg</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="metric-card" style="background-color: #d97706;"><div class="metric-title">إجمالي الحجم</div><div class="metric-value">{total_volume:,.3f} m³</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">دفع الشركة</div><div class="metric-value">¥{office_paid:,.2f}</div></div>', unsafe_allow_html=True)
    with c7:
        st.markdown(f'<div class="metric-card" style="background-color: #9333ea;"><div class="metric-title">دفع الزبون</div><div class="metric-value">¥{client_paid:,.2f}</div></div>', unsafe_allow_html=True)

def style_container_column(df_to_style):
    target_container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in df_to_style.columns), None)
    sponsor_col_check = "الكفيل" if "الكفيل" in df_to_style.columns else None

    if not target_container_col:
        return df_to_style.style

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
            
            if is_not_arrived:
                styles[col_idx] = 'background-color: #fef08a; color: #000000; font-weight: bold;'
            elif is_arrived:
                styles[col_idx] = 'background-color: #bbf7d0; color: #000000; font-weight: bold;'
                
        return styles

    return df_to_style.style.apply(highlight_cells, axis=1)

if page == "📊 لوحة التحكم (Dashboard)":
    st.title("📊 لوحة التحكم الرئيسية")
    st.markdown("---")
    render_dashboard_metrics(filtered_df)
    render_download_buttons(filtered_df)
    
    styled_filtered_df = style_container_column(filtered_df)
    table_height = max(300, min(len(filtered_df) * 35 + 50, 1200))
    st.dataframe(styled_filtered_df, use_container_width=True, height=table_height)
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "💰 كشف اجور الكمارك":
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
    
    sponsor_name = "الكفيل"
    sponsor_remaining = 0.0
    sponsor_collected = 0.0
    
    if "الكفيل" in pivot_filtered_df.columns and not pivot_filtered_df.empty:
        valid_sponsors = [s for s in pivot_filtered_df["الكفيل"].dropna().unique() if "لم تصل بعد" not in str(s)]
        if valid_sponsors:
            sponsor_name = str(valid_sponsors[0]).strip()
            sponsor_df = pivot_filtered_df[pivot_filtered_df["الكفيل"] == valid_sponsors[0]]
            sponsor_remaining = sponsor_df["متبقي حقيقي"].sum()
            sponsor_collected = sponsor_df["قيمة الاستحصالات"].sum()
            
    not_arrived_remaining = 0.0
    if "الكفيل" in pivot_filtered_df.columns and not pivot_filtered_df.empty:
        not_arrived_remaining = pivot_filtered_df[pivot_filtered_df["الكفيل"].astype(str).str.contains("لم تصل بعد", na=False)]["متبقي حقيقي"].sum()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">أجور الجمرك الكلي</div><div class="metric-value">${total_customs:,.2f}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card" style="background-color: #0f766e;"><div class="metric-title">متبقي ({sponsor_name})</div><div class="metric-value">${sponsor_remaining:,.2f}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">مسدد ({sponsor_name})</div><div class="metric-value">${sponsor_collected:,.2f}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card" style="background-color: #dc2626;"><div class="metric-title">متبقي (لم تصل بعد)</div><div class="metric-value">${not_arrived_remaining:,.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    tree_rows = []
    if not pivot_filtered_df.empty:
        grand_customs = pivot_filtered_df["مبلغ الجمرك"].sum() if "مبلغ الجمرك" in pivot_filtered_df else 0.0
        grand_collections = pivot_filtered_df["قيمة الاستحصالات"].sum() if "قيمة الاستحصالات" in pivot_filtered_df else 0.0
        grand_remaining = pivot_filtered_df["متبقي حقيقي"].sum() if "متبقي حقيقي" in pivot_filtered_df else 0.0
        grand_days = pivot_filtered_df["عدد الايام"].max() if "عدد الايام" in pivot_filtered_df and not pivot_filtered_df["عدد الايام"].empty else 0.0

        sponsor_col = "الكفيل" if "الكفيل" in pivot_filtered_df.columns else None
        
        group_cols = []
        if sponsor_col: group_cols.append(sponsor_col)
        if "code" in pivot_filtered_df.columns: group_cols.append("code")

        if group_cols:
            grouped_parents = pivot_filtered_df.groupby(group_cols, dropna=False)

            for group_keys, parent_group in grouped_parents:
                is_not_arrived = False
                if isinstance(group_keys, tuple):
                    s_val, c_val = group_keys[0], group_keys[1]
                    sponsor_str = str(s_val).strip() if pd.notna(s_val) else "غير محدد"
                    code_str = str(c_val).strip() if pd.notna(c_val) else ""
                    
                    label_text = f"➖ الكفيل: {sponsor_str} ({code_str})"
                    if "لم تصل بعد" in sponsor_str:
                        is_not_arrived = True
                else:
                    val_str = str(group_keys).strip()
                    label_text = f"➖ الكفيل: {val_str}"
                    if "لم تصل بعد" in val_str:
                        is_not_arrived = True

                sum_customs = parent_group["مبلغ الجمرك"].sum() if "مبلغ الجمرك" in parent_group else 0.0
                sum_collections = parent_group["قيمة الاستحصالات"].sum() if "قيمة الاستحصالات" in parent_group else 0.0
                sum_remaining = parent_group["متبقي حقيقي"].sum() if "متبقي حقيقي" in parent_group else 0.0
                group_days = parent_group["عدد الايام"].max() if "عدد الايام" in parent_group and not parent_group["عدد الايام"].empty else 0.0

                tree_rows.append({
                    "Row Labels": label_text,
                    "Sum of مبلغ الجمرك": f"${sum_customs:,.2f}",
                    "Sum of قيمة الاستحصالات": f"${sum_collections:,.2f}",
                    "Sum of متبقي حقيقي": f"${sum_remaining:,.0f}",
                    "عدد الايام": f"{group_days:,.0f}",
                    "is_not_arrived": is_not_arrived
                })

                if container_col:
                    for container, c_group in parent_group.groupby(container_col, dropna=False):
                        c_customs = c_group["مبلغ الجمرك"].sum() if "مبلغ الجمرك" in c_group else 0.0
                        c_collections = c_group["قيمة الاستحصالات"].sum() if "قيمة الاستحصالات" in c_group else 0.0
                        c_remaining = c_group["متبقي حقيقي"].sum() if "متبقي حقيقي" in c_group else 0.0
                        c_days = c_group["عدد الايام"].max() if "عدد الايام" in c_group and not c_group["عدد الايام"].empty else 0.0

                        tree_rows.append({
                            "RowLabels": f"    ↳ {container}",
                            "Sum of مبلغ الجمرك": f"${c_customs:,.2f}",
                            "Sum of قيمة الاستحصالات": f"${c_collections:,.2f}",
                            "Sum of متبقي حقيقي": f"${c_remaining:,.0f}",
                            "عدد الايام": f"{c_days:,.0f}",
                            "is_not_arrived": is_not_arrived
                        })

        tree_rows.append({
            "Row Labels": "Grand Total",
            "Sum of مبلغ الجمرك": f"${grand_customs:,.2f}",
            "Sum of قيمة الاستحصالات": f"${grand_collections:,.2f}",
            "Sum of متبقي حقيقي": f"${grand_remaining:,.0f}",
            "عدد الايام": f"{grand_days:,.0f}",
            "is_not_arrived": False
        })

    pivot_display_df = pd.DataFrame(tree_rows)

    if not pivot_display_df.empty:
        is_not_arrived_list = pivot_display_df["is_not_arrived"].tolist()
        display_df = pivot_display_df.drop(columns=["is_not_arrived"])

        def apply_row_styles(row):
            idx = row.name
            label = str(row["Row Labels"])
            is_not_arr = is_not_arrived_list[idx]

            if is_not_arr:
                return ['background-color: #fee2e2; color: #000000; font-weight: bold;'] * len(row)
            elif label.startswith("➖") or label == "Grand Total":
                return ['background-color: #f1f5f9; color: #000000; font-weight: bold;'] * len(row)
            
            return ['color: #000000; font-weight: bold; background-color: #ffffff;'] * len(row)

        styled_pivot = display_df.style.apply(apply_row_styles, axis=1)
        render_download_buttons(display_df)
        
        pivot_table_height = max(300, min(len(display_df) * 35 + 50, 1200))
        st.dataframe(styled_pivot, use_container_width=True, height=pivot_table_height)
        st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
    else:
        st.warning("لا توجد نتائج مطابقة.")

elif page == "👥 الديون على الكفلاء":
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
                        <div>📦 الطلبات: <b style="color: #ffffff;">{s_orders:,}</b></div>
                        <div>💰 الجمرك: <b style="color: #ffffff;">${s_customs:,.2f}</b></div>
                        <div>✅ المسدد: <b style="color: #ffffff;">${s_collected:,.2f}</b></div>
                        <div>⏳ المتبقي: <b style="color: #ffffff;">${s_remaining:,.2f}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### 📊 جدول تفصيلي بملخص الكفلاء (Pivot Table)")
        
        pivot_code_col = next((c for c in ["code", "الكود", "كود"] if c in filtered_df.columns), None)
        pivot_container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in filtered_df.columns), None)
        pivot_value_col = "مبلغ الجمرك" if "مبلغ الجمرك" in filtered_df.columns else None

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

            formatted_pivot = pivot_table_df.map(lambda val: f"${val:,.0f}" if isinstance(val, (int, float)) and val > 0 else ("" if isinstance(val, (int, float)) else val))
            
            def style_pivot_cells(val):
                if val == "" or val == "$0":
                    return 'background-color: #f8fafc; color: #cbd5e1;'
                return 'background-color: #fce7f3; color: #000000; font-weight: bold;'

            styled_matrix = formatted_pivot.style.map(style_pivot_cells)

            matrix_height = max(300, min(len(pivot_table_df) * 35 + 50, 1200))
            st.markdown(styled_matrix.to_html(escape=False), unsafe_allow_html=True)
        else:
            st.warning("الأعمدة المطلوبة لإنشاء جدول البايفت غير متوفرة بالكامل.")
    else:
        st.warning("لا توجد بيانات متاحة لعرض التقارير حالياً.")
    
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "🛃 كمرك الشحنات والاستحصالات":
    st.title("🛃 نافذة كمرك الشحنات والاستحصالات")
    st.markdown("---")
    st.markdown("### 📋 ملخص الحاويات حسب مبالغ الجمرك والاستحصالات والمتبقي الحقيقي")

    if not filtered_df.empty:
        total_c = filtered_df["مبلغ الجمرك"].sum() if "مبلغ الجمرك" in filtered_df.columns else 0
        total_coll = filtered_df["قيمة الاستحصالات"].sum() if "قيمة الاستحصالات" in filtered_df.columns else 0
        total_rem = filtered_df["متبقي حقيقي"].sum() if "متبقي حقيقي" in filtered_df.columns else 0

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

        formatted_agg = agg_df.copy()
        for col in ["Sum of مبلغ الجمرك", "Sum of قيمة الاستحصالات", "Sum of متبقي حقيقي"]:
            formatted_agg[col] = formatted_agg[col].apply(lambda x: f"${x:,.0f}")

        def style_summary_rows(row):
            if row["رقم الحاوية"] == "Grand Total":
                return ['background-color: #f1f5f9; color: #000000; font-weight: bold;'] * len(row)
            return ['background-color: #ffffff; color: #000000; font-weight: bold;'] * len(row)

        styled_summary = formatted_agg.style.apply(style_summary_rows, axis=1)

        summary_height = max(300, min(len(formatted_agg) * 35 + 50, 1200))
        st.dataframe(styled_summary, use_container_width=True, height=summary_height)
    else:
        st.warning("عذراً، عمود رقم الحاوية غير متوفر في البيانات أو البيانات فارغة.")

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "⏳ اعمار الديون للعملاء":
    st.title("⏳ اعمار الديون للعملاء (Aging Report)")
    st.markdown("---")
    st.markdown("### 📋 جدول اعمار الديون (توزيع المتبقي حسب الحاويات والأكواد)")

    aging_code_col = next((c for c in ["code", "الكود", "كود"] if c in filtered_df.columns), None)
    aging_container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in filtered_df.columns), None)
    aging_days_col = "عدد الايام" if "عدد الايام" in filtered_df.columns else None

    if aging_code_col and aging_container_col and "متبقي حقيقي" in filtered_df.columns:
        base_aging_df = filtered_df.copy()

        pivot_col_target = aging_days_col if aging_days_col else aging_container_col
        
        tree_aging_rows = []
        all_col_values = sorted(base_aging_df[pivot_col_target].dropna().unique().tolist())
        
        grouped_containers = base_aging_df.groupby(aging_container_col, dropna=False)

        grand_totals_dict = {col: 0.0 for col in all_col_values}
        grand_total_sum = 0.0

        for container_val, container_group in grouped_containers:
            container_str = str(container_val).strip() if pd.notna(container_val) else "غير محدد"
            
            container_col_sums = {}
            container_total = 0.0
            for col in all_col_values:
                sub_val = container_group[container_group[pivot_col_target] == col]["متبقي حقيقي"].sum()
                container_col_sums[col] = sub_val
                container_total += sub_val
                grand_totals_dict[col] += sub_val
                grand_total_sum += sub_val

            parent_row = {
                "Row Labels": f"➕ الحاوية: {container_str}",
                "is_parent": True
            }
            for col in all_col_values:
                parent_row[str(col)] = container_col_sums[col]
            parent_row["Grand Total"] = container_total
            tree_aging_rows.append(parent_row)

            for code_val, code_group in container_group.groupby(aging_code_col, dropna=False):
                code_str = str(code_val).strip() if pd.notna(code_val) else ""
                code_col_sums = {}
                code_total = 0.0
                for col in all_col_values:
                    c_val = code_group[code_group[pivot_col_target] == col]["متبقي حقيقي"].sum()
                    code_col_sums[col] = c_val
                    code_total += c_val

                child_row = {
                    "Row Labels": f"    ↳ {code_str}",
                    "is_parent": False
                }
                for col in all_col_values:
                    child_row[str(col)] = code_col_sums[col]
                child_row["Grand Total"] = code_total
                tree_aging_rows.append(child_row)

        grand_row = {
            "Row Labels": "Grand Total",
            "is_parent": False
        }
        for col in all_col_values:
            grand_row[str(col)] = grand_totals_dict[col]
        grand_row["Grand Total"] = grand_total_sum
        tree_aging_rows.append(grand_row)

        aging_display_df = pd.DataFrame(tree_aging_rows)
        
        cols_order = ["Row Labels"] + [str(c) for c in all_col_values] + ["Grand Total"]
        aging_display_df = aging_display_df[[c for c in cols_order if c in aging_display_df.columns]]

        # تصحيح قراءة عمود is_parent بأمان لتفادي خطأ KeyError نهائياً
        if "is_parent" in aging_display_df.columns:
            is_parent_list = aging_display_df["is_parent"].tolist()
            matrix_df = aging_display_df.drop(columns=["is_parent"])
        else:
            is_parent_list = [False] * len(aging_display_df)
            matrix_df = aging_display_df.copy()

        formatted_matrix = matrix_df.copy()
        for col in formatted_matrix.columns:
            if col != "Row Labels":
                formatted_matrix[col] = formatted_matrix[col].apply(
                    lambda val: f"${val:,.0f}" if isinstance(val, (int, float)) and val > 0 else ""
                )

        def style_aging_tree(row):
            idx = row.name
            label = str(row["Row Labels"])
            
            if label == "Grand Total":
                return ['background-color: #f1f5f9; color: #000000; font-weight: bold;'] * len(row)
            elif idx < len(is_parent_list) and is_parent_list[idx]:
                return ['background-color: #e2e8f0; color: #0f172a; font-weight: bold;'] * len(row)
            else:
                return ['background-color: #ffffff; color: #1e293b;'] * len(row)

        styled_aging_matrix = formatted_matrix.style.apply(style_aging_tree, axis=1)

        render_download_buttons(matrix_df)

        aging_height = max(300, min(len(formatted_matrix) * 35 + 50, 1200))
        st.markdown(styled_aging_matrix.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.warning("الأعمدة المطلوبة (الكود، رقم الحاوية، أو المتبقي الحقيقي) غير متوفرة بالكامل في البيانات الحالية.")

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

elif page == "📈 الرسوم البيانية":
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
