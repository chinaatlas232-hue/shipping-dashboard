import io
import os
import pandas as pd
import streamlit as st

# 1. إعداد الصفحة والتنسيقات
st.set_page_config(
    page_title="Logistics Admin Dashboard", page_icon="📦", layout="wide"
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
    .block-container { padding-top: 1.5rem !important; padding-bottom: 4rem; max-width: 99% !important; }

    [data-testid="stTextInput"] label {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #1f2937 !important;
    }

    [data-testid="stDataFrame"] {
        margin-bottom: 35px !important;
    }
    
    /* تخصيص شريط التمرير ليصبح على شكل مربع صغير ومرتب بلون أحمر فاتح */
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
        background: #f87171 !important; /* لون أحمر فاتح */
        border-radius: 4px !important; /* شكل يشبه المربع الصغير */
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #ef4444 !important; /* أحمر داكن قليلاً عند التمرير عليها */
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

# 2. تحميل البيانات
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
            "الوزن", "حجم", "رقم الحاوية", "مبلغ الجمرك", "قيمة الاستحصالات"
        ])

    df.columns = df.columns.astype(str).str.strip()

    if "الزبون دفع" in df.columns and "Client Paid" not in df.columns:
        df["Client Paid"] = df["الزبون دفع"]

    if "المكتب دفع" in df.columns and "Office Paid" not in df.columns:
        df["Office Paid"] = df["المكتب دفع"]

    numeric_cols = [
        "المكتب دفع", "Office Paid", "الزبون دفع", "Client Paid",
        "عدد الكارتون", "الوزن", "حجم", "المجموع", "مبلغ الجمرك", "قيمة الاستحصالات"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = clean_numeric(df[col])

    if "مبلغ الجمرك" in df.columns and "قيمة الاستحصالات" in df.columns:
        df["متبقي حقيقي"] = df["مبلغ الجمرك"] - df["قيمة الاستحصالات"]

    return df

# 3. القائمة الجانبية (Sidebar)
st.sidebar.title("🚢 إدارة اللوجستيات")
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

# إضافة الفلتر الجانبي لاسم الكفيل
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
        "📈 واجهة التقارير"
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

# دالة لتلوين عمود رقم الحاوية بناءً على حالة الكفيل
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
                styles[col_idx] = 'background-color: #fef08a; color: #713f12; font-weight: bold;'
            elif is_arrived:
                styles[col_idx] = 'background-color: #bbf7d0; color: #14532d; font-weight: bold;'
                
        return styles

    return df_to_style.style.apply(highlight_cells, axis=1)

# 4. التنقل بين الصفحات
if page == "📊 لوحة التحكم (Dashboard)":
    st.title("📊 لوحة التحكم الرئيسية")
    st.markdown("---")
    render_dashboard_metrics(filtered_df)
    render_download_buttons(filtered_df)
    
    styled_filtered_df = style_container_column(filtered_df)
    st.dataframe(styled_filtered_df, use_container_width=True, height=700)
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

                tree_rows.append({
                    "Row Labels": label_text,
                    "Sum of مبلغ الجمرك": f"${sum_customs:,.2f}",
                    "Sum of قيمة الاستحصالات": f"${sum_collections:,.2f}",
                    "Sum of متبقي حقيقي": f"${sum_remaining:,.0f}",
                    "is_not_arrived": is_not_arrived
                })

                if container_col:
                    for container, c_group in parent_group.groupby(container_col, dropna=False):
                        c_customs = c_group["مبلغ الجمرك"].sum() if "مبلغ الجمرك" in c_group else 0.0
                        c_collections = c_group["قيمة الاستحصالات"].sum() if "قيمة الاستحصالات" in c_group else 0.0
                        c_remaining = c_group["متبقي حقيقي"].sum() if "متبقي حقيقي" in c_group else 0.0

                        tree_rows.append({
                            "RowLabels": f"    ↳ {container}",
                            "Sum of مبلغ الجمرك": f"${c_customs:,.2f}",
                            "Sum of قيمة الاستحصالات": f"${c_collections:,.2f}",
                            "Sum of متبقي حقيقي": f"${c_remaining:,.0f}",
                            "is_not_arrived": is_not_arrived
                        })

        tree_rows.append({
            "Row Labels": "Grand Total",
            "Sum of مبلغ الجمرك": f"${grand_customs:,.2f}",
            "Sum of قيمة الاستحصالات": f"${grand_collections:,.2f}",
            "Sum of متبقي حقيقي": f"${grand_remaining:,.0f}",
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
                return ['background-color: #fee2e2; color: #991b1b; font-weight: bold;'] * len(row)
            elif label.startswith("➖") or label == "Grand Total":
                return ['background-color: #f1f5f9; color: #0f172a; font-weight: bold;'] * len(row)
            
            return ['color: #1e293b; background-color: #ffffff;'] * len(row)

        styled_pivot = display_df.style.apply(apply_row_styles, axis=1)
        render_download_buttons(display_df)
        st.dataframe(styled_pivot, use_container_width=True, height=750)
        st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
    else:
        st.warning("لا توجد نتائج مطابقة.")

elif page == "📈 واجهة التقارير":
    st.title("📈 واجهة التقارير الشاملة حسب الكفيل")
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
                    <h3 style="margin: 0 0 10px 0; font-size: 18px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 5px;">👤 الكفيل: {sponsor_name}</h3>
                    <div style="display: flex; justify-content: space-between; font-size: 15px; text-align: center;">
                        <div>📦 الطلبات: <b>{s_orders:,}</b></div>
                        <div>💰 الجمرك: <b>${s_customs:,.2f}</b></div>
                        <div>✅ المسدد: <b>${s_collected:,.2f}</b></div>
                        <div>⏳ المتبقي: <b>${s_remaining:,.2f}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown("### 📊 جدول تفصيلي بملخص الكفلاء (Pivot Table)")
        
        pivot_code_col = next((c for c in ["code", "الكود", "كود"] if c in filtered_df.columns), None)
        pivot_container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in filtered_df.columns), None)
        pivot_value_col = "مبلغ الجمرك" if "مبلغ الجمرك" in filtered_df.columns else None

        if pivot_code_col and pivot_container_col and pivot_value_col:
            pivot_table_df = filtered_df.pivot_table(
                index=pivot_code_col,
                columns=pivot_container_col,
                values=pivot_value_col,
                aggfunc="sum",
                fill_value=0
            )

            pivot_table_df["Grand Total"] = pivot_table_df.sum(axis=1)
            grand_total_row = pivot_table_df.sum(axis=0)
            pivot_table_df.loc["Grand Total"] = grand_total_row

            # تم تعديل applymap إلى map هنا لحل المشكلة نهائياً
            formatted_pivot = pivot_table_df.map(lambda val: f"${val:,.0f}" if val > 0 else "")
            
            def style_pivot_cells(val):
                if val == "" or val == "$0":
                    return 'background-color: #1e3a8a; color: #1e3a8a;'
                return 'background-color: #ffffff; color: #000000; font-weight: bold;'

            styled_matrix = formatted_pivot.style.map(style_pivot_cells)
            st.dataframe(styled_matrix, use_container_width=True)
        else:
            st.warning("الأعمدة المطلوبة لإنشاء جدول البايفت (الكود، رقم الحاوية، مبلغ الجمرك) غير متوفرة بالكامل.")
            st.dataframe(sponsor_summary, use_container_width=True)
    else:
        st.warning("لا توجد بيانات متاحة لعرض التقارير حالياً.")
    
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
