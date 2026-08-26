import io
import os
import pandas as pd
import streamlit as st

# 1. إعداد الصفحة والتنسيقات
st.set_page_config(
    page_title="شركة أطلس المحيط",
    page_icon="📦",
    layout="wide"
)

st.markdown("""
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
</style>
""", unsafe_allow_html=True)

DATA_FILE = "shipping_data.xlsx"
WMS_FILE = "wms_daily_data.xlsx"

def clean_numeric(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace("¥", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip(),
        errors="coerce"
    ).fillna(0)

# تحميل بيانات الشحن الأساسية
def load_shipping_data(uploaded_file):
    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            df.to_excel(DATA_FILE, index=False)
            st.sidebar.success("تم حفظ ملف الشحن بنجاح ✔️")
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
    
    # توحيد أسماء أعمدة الدفع لضمان قراءتها دائماً
    if "Office Paid" in df.columns and "المكتب دفع" not in df.columns:
        df["المكتب دفع"] = df["Office Paid"]
    if "Client Paid" in df.columns and "الزبون دفع" not in df.columns:
        df["الزبون دفع"] = df["Client Paid"]
        
    numeric_cols = ["المكتب دفع", "الزبون دفع", "عدد الكارتون", "الوزن", "حجم", "المجموع", "مبلغ الجمرك", "قيمة الاستحصالات", "عدد الايام"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = clean_numeric(df[col])
            
    if "مبلغ الجمرك" in df.columns and "قيمة الاستحصالات" in df.columns:
        df["متبقي حقيقي"] = df["مبلغ الجمرك"] - df["قيمة الاستحصالات"]
        
    return df

# تحميل بيانات حركة المخازن (WMS) بشكل مستقل تماماً
def load_wms_data(uploaded_wms):
    df_wms = None
    if uploaded_wms is not None:
        try:
            df_wms = pd.read_excel(uploaded_wms)
            df_wms.to_excel(WMS_FILE, index=False)
            st.success("تم حفظ ملف حركة المخازن بنجاح ✔️")
        except Exception as e:
            st.error(f"خطأ في قراءة ملف WMS: {e}")
            
    if df_wms is None and os.path.exists(WMS_FILE):
        try:
            df_wms = pd.read_excel(WMS_FILE)
        except Exception:
            df_wms = None
            
    return df_wms

# القائمة الجانبية
st.sidebar.title("🚢 شركة أطلس المحيط")
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📁 رفع ملف الشحن الأساسي (Excel)", type=["xlsx", "xls"])

if st.sidebar.button("🗑️ مسح بيانات ملف الشحن الحالي"):
    if os.path.exists(DATA_FILE):
        try:
            os.remove(DATA_FILE)
            st.sidebar.success("تم مسح البيانات بنجاح! ✔️")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"خطأ أثناء حذف الملف: {e}")
    else:
        st.sidebar.info("لا توجد بيانات مسجلة مسبقاً.")

df = load_shipping_data(uploaded_file)
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

page_options = {
    "لوحة التحكم (Dashboard)": "dashboard",
    "حركة المخازن (WMS)": "wms_movement",
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
        st.download_button(
            label="📥 Download as CSV",
            data=data_to_download.to_csv(index=False).encode('utf-8'),
            file_name="filtered_details.csv",
            mime="text/csv"
        )

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

# صفحة لوحة التحكم
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
    
    total_office_paid = filtered_df["المكتب دفع"].sum() if "المكتب دفع" in filtered_df.columns else 0
    total_client_paid = filtered_df["الزبون دفع"].sum() if "الزبون دفع" in filtered_df.columns else 0
    
    row1_c1, row1_c2, row1_c3, row1_c4 = st.columns(4)
    with row1_c1:
        st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">📦 عدد الطلبات / الطرود</div><div class="metric-value">{total_orders:,}</div></div>', unsafe_allow_html=True)
    with row1_c2:
        st.markdown(f'<div class="metric-card" style="background-color: #0f766e;"><div class="metric-title">👥 إجمالي عدد العملاء</div><div class="metric-value">{total_clients:,}</div></div>', unsafe_allow_html=True)
    with row1_c3:
        st.markdown(f'<div class="metric-card" style="background-color: #1d4ed8;"><div class="metric-title">🚢 إجمالي عدد الحاويات</div><div class="metric-value">{total_containers_count:,}</div></div>', unsafe_allow_html=True)
    with row1_c4:
        st.markdown(f'<div class="metric-card" style="background-color: #b45309;"><div class="metric-title">📦 إجمالي عدد الكارتون</div><div class="metric-value">{total_ctns:,.0f}</div></div>', unsafe_allow_html=True)
        
    row2_c1, row2_c2, row2_c3, row2_c4 = st.columns(4)
    with row2_c1:
        st.markdown(f'<div class="metric-card" style="background-color: #047857;"><div class="metric-title">⚖️ إجمالي الوزن (kg)</div><div class="metric-value">{total_weight:,.2f}</div></div>', unsafe_allow_html=True)
    with row2_c2:
        st.markdown(f'<div class="metric-card" style="background-color: #7c2d12;"><div class="metric-title">📐 إجمالي الحجم (m³)</div><div class="metric-value">{total_volume:,.3f}</div></div>', unsafe_allow_html=True)
    with row2_c3:
        st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">💰 مبالغ دفعت من المكتب</div><div class="metric-value">¥{total_office_paid:,.2f}</div></div>', unsafe_allow_html=True)
    with row2_c4:
        st.markdown(f'<div class="metric-card" style="background-color: #9333ea;"><div class="metric-title">👤 مبالغ دفعت من الزبون</div><div class="metric-value">¥{total_client_paid:,.2f}</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    render_download_buttons(filtered_df)
    styled_filtered_df = style_container_column(filtered_df)
    table_height = max(300, min(len(filtered_df) * 35 + 50, 1200))
    st.dataframe(styled_filtered_df, use_container_width=True, height=table_height)

# صفحة حركة المخازن المستقلة (WMS)
elif page == "wms_movement":
    st.title("📦 إدارة حركة المخازن والتقرير اليومي (WMS)")
    st.markdown("---")
    uploaded_wms = st.file_uploader("📁 رفع ملف حركة المخازن اليومي (Excel)", type=["xlsx", "xls"], key="wms_file_uploader")
    
    if st.button("🗑️ مسح بيانات ملف WMS الحالي"):
        if os.path.exists(WMS_FILE):
            try:
                os.remove(WMS_FILE)
                st.success("تم مسح بيانات WMS بنجاح! ✔️")
                st.rerun()
            except Exception as e:
                st.error(f"خطأ أثناء حذف ملف WMS: {e}")
        else:
            st.info("لا توجد بيانات WMS مسجلة مسبقاً.")
            
    wms_df = load_wms_data(uploaded_wms)
    if wms_df is not None and not wms_df.empty:
        st.success("تم تحميل تقرير حركة المخازن وعرضه بنجاح!")
        st.dataframe(wms_df, use_container_width=True)
    else:
        st.info("يرجى رفع ملف حركة المخازن اليومي (Excel) لعرضه هنا.")

# صفحة كشف اجور الكمارك
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
        st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">أجور الجمرك الكلي</div><div class="metric-value">¥{total_customs:,.2f}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card" style="background-color: #0f766e;"><div class="metric-title">متبقي ({sponsor_name})</div><div class="metric-value">¥{sponsor_remaining:,.2f}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">مسدد ({sponsor_name})</div><div class="metric-value">¥{sponsor_collected:,.2f}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card" style="background-color: #b45309;"><div class="metric-title">متبقي (لم تصل بعد)</div><div class="metric-value">¥{not_arrived_remaining:,.2f}</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("### 📋 جدول تفصيلي للشحنات")
    render_download_buttons(pivot_filtered_df)
    styled_pivot_df = style_container_column(pivot_filtered_df)
    customs_table_height = max(300, min(len(pivot_filtered_df) * 35 + 50, 1200))
    st.dataframe(styled_pivot_df, use_container_width=True, height=customs_table_height)

# صفحة الديون على الكفلاء
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
            card_bg = "#1e3a8a" if "لم تصل بعد" in str(sponsor_name) else "#1f2937"
            if "لم تصل بعد" in str(sponsor_name):
                card_bg = "#b45309"
            st.markdown(f'<div class="metric-card" style="background-color: {card_bg}; text-align: right; direction: rtl;"><div class="metric-title" style="font-size: 16px;">👤 الكفيل: {sponsor_name}</div><div style="font-size: 14px; margin-top: 5px;">📦 الطلبات: {s_orders:,} | 💰 الجمرك: ¥{s_customs:,.2f} | ✅ المسدد: ¥{s_collected:,.2f} | ⏳ المتبقي: ¥{s_remaining:,.2f}</div></div>', unsafe_allow_html=True)

# صفحة أعمار الديون
elif page == "aging":
    st.title("⏳ تقرير أعمار الديون (Aging Report)")
    st.markdown("---")
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
            
        formatted_aging = aging_pivot.map(lambda val: f"¥{val:,.0f}" if isinstance(val, (int, float)) and val > 0 else "")
        st.dataframe(formatted_aging, use_container_width=True)
    else:
        st.warning("عذراً، الأعمدة المطلوبة لتقرير أعمار الديون غير متوفرة بالكامل.")

# صفحة كمرك الشحنات والاستحصالات
elif page == "collections":
    st.title("🛃 نافذة كمرك الشحنات والاستحصالات")
    st.markdown("---")
    if not filtered_df.empty:
        total_c = filtered_df["مبلغ الجمرك"].sum() if "مبلغ الجمرك" in filtered_df.columns else 0
        total_coll = filtered_df["قيمة الاستحصالات"].sum() if "قيمة الاستحصالات" in filtered_df.columns else 0
        total_rem = filtered_df["متبقي حقيقي" if "متبقي حقيقي" in filtered_df.columns else filtered_df.columns[0]].sum() if "متبقي حقيقي" in filtered_df.columns else 0
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">إجمالي مبالغ الجمرك</div><div class="metric-value">¥{total_c:,.2f}</div></div>', unsafe_allow_html=True)
        with mc2:
            st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">إجمالي الاستحصالات</div><div class="metric-value">¥{total_coll:,.2f}</div></div>', unsafe_allow_html=True)
        with mc3:
            st.markdown(f'<div class="metric-card" style="background-color: #b45309;"><div class="metric-title">إجمالي المتبقي الحقيقي</div><div class="metric-value">¥{total_rem:,.2f}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        render_download_buttons(filtered_df)
        container_field = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in filtered_df.columns), None)
        if container_field:
            agg_df = filtered_df.groupby(container_field, dropna=False).agg({
                "مبلغ الجمرك": "sum",
                "قيمة الاستحصالات": "sum",
                "متبقي حقيقي": "sum"
            }).reset_index()
            st.dataframe(style_container_column(agg_df), use_container_width=True)

# صفحة الرسوم البيانية
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
