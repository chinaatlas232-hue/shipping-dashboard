import streamlit as st
import pandas as pd
import io
import os

# 1. إعدادات الصفحة لتكون عريضة ومتوافقة مع التصميم الموضح بالصورة
st.set_page_config(
    page_title="Logistics Dashboard", 
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

# أداة رفع ملف العميل الجديد لتثبيته في النظام
uploaded_file = st.sidebar.file_uploader("رفع ملف اكسل الجديد لتثبيته في النظام", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.getvalue()
        # حفظ الملف دائمًا على السيرفر لضمان استقراره
        with open(SAVED_FILE_PATH, "wb") as f:
            f.write(file_bytes)
        
        # قراءة وتخزين البيانات الخام بدون شروط مسبقة تفادياً للمشاكل
        df_fresh = pd.read_excel(io.BytesIO(file_bytes), header=None)
        st.session_state["df_raw"] = df_fresh
        st.sidebar.success("تم تثبيت وحفظ البيانات بنجاح! 🚀")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"خطأ أثناء معالجة الملف: {e}")

# قراءة الملف المحفوظ تلقائياً عند فتح الصفحة مجدداً في أي وقت
if "df_raw" not in st.session_state and os.path.exists(SAVED_FILE_PATH):
    try:
        st.session_state["df_raw"] = pd.read_excel(SAVED_FILE_PATH, header=None)
    except:
        pass

df_raw = st.session_state.get("df_raw", None)

# الحالة عندما يكون النظام مصفراً أو في أول تشغيل
if df_raw is None or df_raw.empty:
    st.title("📦 Logistics Dashboard")
    st.warning("⚠️ النظام فارغ ومصفّر حالياً. يرجى رفع ملف إكسل من الشريط الجانبي لتشغيل اللوحة.")
    st.stop()

# --- 3. [تحديث ذكي]: البحث التلقائي عن سطر العناوين الحقيقي في الملف المرفوع ---
df_processed = df_raw.copy()

# البحث عن السطر الذي يحتوي على ترويسة الجدول الحقيقية
header_row_idx = 0
for idx, row in df_processed.iterrows():
    row_strings = [str(val).strip().lower() for val in row.dropna()]
    if any("shipping mark" in s or "container no" in s or "amount" in s for s in row_strings):
        header_row_idx = idx
        break

# تعيين السطر المكتشف كعنوان حقيقي للأعمدة وقص ما قبله
df_processed.columns = [str(c).strip() for c in df_processed.iloc[header_row_idx]]
df_data = df_processed.iloc[header_row_idx + 1:].reset_index(drop=True)

# قواميس للبحث الذكي عن الكلمات الدلالية في الأعمدة المكتشفة لربط الحسابات
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
        # حل مشكلة الأعمدة المكررة أو المدمجة تفادياً للأخطاء
        if isinstance(series_data, pd.DataFrame):
            series_data = series_data.iloc[:, 0]
            
        if target in ['Amount', 'Client_paid', 'Office_paid', 'Ctns', 'Cbm']:
            # تنظيف وتطهير الرموز المالية ¥ و $ والمسافات ليقبلها الحساب كأرقام حقيقية
            series_clean = series_data.astype(str).str.replace('¥', '').str.replace('$', '').str.replace(',', '').str.strip()
            final_columns[target] = pd.to_numeric(series_clean, errors='coerce').fillna(0)
        else:
            final_columns[target] = series_data.fillna("").astype(str).str.strip()
    else:
        # عمود افتراضي أصفار لحماية الصفحة من التعطل إذا لم يجد الاسم
        final_columns[target] = pd.Series(0, index=range(len(df_data)))

# بناء جدول البيانات النظيف المربوط بالداش بورد
df_cleaned = pd.DataFrame(final_columns)

# إزالة الأسطر الفارغة أو السطور الإجمالية التي قد تظهر في أسفل الملف وتؤثر على الحسابات
df_cleaned = df_cleaned[df_cleaned['Shipping_mark'] != ""].reset_index(drop=True)

# ملء خلايا رقم الحاوية المدمجة تلقائياً لضمان دقة حساب عدد الحاويات عند الفلترة
if 'Container' in df_cleaned.columns:
    df_cleaned['Container'] = df_cleaned['Container'].replace('', None).ffill()

# --- 4. واجهة البحث التفاعلية وعملية التصفية ---
st.title("📊 Logistics Dashboard")

# استخراج الكود الرئيسي الفريد (مثل B12) لتسهيل الفلترة والبحث
if 'Shipping_mark' in df_cleaned.columns:
    df_cleaned['Main_Code'] = df_cleaned['Shipping_mark'].apply(lambda x: str(x).split('-')[0] if '-' in str(x) else str(x))
    unique_codes = sorted([c for c in df_cleaned['Main_Code'].unique() if str(c).strip()])
else:
    unique_codes = []

if not unique_codes:
    unique_codes = ["B12"]

selected_code = st.selectbox("🔍 اختر أو ابحث عن كود الشحن لتتجمع البيانات الخاصة به تلقائياً:", unique_codes)

# تصفية البيانات بناءً على الكود المحدد بالبحث العلوي
df_filtered = df_cleaned[df_cleaned['Main_Code'] == selected_code].reset_index(drop=True)

# حساب الإحصائيات التجميعية الحقيقية للكود المختار
total_orders = len(df_filtered)
total_containers = df_filtered['Container'].nunique() if 'Container' in df_filtered.columns else 0
total_amount = float(df_filtered['Amount'].sum())
total_client_paid = float(df_filtered['Client_paid'].sum())
total_office_paid = float(df_filtered['Office_paid'].sum())
total_cartons = int(df_filtered['Ctns'].sum())
total_cbm = float(df_filtered['Cbm'].sum())

# --- 5. تصميم الشاشات العلوية الملونة التفاعلية المستقرة ---
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

# --- 6. عرض جدول البيانات المصفى بالكامل بالأسفل للمعاينة والتأكد ---
st.subheader(f"📋 جدول التفاصيل التابع للكود المختار: {selected_code}")

display_df = df_filtered[['Container', 'Shipping_mark', 'Amount', 'Client_paid', 'Office_paid', 'Ctns', 'Cbm']].copy()
display_df.columns = ['Container NO.', 'Shipping mark', 'Amount', 'Client paid', 'Office paid', 'Sum of Ctns', 'Sum of Cbm']

st.dataframe(display_df, use_container_width=True, hide_index=True)

# زر تحميل الملف المباشر المصفى كـ Excel لسهولة التصدير
try:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        display_df.to_excel(writer, index=False, sheet_name='Summary_Report')
    processed_excel_data = output.getvalue()
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 تحميل تقرير الكود الحالي (Excel)",
        data=processed_excel_data,
        file_name=f"{selected_code}_logistics_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
except:
    pass
