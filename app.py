import streamlit as st
import pandas as pd
import io
import os

# 1. إعدادات الصفحة لتكون عريضة
st.set_page_config(
    page_title="Logistics Dashboard", 
    page_icon="📦", 
    layout="wide"
)

st.sidebar.subheader("📁 إدارة ملفات الشحنات")

# البحث التلقائي عن أي ملف إكسل مخزن على السيرفر دون التقيد باسم ثابت
all_files = os.listdir(".") if os.path.exists(".") else []
excel_files = [f for f in all_files if f.endswith(('.xlsx', '.xls'))]
SAVED_FILE_PATH = excel_files[0] if excel_files else "data.xlsx"

# --- زر المسح البرمجي والتصفير الشامل ---
if excel_files:
    if st.sidebar.button("🗑️ مسح وتصفير البيانات المخزنة", type="primary"):
        try:
            for f in excel_files:
                os.remove(f)
            if "df_raw" in st.session_state:
                del st.session_state["df_raw"]
            st.sidebar.success("تم مسح البيانات وتصفير النظام بنجاح! 🔄")
            st.rerun()                 
        except Exception as e:
            st.sidebar.error(f"تعذر المسح: {e}")
    st.sidebar.markdown("---")

# --- أداة رفع ملف العميل الجديد ---
uploaded_file = st.sidebar.file_uploader("رفع ملف اكسل الجديد لتثبيته في النظام", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.getvalue()
        # مسح أي ملفات قديمة منعاً للتضارب وحفظ الملف الجديد باسمه الأصلي
        for f in excel_files:
            os.remove(f)
        
        target_path = uploaded_file.name
        with open(target_path, "wb") as f:
            f.write(file_bytes)
        
        df_fresh = pd.read_excel(io.BytesIO(file_bytes))
        st.session_state["df_raw"] = df_fresh
        st.sidebar.success("تم تثبيت وحفظ البيانات بنجاح! 🚀")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"خطأ أثناء معالجة الملف: {e}")

# قراءة الملف المخزن تلقائياً إن وجد
if "df_raw" not in st.session_state and excel_files:
    try:
        st.session_state["df_raw"] = pd.read_excel(excel_files[0])
    except:
        pass

df_raw = st.session_state.get("df_raw", None)

# الحالة عندما يكون النظام مصفراً
if df_raw is None or df_raw.empty:
    st.title("📦 Logistics Dashboard")
    st.warning("⚠️ النظام فارغ ومصفّر حالياً. يرجى رفع ملف إكسل من الشريط الجانبي لتشغيل اللوحة.")
    st.stop()

# --- 2. تنظيف وتجهيز الأعمدة والحسابات ---
df = df_raw.copy()
df.columns = [str(c).strip() for c in df.columns]

keywords_map = {
    'Container': ['container', 'الحاوية', 'رقم الحاوية'],
    'Shipping_mark': ['shipping mark', 'رمز الشحن', 'ماركة', 'code'],
    'Amount': ['amount', 'المجموع', 'القيمة', 'السعر'],
    'Client_paid': ['client paid', 'الزبون دفع', 'المدفوع'],
    'Office_paid': ['office paid', 'المكتب دفع'],
    'Ctns': ['sum of ctns', 'ctn', 'عدد الكارتون', 'الكراتين'],
    'Cbm': ['sum of cbm', 'cbm', 'الحجم']
}

final_columns = {}
for target, keywords in keywords_map.items():
    matched_col = None
    for col in df.columns:
        if any(k in col.lower() for k in keywords):
            matched_col = col
            break
            
    if matched_col is not None:
        series_data = df[matched_col]
        if isinstance(series_data, pd.DataFrame):
            series_data = series_data.iloc[:, 0]
            
        if target in ['Amount', 'Client_paid', 'Office_paid', 'Ctns', 'Cbm']:
            series_clean = series_data.astype(str).str.replace('¥', '').str.replace('$', '').str.replace(',', '').str.strip()
            final_columns[target] = pd.to_numeric(series_clean, errors='coerce').fillna(0)
        else:
            final_columns[target] = series_data.fillna("").astype(str).str.strip()
    else:
        final_columns[target] = pd.Series(0, index=range(len(df)))

df_cleaned = pd.DataFrame(final_columns)

if 'Container' in df_cleaned.columns:
    df_cleaned['Container'] = df_cleaned['Container'].replace('', None).ffill()

# --- 3. واجهة البحث التفاعلية وعملية التصفية ---
st.title("📊 Logistics Dashboard")

if 'Shipping_mark' in df_cleaned.columns:
    df_cleaned['Main_Code'] = df_cleaned['Shipping_mark'].apply(lambda x: x.split('-')[0] if '-' in str(x) else str(x))
    unique_codes = sorted([c for c in df_cleaned['Main_Code'].unique() if str(c).strip()])
else:
    unique_codes = []

if not unique_codes:
    unique_codes = ["B12"]

selected_code = st.selectbox("🔍 اختر أو ابحث عن كود الشحن لتجميع البيانات الخاصة به:", unique_codes)

df_filtered = df_cleaned[df_cleaned['Main_Code'] == selected_code].reset_index(drop=True)

# حاسبة الإحصائيات التجميعية للكود المختار
total_orders = len(df_filtered)
total_containers = df_filtered['Container'].nunique() if 'Container' in df_filtered.columns else 0
total_amount = float(df_filtered['Amount'].sum())
total_client_paid = float(df_filtered['Client_paid'].sum())
total_office_paid = float(df_filtered['Office_paid'].sum())
total_cartons = int(df_filtered['Ctns'].sum())
total_cbm = float(df_filtered['Cbm'].sum())

# --- 4. تصميم الشاشات العلوية الملونة التفاعلية ---
st.markdown(f"""
<style>
    .kpi-container {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 25px; direction: rtl; }}
    .kpi-card {{ flex: 1; min-width: 170px; padding: 18px; border-radius: 10px; color: white; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); text-align: center; }}
    .kpi-title {{ font-size: 13px; font-weight: bold; margin-bottom: 6px; opacity: 0.95; }}
    .kpi-value {{ font-size: 22px; font-weight: bold; }}
</style>
<div class="kpi-container">
    <div class="kpi-card" style="background-color: #2ECC71;">
        <div class="kpi-title">كود الشحن الحالي</div>
        <div class="kpi-value">{selected_code}</div>
    </div>
    <div class="kpi-card" style="background-color: #3498DB;">
        <div class="kpi-title">عدد الطلبات</div>
        <div class="kpi-value">{total_orders} طلب</div>
    </div>
    <div class="kpi-card" style="background-color: #E74C3C;">
        <div class="kpi-title">عدد الحاويات</div>
        <div class="kpi-value">{total_containers} حاوية</div>
    </div>
    <div class="kpi-card" style="background-color: #9B59B6;">
        <div class="kpi-title">إجمالي المبالغ Amount</div>
        <div class="kpi-value">¥ {total_amount:,.0f}</div>
    </div>
    <div class="kpi-card" style="background-color: #1ABC9C;">
        <div class="kpi-title">Client Paid</div>
        <div class="kpi-value">¥ {total_client_paid:,.0f}</div>
    </div>
    <div class="kpi-card" style="background-color: #E67E22;">
        <div class="kpi-title">Office Paid</div>
        <div class="kpi-value">¥ {total_office_paid:,.0f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="📦 إجمالي عدد الكراتين المجمعة (Sum of Ctns)", value=f"{total_cartons:,} كارتون")
with col2:
    st.metric(label="📐 إجمالي الحجم الكلي المجمع (Sum of Cbm)", value=f"{total_cbm:,.3f} Cbm")

st.markdown("---")

# --- 5. عرض جدول البيانات المصفى بالكامل بالأسفل ---
st.subheader(f"📋 جدول التفاصيل التابع للكود المختار: {selected_code}")

available_display_cols = [c for c in ['Container', 'Shipping_mark', 'Amount', 'Client_paid', 'Office_paid', 'Ctns', 'Cbm'] if c in df_filtered.columns]
display_df = df_filtered[available_display_cols].copy()

st.dataframe(display_df, use_container_width=True, hide_index=True)
