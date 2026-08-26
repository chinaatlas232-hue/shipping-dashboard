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
[data-testid="stSidebar"] [data-testid="stSelectbox"] * {
    color: #000000 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"],
[data-testid="stSidebar"] [data-testid="stButton"],
[data-testid="stSidebar"] [data-testid="stSelectbox"] {
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
</style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = "shipping_data.xlsx"
WMS_FILE = "wms_daily_data.xlsx"

def clean_numeric(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.strip(),
        errors="coerce"
    ).fillna(0)

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

df.columns = df.columns.astype(str).str.strip()

# البحث الشامل والذكي عن أعمدة الدفع بغض النظر عن المسافات أو التسمية
office_col_candidate = next((c for c in df.columns if any(k in c for k in ["المكتب دفع", "Office Paid", "مكتب", "Office"])), None)
client_col_candidate = next((c for c in df.columns if any(k in c for k in ["الزبون دفع", "Client Paid", "الزبون", "Client"])), None)

if office_col_candidate:
    df["Office Paid"] = clean_numeric(df[office_col_candidate])
else:
    df["Office Paid"] = 0

if client_col_candidate:
    df["Client Paid"] = clean_numeric(df[client_col_candidate])
else:
    df["Client Paid"] = 0

numeric_cols = ["عدد الكارتون", "الوزن", "حجم", "المجموع", "مبلغ الجمرك", "قيمة الاستحصالات", "عدد الايام"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = clean_numeric(df[col])

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

def style_container_column(df_to_style):
    target_container_col = next((c for c in ["رقم الحاوية", "رقم الحاويات"] if c in df_to_style.columns), None)
    sponsor_col_check = "الكفيل" if "الكفيل" in df_to_style.columns else None
    if not target_container_col:
        return df_to_style.style
        
    def highlight_cells(row):
        styles = [''] * len(row)
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
    styled_filtered_df = style_container_column(filtered_df)
    table_height = max(300, min(len(filtered_df) * 35 + 50, 1200))
    st.dataframe(styled_filtered_df, use_container_width=True, height=table_height)
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

# صفحة حركة المخازن (WMS)
elif page == "wms_movement":
    st.title("📦 إدارة حركة المخازن والتقرير اليومي (WMS)")
    st.markdown("---")
    st.write("قم برفع ملف الحسابات أو التقرير اليومي الخاص بحركة المخازن (WMS).")

    daily_file = st.file_uploader("رفع ملف حركة المخازن اليومي (Excel)", type=["xlsx", "xls"], key="wms_uploader")
    wms_df = load_data(daily_file, WMS_FILE)

    if wms_df is not None and not wms_df.empty:
        st.success("تم تحميل وتحليل تقرير حركة المخازن بنجاح!")
        wms_df.columns = wms_df.columns.astype(str).str.strip()

        status_col = next((c for c in wms_df.columns if any(k in c for k in ["حالة الطلب", "Status", "الحالة"])), None)

        if status_col:
            total_wms = len(wms_df)
            shipped_val = len(wms_df[wms_df[status_col].astype(str).str.contains("شحن|تم الشحن", case=False, na=False)])
            on_the_way_val = len(wms_df[wms_df[status_col].astype(str).str.contains("طريق|بالطريق", case=False, na=False)])
            plan_val = len(wms_df[wms_df[status_col].astype(str).str.contains("خطة", case=False, na=False)])
            not_entered_val = len(wms_df[wms_df[status_col].astype(str).str.contains("لم تدخل|لم تصل", case=False, na=False)])

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("إجمالي الطلبات", total_wms)
            c2.metric("تم الشحن 🚢", shipped_val)
            c3.metric("بالطريق 🛣️", on_the_way_val)
            c4.metric("خطة شحن 📋", plan_val)
            c5.metric("لم تدخل المخزن بعد ⏳", not_entered_val)

            st.markdown("---")
            selected_wms_status = st.selectbox("تصفية حسب الحالة:", ["الكل"] + list(wms_df[status_col].unique()))
            if selected_wms_status != "الكل":
                filtered_wms = wms_df[wms_df[status_col] == selected_wms_status]
            else:
                filtered_wms = wms_df

            st.dataframe(filtered_wms, use_container_width=True)
            render_download_buttons(filtered_wms)
        else:
            st.warning("لم يتم العثور على عمود يمثل (حالة الطلب) تلقائياً في الملف المرفق.")
            st.dataframe(wms_df)
    else:
        st.info("يرجى رفع ملف حركة المخازن اليومي من الزر أعلاه لعرض المؤشرات وتحليل البيانات.")

# صفحة كشف أجور الكمارك
elif page == "customs":
    st.title("كشف اجور الكمارك")
    st.markdown("---")
    search_query = st.text_input("بحث ذكي: ابحث برقم الكود، اسم الكفيل، أو رقم الحاوية").strip()
    
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
        st.markdown(f'<div class="metric-card" style="background-color: #16a34a;"><div class="metric-title">إجمالي الاستحصالات المسدد</div><div class="metric-value">${total_collected:,.2f}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card" style="background-color: #dc2626;"><div class="metric-title">متبقي لم تصل بعد</div><div class="metric-value">${not_arrived_remaining:,.2f}</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("### جدول ملخص أجور الكمارك والاستحصالات حسب الكود")
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
            "عدد الكارتون": customs_summary["عدد الكارتون"].sum(),
            "مبلغ الجمرك": customs_summary["مبلغ الجمرك"].sum(),
            "قيمة الاستحصالات": customs_summary["قيمة الاستحصالات"].sum(),
            "متبقي حقيقي": customs_summary["متبقي حقيقي"].sum()
        })
        customs_summary = pd.concat([customs_summary, grand_total_row], ignore_index=True)
        customs_summary = customs_summary.rename(columns={pivot_code_col: "Row Labels"})
        
        formatted_customs = customs_summary.copy()
        for col in ["مبلغ الجمرك", "قيمة الاستحصالات", "متبقي حقيقي"]:
            if col in formatted_customs.columns:
                formatted_customs[col] = formatted_customs[col].apply(lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else x)
                
        def style_customs_table(row):
            if str(row["Row Labels"]) == "Grand Total":
                return ['background-color: #e2e8f0; color: #000000; font-weight: bold;'] * len(row)
            return [''] * len(row)
            
        styled_customs_table = formatted_customs.style.apply(style_customs_table, axis=1)
        render_download_buttons(customs_summary)
        table_height = max(300, min(len(formatted_customs) * 35 + 50, 1200))
        st.dataframe(styled_customs_table, use_container_width=True, height=table_height)
    else:
        st.warning("الأعمدة المطلوبة لإنشاء الجدول غير متوفرة أو البيانات فارغة")
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

# صفحة الديون على الكفلاء
elif page == "sponsors":
    st.title("الديون على الكفلاء")
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
        
        st.markdown("### ملخص المبالغ لكل كفيل")
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
                <h3 style="margin: 0 0 10px 0; font-size: 18px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 5px; color: #ffffff !important;">الكفيل: {sponsor_name}</h3>
                <div style="display: flex; justify-content: space-between; font-size: 15px; text-align: center; color: #ffffff !important;">
                    <div>الطلبات: <b style="color: #ffffff;">{s_orders:,}</b></div>
                    <div>الجمرك: <b style="color: #ffffff;">${s_customs:,.2f}</b></div>
                    <div>المسدد: <b style="color: #ffffff;">${s_collected:,.2f}</b></div>
                    <div>المتبقي: <b style="color: #ffffff;">${s_remaining:,.2f}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("عذراً، عمود الكفيل غير متوفر في البيانات.")
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

# تقرير أعمار الديون
elif page == "aging":
    st.title("تقرير أعمار الديون (Aging Report)")
    st.markdown("---")
    aging_df = filtered_df.copy()
    code_field = next((c for c in ["code", "الكود", "كود"] if c in aging_df.columns), None)
    
    if not aging_df.empty and container_col in aging_df.columns and "عدد الايام" in aging_df.columns and "متبقي حقيقي" in aging_df.columns:
        aging_df["عدد الايام"] = pd.to_numeric(aging_df["عدد الايام"], errors="coerce").fillna(0).astype(int)
        aging_df = aging_df[aging_df["عدد الايام"] > 0]
        
        index_cols = [code_field, container_col] if code_field else [container_col]
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
            
        formatted_aging = aging_pivot.map(lambda val: f"${val:,.0f}" if isinstance(val, (int, float)) and val > 0 else "")
        render_download_buttons(aging_pivot.reset_index())
        st.dataframe(formatted_aging, use_container_width=True)
    else:
        st.warning("عذراً، الأعمدة الأساسية المطلوبة غير متوفرة بالكامل في البيانات الحالية (مثل عدد الأيام أو المتبقي الحقيقي).")
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

# كمرك الشحنات والاستحصالات
elif page == "collections":
    st.title("نافذة كمرك الشحنات والاستحصالات")
    st.markdown("---")
    if not filtered_df.empty:
        total_c = filtered_df["مبلغ الجمرك"].sum() if "مبلغ الجمرك" in filtered_df.columns else 0
        total_coll = filtered_df["قيمة الاستحصالات"].sum() if "قيمة الاستحصالات" in filtered_df.columns else 0
        total_rem = filtered_df["متبقي حقيقي"].sum() if "متبقي حقيقي" in filtered_df.columns else 0
        
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(f'<div class="metric-card" style="background-color: #1e3a8a;"><div class="metric-title">إجمالي مبالغ الجمرك</div><div class="metric-value">{total_c:,.2f}</div></div>', unsafe_allow_html=True)
        with mc2:
            st.markdown(f'<div class="metric-card" style="background-color: #059669;"><div class="metric-title">إجمالي الاستحصالات</div><div class="metric-value">{total_coll:,.2f}</div></div>', unsafe_allow_html=True)
        with mc3:
            st.markdown(f'<div class="metric-card" style="background-color: #d97706;"><div class="metric-title">إجمالي المتبقي الحقيقي</div><div class="metric-value">{total_rem:,.2f}</div></div>', unsafe_allow_html=True)
            
        st.markdown("---")
        render_download_buttons(filtered_df)
        if container_col:
            agg_df = filtered_df.groupby(container_col, dropna=False).agg({
                "مبلغ الجمرك": "sum",
                "قيمة الاستحصالات": "sum",
                "متبقي حقيقي": "sum"
            }).reset_index()
            st.dataframe(agg_df, use_container_width=True)
    else:
        st.warning("البيانات فارغة.")
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

# الرسوم البيانية
elif page == "charts":
    st.title("لوحة الرسوم البيانية والتحليلات")
    st.markdown("---")
    if filtered_df.empty:
        st.warning("لا توجد بيانات متاحة لعرض الرسوم البيانية")
    else:
        if container_col and "مبلغ الجمرك" in filtered_df.columns:
            st.subheader("مقارنة مبالغ الجمرك والاستحصالات حسب الحاويات")
            chart_data = filtered_df.groupby(container_col)[["مبلغ الجمرك", "قيمة الاستحصالات", "متبقي حقيقي"]].sum()
            st.bar_chart(chart_data)
        st.markdown("---")
        if "الكفيل" in filtered_df.columns and "مبلغ الجمرك" in filtered_df.columns:
            st.subheader("إجمالي مبالغ الجمرك والاستحصالات حسب الكفلاء")
            sponsor_chart_data = filtered_df.groupby("الكفيل")[["مبلغ الجمرك", "قيمة الاستحصالات"]].sum()
            st.bar_chart(sponsor_chart_data)
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)
