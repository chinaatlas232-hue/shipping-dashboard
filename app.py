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
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem; max-width: 99% !important; }

    [data-testid="stTextInput"] label {
        font-size: 18px !important;
        font-weight: bold !important;
        color: #1f2937 !important;
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
        df = pd.DataFrame({
            "No": [1324, 1352],
            "code": ["BS79", "BS79"],
            "الكفيل": ["مرتضى", "لم تصل بعد"],
            "Shipping mark": ["BS79-C23", "BS79-C03"],
            "رقم دخول المخزن": ["RS2607223184", "RS2607202745"],
            "المكتب دفع": [0, 0],
            "الزبون دفع": [100, 690],
            "المجموع": [3465, 5600],
            "عدد الكارتون": [1, 2],
            "الوزن": [40, 98],
            "حجم": [0.132, 0.525],
            "رقم الحاوية": ["RQ6029", "RQ6034"],
            "مبلغ الجمرك": [3768.30, 94.80],
            "قيمة الاستحصالات": [0.0, 0.0]
        })

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

# زر مسح بيانات شيت الطلبات فقط (حذف ملف البيانات المحفوظ وإعادة تحميل الصفحة)
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

# فلتر رقم الحاوية
container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in df.columns), None)
selected_container = "الكل"
if container_col:
    containers = ["الكل"] + sorted(df[container_col].dropna().astype(str).unique().tolist())
    selected_container = st.sidebar.selectbox("🚢 اختر رقم الحاوية:", containers)
    if selected_container != "الكل":
        filtered_df = filtered_df[filtered_df[container_col].astype(str) == selected_container]

# فلتر الكود (المدمج الجديد بدقة)
code_col = next((c for c in ["code", "الكود", "كود"] if c in df.columns), "code")
selected_code = "الكل"
if code_col in df.columns:
    codes = ["الكل"] + sorted(df[code_col].dropna().astype(str).unique().tolist())
    selected_code = st.sidebar.selectbox("🏷️ اختر الكود (Code):", codes)
    if selected_code != "الكل":
        filtered_df = filtered_df[filtered_df[code_col].astype(str) == selected_code]

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "📌 القائمة الرئيسية",
    [
        "📊 لوحة التحكم (Dashboard)",
        "🚢 الشحنات والحاويات",
        "📦 الطلبات",
        "💰 كشف الكمارك المستحصلة",
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
    total_customers = data_df[target_customer_col].nunique() if target_customer_col else 0

    office_paid_col = next((c for c in ["المكتب دفع", "Office Paid"] if c in data_df.columns), None)
    client_paid_col = next((c for c in ["الزبون دفع", "Client Paid"] if c in data_df.columns), None)

    office_paid = data_df[office_paid_col].sum() if office_paid_col else 0.0
    client_paid = data_df[client_paid_col].sum() if client_paid_col else 0.0

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

# 4. التنقل بين الصفحات
if page == "📊 لوحة التحكم (Dashboard)":
    st.title("📊 لوحة التحكم الرئيسية")
    st.markdown("---")
    render_dashboard_metrics(filtered_df)
    render_download_buttons(filtered_df)
    st.dataframe(filtered_df, use_container_width=True, height=700)

elif page == "🚢 الشحنات والحاويات":
    st.title("🚢 إدارة الشحنات والحاويات")
    st.markdown("---")
    render_dashboard_metrics(filtered_df)
    render_download_buttons(filtered_df)
    st.dataframe(filtered_df, use_container_width=True, height=700)

elif page == "📦 الطلبات":
    st.title("📦 جميع الطلبات المسجلة")
    st.markdown("---")
    render_dashboard_metrics(filtered_df)
    render_download_buttons(filtered_df)
    st.dataframe(filtered_df, use_container_width=True, height=700)

elif page == "💰 كشف الكمارك المستحصلة":
    st.title("💰 كشف الكمارك المستحصلة من العميل (Pivot Report)")
    st.markdown("---")
    
    search_query = st.text_input("🔍 بحث ذكي (ابحث برقم الكود، اسم الكفيل، أو رقم الحاوية):", "").strip()
    
    pivot_filtered_df = filtered_df.copy()
    
    if search_query:
        search_cols = [c for c in ["code", "الكفيل", "رقم الحاوية", "رقم الحاويات"] if c in pivot_filtered_df.columns]
        if search_cols:
            mask = pivot_filtered_df[search_cols].apply(lambda col: col.astype(str).str.contains(search_query, case=False, na=False))
            pivot_filtered_df = pivot_filtered_df[mask.any(axis=1)]

    total_customs = pivot_filtered_df["مبلغ الجمرك"].sum() if "مبلغ الجمرك" in pivot_filtered_df else 0.0
    
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
                            "Row Labels": f"    ↳ {container}",
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
    else:
        st.warning("لا توجد نتائج مطابقة.")

elif page == "📈 واجهة التقارير":
    st.title("📈 واجهة التقارير الشاملة")
    st.markdown("---")
    render_dashboard_metrics(filtered_df)
    render_download_buttons(filtered_df)
    st.dataframe(filtered_df, use_container_width=True, height=500)
