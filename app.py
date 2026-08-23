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

# حقن التنسيقات المخصصة لتقليل مسافات الجدول وجعل السكرول عريضاً
st.markdown("""
<style>
    /* تصغير مسافات وحجم خلايا الجداول لجعلها مضغوطة جداً */
    div[data-testid="stDataFrame"] table {
        font-size: 11px !important;
    }
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        padding: 2px 4px !important;
        line-height: 1.1 !important;
        height: auto !important;
    }
    
    /* تكبير وتوسيع شريط التمرير (Scrollbar) ليكون عريضاً وسهل الإمساك */
    ::-webkit-scrollbar {
        width: 18px !important;  /* عرض السكرول العمودي */
        height: 18px !important; /* عرض السكرول الأفقي */
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
        border-radius: 10px !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #0077b6 !important; /* لون السكرول أزرق متناسق */
        border-radius: 10px !important;
        border: 2px solid #f1f1f1 !important;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #005683 !important;
    }
    
    /* تطبيق السكرول على حاويات الجداول الخاصة بـ Streamlit */
    .stDataFrame div, .element-container div {
        scrollbar-width: thick !important;
        scrollbar-color: #0077b6 #f1f1f1 !important;
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
    # حل مشكلة الـ TypeError بتحويل القيم لنصوص صافية قبل فصلها
    df_cleaned['Main_Code'] = df_cleaned['Shipping_mark'].apply(lambda x: str(x).split('-')[0] if '-' in str(x) else str(x))
    
    # [تم الإصلاح هنا]: تصفية القيم وتحويلها لنصوص لتجنب خطأ الترتيب البرمجي
    raw_unique = df_cleaned['Main_Code'].dropna().unique()
    unique_codes = sorted([str(c).strip() for c in raw_unique if str(c).strip()])
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

# --- 5. نظام التبويبات لعرض الجداول المدمجة والمضغوطة بالأسفل ---
tab1, tab2 = st.tabs(["📊 الجدول المصفى للكود الحالي", "🗂️ ملف الإكسل الكامل والشامل"])

with tab1:
    st.subheader(f"📋 جدول التفاصيل التابع للكود المختار: {selected_code}")
    display_df = df_filtered[['Container', 'Shipping_mark', 'Amount', 'Client_paid', 'Office_paid', 'Ctns', 'Cbm']].copy()
    display_df.columns = ['Container NO.', 'Shipping mark', 'Amount', 'Client paid', 'Office paid', 'Sum of Ctns', 'Sum of Cbm']
    st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("📋 جدول ملف الإكسل الأصلي الكامل (دون تصفية)")
    full_display_df = df_raw.iloc[header_row_idx:].reset_index(drop=True)
    full_display_df.columns = [str(c) for c in full_display_df.iloc[0]]
    full_display_df = full_display_df.iloc[1:].reset_index(drop=True)
    st.dataframe(full_display_df, use_container_width=True, hide_index=True)
