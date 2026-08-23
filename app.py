import streamlit as st
import pandas as pd
import io
import os

# 1. إعدادات الصفحة لتكون عريضة ومتوافقة مع التصميم الموضح بالصورة
st.set_page_config(
    page_title="Shipments Intelligence Dashboard", 
    page_icon="📦", 
    layout="wide"
)

# مسار حفظ الملف الثابت على الخادم لضمان عدم ضياع البيانات
SAVED_FILE_PATH = "permanent_shipping_data.xlsx"

# --- 2. تصميم الشريط الجانبي لإدارة الملفات والتصفير ---
st.sidebar.subheader("📁 إدارة ملفات الشحنات")

# زر المسح البرمجي والتصفير الشامل عند الحاجة
if os.path.exists(SAVED_FILE_PATH):
    if st.sidebar.button("🗑️ مسح وتصفير البيانات المخزنة", type="primary"):
        try:
            os.remove(SAVED_FILE_PATH)
            if "df_raw" in st.session_state:
                del st.session_state["df_raw"]
            st.sidebar.success("تم مسح البيانات وتصفير النظام بنجاح! 🔄")
            st.rerun()                 
        except Exception as e:
            st.sidebar.error(f"تعذر المسح: {e}")
    st.sidebar.markdown("---")

# أداة رفع ملف العميل لتحديث البيانات وتثبيتها دائمًا
uploaded_file = st.sidebar.file_uploader("رفع ملف اكسل جديد لتثبيته في النظام", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.getvalue()
        # حفظ الملف دائمًا على السيرفر
        with open(SAVED_FILE_PATH, "wb") as f:
            f.write(file_bytes)
        
        # قراءة وتخزين البيانات الخام
        df_fresh = pd.read_excel(io.BytesIO(file_bytes))
        st.session_state["df_raw"] = df_fresh
        st.sidebar.success("تم تثبيت وحفظ البيانات بنجاح! 🚀")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"خطأ أثناء معالجة الملف: {e}")

# قراءة الملف المحفوظ تلقائياً عند فتح الصفحة مجدداً في أي وقت
if "df_raw" not in st.session_state and os.path.exists(SAVED_FILE_PATH):
    try:
        st.session_state["df_raw"] = pd.read_excel(SAVED_FILE_PATH)
    except:
        pass

df_raw = st.session_state.get("df_raw", None)

# الحالة عندما يكون النظام مصفراً أو في أول تشغيل
if df_raw is None or df_raw.empty:
    st.title("📦 Shipments Intelligence Dashboard")
    st.warning("⚠️ النظام فارغ ومصفّر حالياً. يرجى رفع ملف إكسل من الشريط الجانبي لتشغيل اللوحة.")
    st.stop()

# --- 3. معالجة وتوحيد مسميات الأعمدة الحسابية بدقة لتعمل الحسابات تلقائياً ---
# الكود يبحث عن الأعمدة لتتناسب مع حسابات المربعات الملونة بالصورة
df = df_raw.copy()
rename_dict = {}
for col in df.columns:
    col_clean = str(col).strip().lower()
    if 'weight' in col_clean or 'الوزن' in col_clean:
        rename_dict[col] = 'WEIGHT'
    elif 'ctn' in col_clean or 'كارتون' in col_clean:
        rename_dict[col] = 'CTN'
    elif 'price' in col_clean or 'سعر' in col_clean or 'المبيعات' in col_clean or 'المجموع' in col_clean:
        rename_dict[col] = 'Price'
    elif 'collected' in col_clean or 'الاستحصال' in col_clean or 'دفع' in col_clean:
        rename_dict[col] = 'Collected'
    elif 'remaining' in col_clean or 'المتبقي' in col_clean or 'متبقي' in col_clean:
        rename_dict[col] = 'Remaining'
    elif 'code' in col_clean or 'الكود' in col_clean:
        rename_dict[col] = 'code'
    elif 'no' in col_clean or 'الشحنة' in col_clean:
        rename_dict[col] = 'No.'

df.rename(columns=rename_dict, inplace=True)

# التأكد من وجود الأعمدة الأساسية بحسابات افتراضية إذا لم تتوفر في الملف المرفوع تفادياً للأعطال
for required_col in ['WEIGHT', 'CTN', 'Price', 'Collected', 'Remaining', 'code', 'No.']:
    if required_col not in df.columns:
        df[required_col] = 0

# تحويل القيم إلى أرقام لإجراء العمليات الرياضية بشكل سليم
df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
df['Collected'] = pd.to_numeric(df['Collected'], errors='coerce').fillna(0)
df['Remaining'] = pd.to_numeric(df['Remaining'], errors='coerce').fillna(0)
df['WEIGHT'] = pd.to_numeric(df['WEIGHT'], errors='coerce').fillna(0)
df['CTN'] = pd.to_numeric(df['CTN'], errors='coerce').fillna(0)

# --- 4. حساب القيم الخاصة بالمربعات الملونة الستة (KPI Cards) ---
total_sales = df['Price'].sum()
total_collected = df['Collected'].sum()
total_remaining = df['Remaining'].sum()
total_weight = df['WEIGHT'].sum()
total_cartons = int(df['CTN'].sum())
total_skus = df['code'].nunique()

collection_rate = (total_collected / total_sales * 100) if total_sales > 0 else 0.0
avg_weight = (total_weight / len(df)) if len(df) > 0 else 0.0
total_items_count = len(df)

# --- 5. تصميم واجهة اللوحة الرئيسية وعلامات التبويب والألوان المستقرة ---
st.title("📦 Shipments Intelligence Dashboard")
st.markdown("<p style='color:#666;'>dynamic charts, summaries & live filters (Streamlit + Plotly) — لوحة تحكم الشحنات الذكية</p>", unsafe_import_html=True)

# ستايل مخصص لمحاكاة نفس البطاقات الملونة الستة الموجودة في صورتك تماماً
st.markdown(f"""
<style>
    .kpi-container {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 25px; }}
    .kpi-card {{ flex: 1; min-width: 180px; padding: 20px; border-radius: 12px; color: white; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }}
    .kpi-title {{ font-size: 13px; font-weight: bold; margin-bottom: 8px; opacity: 0.9; }}
    .kpi-value {{ font-size: 24px; font-weight: bold; margin-bottom: 5px; }}
    .kpi-sub {{ font-size: 11px; opacity: 0.8; }}
</style>
<div class="kpi-container">
    <div class="kpi-card" style="background-color: #6C5CE7;">
        <div class="kpi-title">سعر المبيعات — Total Sales</div>
        <div class="kpi-value">{total_sales:,.1f}</div>
        <div class="kpi-sub">{total_items_count} line items</div>
    </div>
    <div class="kpi-card" style="background-color: #00B894;">
        <div class="kpi-title">الاستحصالات — Collected</div>
        <div class="kpi-value">{total_collected:,.1f}</div>
        <div class="kpi-sub">Collection rate {collection_rate:.0f}%</div>
    </div>
    <div class="kpi-card" style="background-color: #FF7675;">
        <div class="kpi-title">المتبقي — Remaining</div>
        <div class="kpi-value">{total_remaining:,.1f}</div>
        <div class="kpi-sub">Outstanding balance</div>
    </div>
    <div class="kpi-card" style="background-color: #0984E3;">
        <div class="kpi-title">الوزن — Total Weight</div>
        <div class="kpi-value">{total_weight:,.1f} kg</div>
        <div class="kpi-sub">Avg {avg_weight:.1f} kg/item</div>
    </div>
    <div class="kpi-card" style="background-color: #E67E22;">
        <div class="kpi-title">Cartons — CTN</div>
        <div class="kpi-value">{total_cartons}</div>
        <div class="kpi-sub">{total_items_count} shipments</div>
    </div>
    <div class="kpi-card" style="background-color: #A29BFE;">
        <div class="kpi-title">الأكواد — SKUs</div>
        <div class="kpi-value">{total_skus}</div>
        <div class="kpi-sub">0 rows filtered out</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. نظام علامات التبويب (Tabs) كما يظهر بالصورة تماماً ---
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Deep Analysis", "🗂️ Data & Columns"])

with tab1:
    st.subheader("Filtered records")
    # عرض الجدول المنسق والمطابق للأعمدة المطلوبة بالصورة
    display_df = df[['No.', 'code', 'WEIGHT', 'CTN', 'Price', 'Collected', 'Remaining']]
    # إعادة تسمية الأعمدة المعروضة لتطابق صورتك تماماً باللغتين العربية والإنجليزية
    display_df.columns = ['الشحنة', 'الكود', 'WEIGHT', 'CTN', 'Price', 'سعر المبيعات', 'الاستحصالات', 'المتبقي']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # زر مدمج لتحميل البيانات كـ CSV أسفل الجدول مباشرة
    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download filtered data as CSV",
        data=csv_data,
        file_name="filtered_shipments.csv",
        mime="text/csv"
    )

with tab2:
    st.subheader("تحليلات معمقة إضافية")
    st.info("هذه الصفحة مخصصة لعرض الإحصاءات الإضافية والرسوم البيانية المتقدمة.")

with tab3:
    st.subheader("جميع بيانات وأعمدة الملف المرفوع")
    st.dataframe(df_raw, use_container_width=True)
