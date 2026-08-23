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

# حقن تنسيقات مخصصة لتصغير الفراغات وتكبير خط الترويسة وجعلها ثخينة جداً عريضة
st.markdown("""
<style>
    /* إلغاء التمدد الإجمالي العريض وجعل الجدول ملموماً بحجم نصوصه */
    div[data-testid="stDataFrame"] table {
        font-size: 13px !important;
        width: auto !important; 
        margin: 0 auto !important; 
        table-layout: auto !important; 
    }
    
    /* تكبير خط الترويسة العلوية وجعلها ثخينة جداً وعريضة بارزة البنية */
    div[data-testid="stDataFrame"] th {
        background-color: #f8f9fa !important;
        color: #1a252f !important; 
        font-size: 15px !important;  
        font-weight: 900 !important;   
        text-align: center !important;
        padding: 8px 14px !important; 
        white-space: nowrap !important; 
    }
    
    /* تنسيق خلايا البيانات بالأسفل */
    div[data-testid="stDataFrame"] td {
        padding: 6px 14px !important; 
        text-align: center !important;
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
    .kpi-container {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 15px; direction: rtl; }}
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

# [تعديل وضع القيم في مربعات]: تحويل الكراتين والحجم إلى مربعات ملونة متناسقة بالكامل
st.markdown(f"""
<div class="kpi-container">
    <!-- مربع إجمالي عدد الكراتين المجمعة (بني/وردي داكن متناسق) -->
    <div class="kpi-card" style="background-color: #D35400;">
        <div class="kpi-title">📦 إجمالي عدد الكراتين المجمعة (Sum of Ctns)</div>
        <div class="kpi-value">{total_cartons:,} كارتون</div>
    </div>
    <!-- مربع إجمالي الحجم الكلي المجمع (رمادي داكن متناسق) -->
    <div class="kpi-card" style="background-color: #34495E;">
        <div class="kpi-title">📐 إجمالي الحجم الكلي المجمع (Sum of Cbm)</div>
        <div class="kpi-value">{total_cbm:,.3f} Cbm</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# دالة حتمية لتعديل محتوى الخلايا بشكل مباشر دون التسبب في خطأ إخفاء الجداول
def safe_format_date_cell(x):
    x_str = str(x).strip()
    if x_str.isdigit() and len(x_str) >= 10:
        try:
            return pd.to_datetime(int(x_str), unit='ms', errors='coerce').strftime('%Y-%m-%d')
        except:
            return x_str
    try:
        return pd.to_datetime(x, errors='coerce').strftime('%Y-%m-%d')
    except:
        return x_str

def process_dataframe_safely(dataframe):
    configs = {}
    for col in dataframe.columns:
        col_clean = str(col).strip().lower()
        if 'تاريخ' in col_clean or 'date' in col_clean:
            dataframe[col] = dataframe[col].apply(fix_date_cell_wrapper).fillna(dataframe[col].astype(str))
            configs[col] = st.column_config.TextColumn(col, alignment="center")
        else:
            sample = str(dataframe[col].dropna().iloc) if not dataframe[col].dropna().empty else ""
