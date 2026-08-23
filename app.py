import streamlit as st
import pandas as pd
import io
import os

# إعدادات الصفحة لتكون عريضة ومتوافقة مع التصميم الموضح بالصورة
st.set_page_config(
    page_title="Shipments Intelligence Dashboard", 
    page_icon="📦", 
    layout="wide"
)

# مسار حفظ الملف الثابت على الخادم لضمان عدم ضياع البيانات
SAVED_FILE_PATH = "permanent_shipping_data.xlsx"

# --- تصميم الشريط الجانبي لإدارة الملفات والتصفير ---
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

# --- معالجة وتوحيد مسميات الأعمدة الحسابية بشكل آمن وتفادي مشكلة التكرار ---
df = df_raw.copy()

# حل مشكلة الأسماء المتكررة عبر إجبار الأعمدة على أخذ مسميات فريدة وسلسلة نصية فردية
df.columns = [str(c).strip() for c in df.columns]

# تحضير الأعمدة الـ 7 المطلوبة للحسابات والعرض بشكل مستقل ومعزول تماماً
final_columns = {}

for target, keywords in {
    'No.': ['no', 'الشحنة', 'تسلسل'],
    'code': ['code', 'الكود', 'كود'],
    'WEIGHT': ['weight', 'الوزن', 'وزن'],
    'CTN': ['ctn', 'كارتون', 'عدد'],
    'Price': ['price', 'سعر', 'المبيعات', 'المجموع', 'القيمة'],
    'Collected': ['collected', 'الاستحصال', 'دفع', 'المدفوع'],
    'Remaining': ['remaining', 'المتبقي', 'متبقي']
}.items():
    
    matched_col = None
    for col in df.columns:
        if any(k in col.lower() for k in keywords):
            matched_col = col
            break
    
    if matched_col is not None:
        series_data = df[matched_col]
        # [الحل المضمون]: هنا قمنا بعزل العمود وإصلاح مشكلة الـ TypeError نهائياً
        if isinstance(series_data, pd.DataFrame):
            series_data = series_data.iloc[:, 0]
            
        if target in ['WEIGHT', 'CTN', 'Price', 'Collected', 'Remaining']:
            final_columns[target] = pd.to_numeric(series_data, errors='coerce').fillna(0)
        else:
            final_columns[target] = series_data.fillna("")
    else:
        final_columns[target] = pd.Series([0] * len(df))

# بناء جدول البيانات النظيف المحمي من الأخطاء والجاهز للحسابات والعرض
df_cleaned = pd.DataFrame(final_columns)

# --- حساب القيم الخاصة بالمربعات الملونة الستة (KPI Cards) ---
total_sales = float(df_cleaned['Price'].sum())
total_collected = float(df_cleaned['Collected'].sum())
total_remaining = float(df_cleaned['Remaining'].sum())
total_weight = float(df_cleaned['WEIGHT'].sum())
total_cartons = int(df_cleaned['CTN'].sum())
total_skus = int(df_cleaned['code'].nunique())

collection_rate = (total_collected / total_sales * 100) if total_sales > 0 else 0.0
avg_weight = (total_weight / len(df_cleaned)) if len(df_cleaned) > 0 else 0.0
total_items_count = len(df_cleaned)

# --- تصميم واجهة اللوحة الرئيسية وعلامات التبويب والألوان المستقرة ---
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

# --- نظام علامات التبويب (Tabs) كما يظهر بالصورة تماماً ---
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔍 Deep Analysis", "🗂️ Data & Columns"])

with tab1:
    st.subheader("Filtered records")
    
    display_df = df_cleaned[['No.', 'code', 'WEIGHT', 'CTN', 'Price', 'Collected', 'Remaining']].copy()
    display_df.columns = ['الشحنة', 'الكود', 'WEIGHT', 'CTN', 'Price', 'سعر المبيعات', 'الاستحصالات', 'المتبقي']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
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
    st.subheader("جميع بيانات وأعمدة الملف المرفوع الأصلي للرجوع إليها")
    st.dataframe(df_raw, use_container_width=True)
