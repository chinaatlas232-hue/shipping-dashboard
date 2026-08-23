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

# [تعديل المحاذاة الديناميكية حسب نوع العمود]: حقن تنسيقات مخصصة لتنظيم العرض والمحاذاة تلقائياً
st.markdown("""
<style>
    /* تنسيق ترويسة الجدول العلوية - ثابتة وعريضة وثخينة */
    div[data-testid="stDataFrame"] th {
        background-color: #f8f9fa !important;
        color: #1a252f !important; 
        font-size: 15px !important;  
        font-weight: 900 !important;   
        text-align: center !important;
        padding: 8px 14px !important; 
        white-space: nowrap !important; 
    }
    
    /* جعل الجدول يأخذ أبعاده الطبيعية الملمومة دون تمدد مفرط */
    div[data-testid="stDataFrame"] table {
        font-size: 13px !important;
        width: auto !important; 
        margin: 0 auto !important; 
        table-layout: auto !important; 
    }
    
    div[data-testid="stDataFrame"] td {
        padding: 6px 14px !important; 
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

# استخراج العناوين الأصلية الـ 29 كاملة وتطبيقها كأعمدة أساسية
df_processed.columns = [str(c).strip() for c in df_processed.iloc[header_row_idx]]
df_data = df_processed.iloc[header_row_idx + 1:].reset_index(drop=True)

# ربط الكلمات المفتاحية فقط لحساب المربعات الإحصائية العلوية الستة دون المساس بحجم الجدول
keywords_map = {
    'Container': ['container no.', 'container', 'الحاوية', 'رقم الحاوية'],
    'Shipping_mark': ['shipping mark', 'رمز الشحن', 'ماركة', 'كود'],
    'Amount': ['amount', 'المجموع', 'القيمة', 'السعر', 'أجور الشحن'],
    'Client_paid': ['client paid', 'الزبون دفع', 'المدفوع', 'دفع'],
    'Office_paid': ['office paid', 'المكتب دفع'],
    'Ctns': ['sum of ctns', 'ctn', 'عدد الكارتون', 'الكراتين'],
    'Cbm': ['sum of cbm', 'cbm', 'الحجم']
}

# حسابات المربعات الملونة معزولة تماماً للحفاظ على حيوية الملف وعرضه الأصلي
for target, keywords in keywords_map.items():
    matched_col = None
    for col in df_data.columns:
        if any(k in str(col).lower() for k in keywords):
            matched_col = col
            break
    if matched_col is not None:
        if target in ['Amount', 'Client_paid', 'Office_paid', 'Ctns', 'Cbm']:
            df_data[f'calc_{target}'] = pd.to_numeric(df_data[matched_col].astype(str).str.replace('¥', '').str.replace('$', '').str.replace(',', '').str.strip(), errors='coerce').fillna(0)
        else:
            df_data[f'calc_{target}'] = df_data[matched_col].fillna("").astype(str).str.strip()
    else:
        df_data[f'calc_{target}'] = 0

# تصفية الأسطر الفارغة من ملفك
df_data = df_data[df_data['calc_Shipping_mark'] != ""].reset_index(drop=True)

if 'calc_Container' in df_data.columns:
    df_data['calc_Container'] = df_data['calc_Container'].astype(str).str.strip().replace('nan', '')

# --- 3. واجهة البحث والتصفية التفاعلية ---
st.title("📊 Logistics Dashboard")

if 'calc_Shipping_mark' in df_data.columns:
    def extract_main_code(val):
        val_str = str(val).strip()
        if '-' in val_str:
            parts = val_str.split('-')
            return str(parts).strip()
        return val_str

    df_data['Main_Code'] = df_data['calc_Shipping_mark'].apply(extract_main_code)
    
    unique_codes_list = []
    for c in df_data['Main_Code'].dropna():
        c_clean = str(c).strip()
        if c_clean and c_clean != "nan" and c_clean not in unique_codes_list:
            unique_codes_list.append(c_clean)
    unique_codes = sorted(unique_codes_list)
else:
    unique_codes = ["B12"]

if not unique_codes:
    unique_codes = ["B12"]

selected_code = st.selectbox("🔍 اختر أو ابحث عن كود الشحن لتتجمع البيانات الخاصة به تلقائياً:", unique_codes)

# تصفية الملف الأصلي والكامل بناءً على الكود المحدد
df_filtered_full = df_data[df_data['Main_Code'] == selected_code].reset_index(drop=True)

# حساب الإحصائيات التجميعية الحقيقية للمربعات الستة
total_orders = df_filtered_full['calc_Shipping_mark'].nunique() if len(df_filtered_full) > 0 else 0
if selected_code.startswith("BS") and total_orders > 1:
    base_codes = df_filtered_full['calc_Shipping_mark'].apply(lambda x: str(x).split('-') if '-' in str(x) else str(x))
    if base_codes.nunique() == 1:
        total_orders = 1

valid_containers = df_filtered_full['calc_Container'][df_filtered_full['calc_Container'] != '']
total_containers = valid_containers.nunique() if len(valid_containers) > 0 else 0
if total_containers == 0 and len(df_filtered_full) > 0:
    total_containers = 1

total_amount = float(df_filtered_full['calc_Amount'].sum())
total_client_paid = float(df_filtered_full['calc_Client_paid'].sum())
total_office_paid = float(df_filtered_full['calc_Office_paid'].sum())
total_cartons = int(df_filtered_full['calc_Ctns'].sum())
total_cbm = float(df_filtered_full['calc_Cbm'].sum())

# --- 4. الشاشات العلوية الست الملونة التفاعلية المرتبة من اليمين لليسار ---
st.markdown(f"""
<style>
    .kpi-container {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 25px; direction: rtl; }}
    .kpi-card {{ flex: 1; min-width: 170px; padding: 18px; border-radius: 10px; color: white; box-shadow: 2px 2px 8px rgba(0,0,0,0.15); text-align: center; }}
    .kpi-title {{ font-size: 13px; font-weight: bold; margin-bottom: 8px; opacity: 0.95; }}
    .kpi-value {{ font-size: 22px; font-weight: bold; }}
</style>
<div class="kpi-container">
    <!-- 1. عدد الطلبات (أزرق) -->
    <div class="kpi-card" style="background-color: #3498DB;">
        <div class="kpi-title">عدد الطلبات</div>
        <div class="kpi-value">{total_orders} طلب</div>
    </div>
    <!-- 2. كود الشحن الحالي (أخضر) -->
    <div class="kpi-card" style="background-color: #2ECC71;">
        <div class="kpi-title">كود الشحن الحالي</div>
        <div class="kpi-value">{selected_code}</div>
    </div>
    <!-- 3. عدد الحاويات (أحمر) -->
    <div class="kpi-card" style="background-color: #E74C3C;">
        <div class="kpi-title">عدد الحاويات</div>
        <div class="kpi-value">{total_containers} حاوية</div>
    </div>
    <!-- 4. Client Paid (فيروزي) -->
    <div class="kpi-card" style="background-color: #1ABC9C;">
        <div class="kpi-title">Client Paid</div>
        <div class="kpi-value">¥ {total_client_paid:,.1f}</div>
    </div>
    <!-- 5. Office Paid (برتقالي) -->
    <div class="kpi-card" style="background-color: #E67E22;">
        <div class="kpi-title">Office Paid</div>
        <div class="kpi-value">¥ {total_office_paid:,.1f}</div>
    </div>
    <!-- 6. إجمالي المبالغ Amount (بنفسجي) -->
    <div class="kpi-card" style="background-color: #9B59B6;">
        <div class="kpi-title">إجمالي المبالغ Amount</div>
        <div class="kpi-value">¥ {total_amount:,.1f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric(label="📦 إجمالي عدد الكراتين المجمعة (Sum of Ctns)", value=f"{total_cartons:,} كارتون")
with col2:
    st.metric(label="📐 إجمالي الحجم الكلي المجمع (Sum of Cbm)", value=f"{total_cbm:,.3f} Cbm")

st.markdown("---")

# --- 5. نظام التبويبات لعرض الجداول بالتنسيق والمحاذاة الديناميكية المخصصة لكل عمود ---
tab1, tab2 = st.tabs(["📊 الجدول المصفى للكود الحالي", "🗂️ ملف الإكسل الكامل والشامل"])

# دالة ذكية لتطبيق تنسيق ومحاذاة الأعمدة (الأرقام لليمين، النصوص في المنتصف)
def apply_dynamic_alignment(st_df, source_df):
    # مصفوفة التنسيق لكل عمود بناءً على نوع البيانات الحقيقي فيه
    column_configs = {}
    for col in source_df.columns:
        # إذا كان العمود يحتوي على قيم رقمية أو مبالغ تبدأ برمز العملة
        sample_val = str(source_df[col].dropna().iloc[0]) if not source_df[col].dropna().empty else ""
        if source_df[col].dtype in ['int64', 'float64'] or any(sym in sample_val for sym in ['¥', '$', '.']):
            column_configs[col] = st.column_config.TextColumn(col, alignment="right") # محاذاة المبالغ لليمين
        else:
            column_configs[col] = st.column_config.TextColumn(col, alignment="center") # محاذاة النصوص للمنتصف
    return column_configs

with tab1:
    st.subheader(f"📋 جدول التفاصيل الكامل والمثبت التابع للكود المختار: {selected_code}")
    display_cols = [c for c in df_filtered_full.columns if not str(c).startswith('calc_') and c != 'Main_Code']
    final_filtered_display = df_filtered_full[display_cols].copy()
    
    # تطبيق التنسيق والمحاذاة الديناميكية حسب العمود تلقائياً
    configs_tab1 = apply_dynamic_alignment(st, final_filtered_display)
    st.dataframe(final_filtered_display, use_container_width=False, hide_index=True, column_config=configs_tab1)

with tab2:
