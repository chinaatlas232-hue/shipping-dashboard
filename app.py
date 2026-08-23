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

# [تعديل عرض الأعمدة والترويسة]: حقن تنسيقات مخصصة لتصغير العرض المفرط وجعل الجدول متناسقاً
st.markdown("""
<style>
    /* تحديد حجم الخلايا والعناوين لتكون متناسقة وغير عريضة بشكل مبالغ فيه */
    div[data-testid="stDataFrame"] table {
        font-size: 13px !important;
        width: auto !important; /* إلغاء التمدد العريض الإجباري */
        margin: 0 auto !important;
    }
    div[data-testid="stDataFrame"] th {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
        font-weight: bold !important;
        text-align: center !important;
        padding: 6px 14px !important;
        max-width: 150px !important; /* تحديد حد أقصى لعرض العمود */
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }
    div[data-testid="stDataFrame"] td {
        padding: 6px 14px !important;
        text-align: center !important;
        max-width: 150px !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }
    
    /* شريط التمرير (السكرول) عريض ومريح للإمساك بالماوس */
    ::-webkit-scrollbar {
        width: 14px !important;  
        height: 14px !important; 
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
        border-radius: 10px !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #0077b6 !important; 
        border-radius: 10px !important;
        border: 2px solid #f1f1f1 !important;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #005683 !important;
    }
</style>
""", unsafe_allow_html=True)

# مسار الملف محلياً داخل المستودع مباشرة
SAVED_FILE_PATH = "permanent_shipping_data.xlsx"

# التحقق من وجود الملف في مجلد المشروع لتشغيل لوحة التحكم فوراً
if os.path.exists(SAVED_FILE_PATH):
    try:
        df_raw = pd.read_excel(SAVED_FILE_PATH, header=None)
    except Exception as e:
        st.error(f"خطأ في قراءة ملف البيانات: {e}")
        st.stop()
else:
    st.title("📦 Logistics Dashboard")
    st.warning("⚠️ لم يتم العثور على ملف permanent_shipping_data.xlsx في المستودع.")
    st.stop()

# --- 2. البحث التلقائي الديناميكي عن سطر العناوين الحقيقي في جدولك ---
df_processed = df_raw.copy()

header_row_idx = 0
for idx, row in df_processed.iterrows():
    row_strings = [str(val).strip().lower() for val in row.dropna()]
    if any("shipping mark" in s or "container no" in s or "amount" in s for s in row_strings):
        header_row_idx = idx
        break

df_processed.columns = [str(c).strip() for c in df_processed.iloc[header_row_idx]]
df_data = df_processed.iloc[header_row_idx + 1:].reset_index(drop=True)

# ربط الأعمدة والمسميات الحسابية تلقائياً لتطابق الجدول المرفوع
keywords_map = {
    'Container': ['container no.', 'container', 'الحاوية', 'رقم الحاوية'],
    'Shipping_mark': ['shipping mark', 'رمز الشحن', 'ماركة', 'كود'],
    'Amount': ['amount', 'المجموع', 'القيمة', 'السعر', 'أجور الشحن'],
    'Client_paid': ['client paid', 'الزبون دفع', 'المدفوع', 'دفع'],
    'Office_paid': ['office paid', 'المكتب دفع'],
    'Ctns': ['sum of ctns', 'ctn', 'عدد الكارتون', 'الكراتين'],
    'Cbm': ['sum of cbm', 'cbm', 'الحجم']
}

final_columns = {}
for target, keywords in keywords_map.items():
    matched_col = None
    for col in df_data.columns:
        if any(k in str(col).lower() for k in keywords):
            matched_col = col
            break
            
    if matched_col is not None:
        series_data = df_data[matched_col]
        if isinstance(series_data, pd.DataFrame):
            series_data = series_data.iloc[:, 0]
            
        if target in ['Amount', 'Client_paid', 'Office_paid', 'Ctns', 'Cbm']:
            series_clean = series_data.astype(str).str.replace('¥', '').str.replace('$', '').str.replace(',', '').str.strip()
            final_columns[target] = pd.to_numeric(series_clean, errors='coerce').fillna(0)
        else:
            final_columns[target] = series_data.fillna("").astype(str).str.strip()
    else:
        final_columns[target] = pd.Series(0, index=range(len(df_data)))

df_cleaned = pd.DataFrame(final_columns)
df_cleaned = df_cleaned[df_cleaned['Shipping_mark'] != ""].reset_index(drop=True)

if 'Container' in df_cleaned.columns:
    df_cleaned['Container'] = df_cleaned['Container'].replace('', None).ffill()

# --- 3. واجهة البحث والتصفية التفاعلية علوية الشاشة ---
st.title("📊 Logistics Dashboard")

if 'Shipping_mark' in df_cleaned.columns:
    def extract_main_code(val):
        val_str = str(val).strip()
        if '-' in val_str:
            parts = val_str.split('-')
            return str(parts[0]).strip()
        return val_str

    df_cleaned['Main_Code'] = df_cleaned['Shipping_mark'].apply(extract_main_code)
    
    unique_codes_list = []
    for c in df_cleaned['Main_Code'].dropna():
        c_clean = str(c).strip()
        if c_clean and c_clean != "nan" and c_clean not in unique_codes_list:
            unique_codes_list.append(c_clean)
    unique_codes = sorted(unique_codes_list)
else:
    unique_codes = ["B12"]

if not unique_codes:
    unique_codes = ["B12"]

selected_code = st.selectbox("🔍 اختر أو ابحث عن كود الشحن لتتجمع البيانات الخاصة به تلقائياً:", unique_codes)

# تصفية الجدول بناءً على الكود المحدد
df_filtered = df_cleaned[df_cleaned['Main_Code'] == selected_code].reset_index(drop=True)

# حساب الإحصائيات التجميعية الحقيقية لملفك الحالي
total_orders = len(df_filtered)
total_containers = df_filtered['Container'].nunique() if 'Container' in df_filtered.columns else 0
total_amount = float(df_filtered['Amount'].sum())
total_client_paid = float(df_filtered['Client_paid'].sum())
total_office_paid = float(df_filtered['Office_paid'].sum())
total_cartons = int(df_filtered['Ctns'].sum())
total_cbm = float(df_filtered['Cbm'].sum())

# --- 4. الشاشات العلوية الست الملونة التفاعلية ---
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
        <div class="kpi-value">¥ {total_amount:,.1f}</div>
    </div>
    <div class="kpi-card" style="background-color: #1ABC9C;">
        <div class="kpi-title">Client Paid</div>
        <div class="kpi-value">¥ {total_client_paid:,.1f}</div>
    </div>
    <div class="kpi-card" style="background-color: #E67E22;">
        <div class="kpi-title">Office Paid</div>
        <div class="kpi-value">¥ {total_office_paid:,.1f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="📦 إجمالي عدد الكراتين المجمعة (Sum of Ctns)", value=f"{total_cartons:,} كارتون")
with col2:
    st.metric(label="📐 إجمالي الحجم الكلي المجمع (Sum of Cbm)", value=f"{total_cbm:,.3f} Cbm")

st.markdown("---")

# --- 5. نظام التبويبات لعرض الجداول بالأبعاد المناسبة والمنسقة ---
tab1, tab2 = st.tabs(["📊 الجدول المصفى للكود الحالي", "🗂️ ملف الإكسل الكامل والشامل"])

with tab1:
    st.subheader(f"📋 جدول التفاصيل التابع للكود المختار: {selected_code}")
    display_df = df_filtered[['Container', 'Shipping_mark', 'Amount', 'Client_paid', 'Office_paid', 'Ctns', 'Cbm']].copy()
    
    # مسميات الترويسة باللغة العربية ومكتملة تماماً وعرضها ذكي ومناسب
    display_df.columns = ['رقم الحاوية', 'كود الشحن', 'المجموع (Amount)', 'الزبون دفع', 'المكتب دفع', 'مجموع الكراتين', 'مجموع الحجم']
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("📋 جدول ملف الإكسل الأصلي الكامل (دون تصفية)")
    full_display_df = df_raw.iloc[header_row_idx:].reset_index(drop=True)
    
    raw_headers = [str(c).strip() for c in full_display_df.iloc]
    clean_headers = []
    for i, h in enumerate(raw_headers):
        if h == "" or h == "nan":
            clean_headers.append(f"فارغ_{i}")
        else:
            clean_headers.append(h)
            
    full_display_df.columns = clean_headers
    full_display_df = full_display_df.iloc[1:].reset_index(drop=True)
    st.dataframe(full_display_df, use_container_width=True, hide_index=True)
